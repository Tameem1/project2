# routers/pricing_router.py

import os
import stripe
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db.session import get_db
from models.customer import Customer
from models.usage_token import UsageToken
from middleware import get_current_user

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_XXXX")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_XXXX")
BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")

PLANS = {
    "prod_Rn3o1Du3ssKMNv": {"name": "Basic", "tokens_allotment": 1_000_000},
    "prod_Rn3oIo22pSBsy3": {"name": "Standard", "tokens_allotment": 2_000_000},
    "prod_Rn3on3cd77DcnO": {"name": "Premium", "tokens_allotment": 3_000_000}
}

@router.get("/api/pricing")
def get_pricing():
    try:
        prices = stripe.Price.list(active=True, limit=10, expand=["data.product"])
        valid_product_names = {"Basic", "Premium", "Standard"}
        plans = []
        for price in prices.data:
            product = price.product
            if isinstance(product, dict):
                if product.get("name") in valid_product_names and product.get("active") is True:
                    plans.append({
                        "id": price.id,
                        "product": product,
                        "unit_amount": price.unit_amount,
                        "currency": price.currency,
                        "interval": price.recurring.get("interval") if price.recurring else None,
                        "trial_period_days": price.recurring.get("trial_period_days") if price.recurring else None,
                    })
        return {"plans": plans}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/pricing/checkout")
def create_checkout_session(data: dict, db: Session = Depends(get_db)):
    customer_id_str = data.get("customer_id")
    price_id = data.get("price_id")

    if not customer_id_str or not price_id:
        raise HTTPException(status_code=400, detail="customer_id and price_id are required")

    db_customer = db.query(Customer).filter(Customer.id == customer_id_str).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    billing_info = db_customer.billing_info or {}
    stripe_customer_id = billing_info.get("stripe_customer_id")

    if not stripe_customer_id:
        stripe_customer = stripe.Customer.create(
            email=db_customer.contact_email,
            name=db_customer.name,
        )
        stripe_customer_id = stripe_customer.id
        billing_info["stripe_customer_id"] = stripe_customer_id
        db_customer.billing_info = billing_info
        db.commit()

    try:
        session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{BASE_URL}/pricing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{BASE_URL}/pricing/cancel",
            client_reference_id=customer_id_str,
        )
        return {"session_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/pricing/cancel", tags=["Pricing"])
def cancel_subscription(
    data: dict,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancels the active subscription in Stripe at the end of the billing period.
    Expects JSON: { "customer_id": "<UUID>" }
    """
    customer_id = data.get("customer_id")
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id is required")

    if user.get("customer_id") != customer_id:
        raise HTTPException(status_code=403, detail="Unauthorized to cancel this subscription")

    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    billing_info = dict(db_customer.billing_info) if db_customer.billing_info else {}
    stripe_customer_id = billing_info.get("stripe_customer_id")
    if not stripe_customer_id:
        raise HTTPException(status_code=404, detail="No associated Stripe customer found")

    subscription_id = billing_info.get("subscription_id")
    if not subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription_id found. Are you subscribed?")

    try:
        # Use 'modify' instead of 'update' to avoid the TypeError
        # This sets cancel_at_period_end=True in Stripe
        stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

    # We do NOT remove plan_name or usage yet, user retains access until the subscription is fully canceled
    return {
        "message": (
            "Your subscription has been set to cancel at the end of the current billing period. "
            "You still have full access until then."
        )
    }


@router.post("/api/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.get("type")

    if event_type in ["customer.subscription.created", "customer.subscription.updated"]:
        subscription = event["data"]["object"]
        stripe_customer_id = subscription["customer"]
        product_id = subscription["items"]["data"][0]["price"]["product"]

        db_customer = db.query(Customer).filter(
            Customer.billing_info.op("->>")("stripe_customer_id") == stripe_customer_id
        ).first()

        if not db_customer:
            return {"status": "ignored"}

        billing_info = dict(db_customer.billing_info) if db_customer.billing_info else {}
        subscription_id = subscription["id"]

        plan_data = PLANS.get(product_id)
        if plan_data:
            billing_info["plan_name"] = plan_data["name"]
            new_token_allotment = plan_data["tokens_allotment"]
        else:
            billing_info["plan_name"] = "Unknown"
            new_token_allotment = 1000

        # Save subscription_id so we can cancel later
        billing_info["subscription_id"] = subscription_id

        db_usage = db.query(UsageToken).filter(
            UsageToken.customer_id == db_customer.id
        ).first()

        if not db_usage:
            db_usage = UsageToken(
                customer_id=db_customer.id,
                number_of_tokens=new_token_allotment,
                tokens_used=0,
                tokens_remaining=new_token_allotment
            )
            db.add(db_usage)
        else:
            db_usage.number_of_tokens = new_token_allotment
            db_usage.tokens_remaining = db_usage.number_of_tokens - db_usage.tokens_used

        db_customer.billing_info = billing_info
        db.commit()

    elif event_type in ["customer.subscription.deleted", "customer.subscription.cancelled"]:
        subscription = event["data"]["object"]
        stripe_customer_id = subscription["customer"]

        db_customer = db.query(Customer).filter(
            Customer.billing_info.op("->>")("stripe_customer_id") == stripe_customer_id
        ).first()

        if db_customer:
            billing_info = dict(db_customer.billing_info) if db_customer.billing_info else {}
            billing_info["plan_name"] = None
            billing_info["subscription_id"] = None
            db_customer.billing_info = billing_info
            db.commit()

            usage_record = db.query(UsageToken).filter(
                UsageToken.customer_id == db_customer.id
            ).first()
            if usage_record:
                usage_record.number_of_tokens = 1000
                usage_record.tokens_remaining = usage_record.number_of_tokens - usage_record.tokens_used
                db.commit()

    return JSONResponse(content={"received": True})

@router.get("/api/pricing/verify_subscription")
def verify_subscription(session_id: str, db: Session = Depends(get_db)):
    """
    Checks if our backend recognizes the subscription associated with a given Checkout Session ID.
    
    1. We retrieve the Checkout Session from Stripe using 'stripe.checkout.Session.retrieve(session_id)'.
    2. Extract 'customer' (stripe_customer_id) and optional 'subscription' from the session.
    3. Lookup that Stripe customer in our database by comparing billing_info->>'stripe_customer_id'.
    4. If we find the customer, check if plan_name is set (or any other logic to confirm the subscription).
    5. Return subscriptionFound: True/False.
    """
    try:
        # 1) Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        stripe_customer_id = session.get("customer")       # e.g. "cus_abc123"
        subscription_id = session.get("subscription")      # e.g. "sub_xyz789"

        if not stripe_customer_id:
            return {"subscriptionFound": False, "reason": "No stripe_customer_id in session"}

        # 2) Look up the local Customer that has that stripe_customer_id
        db_customer = db.query(Customer).filter(
            Customer.billing_info.op("->>")("stripe_customer_id") == stripe_customer_id
        ).first()

        if not db_customer:
            return {"subscriptionFound": False, "reason": "Customer not found in DB"}

        # 3) Check if plan_name is set or usage token is updated, etc.
        billing_info = db_customer.billing_info or {}
        plan_name = billing_info.get("plan_name")

        if plan_name:
            # The plan_name indicates our webhook recognized and updated the subscription
            return {"subscriptionFound": True}
        else:
            # The subscription wasn't updated (webhook missed or not processed yet)
            return {"subscriptionFound": False, "reason": "plan_name not set"}
    except Exception as e:
        print("Error verifying subscription:", e)
        # On any failure, just return false so the frontend can show fallback
        return {"subscriptionFound": False, "reason": str(e)}