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

# Example product IDs mapping (if used elsewhere)
PLANS = {
    "prod_Rn3o1Du3ssKMNv": {"name": "Basic", "tokens_allotment": 1_000_000},
    "prod_Rn3oIo22pSBsy3": {"name": "Standard", "tokens_allotment": 2_000_000},
    "prod_Rn3on3cd77DcnO": {"name": "Premium", "tokens_allotment": 3_000_000}
}

@router.get("/api/pricing")
def get_pricing():
    """
    Returns a list of active pricing plans from Stripe filtered to show only
    plans with product names "Basic", "Premium", or "Standard" that are active.
    """
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
    """
    Creates a Stripe Checkout session for a subscription.
    Expects JSON: { "customer_id": "<UUID>", "price_id": "price_XXXX" }
    """
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
    Cancels the active subscription for the authenticated customer.
    Expects JSON: { "customer_id": "<UUID>" }
    The cancellation is set to occur at the end of the billing period.
    """
    customer_id = data.get("customer_id")
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id is required")

    if user.get("customer_id") != customer_id:
        raise HTTPException(status_code=403, detail="Unauthorized to cancel this subscription")

    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    billing_info = db_customer.billing_info or {}
    stripe_customer_id = billing_info.get("stripe_customer_id")
    if not stripe_customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer ID found for cancellation")

    # Retrieve active subscriptions for this customer
    subscriptions = stripe.Subscription.list(customer=stripe_customer_id, status="active")
    if not subscriptions.data:
        raise HTTPException(status_code=400, detail="No active subscription found")

    # For simplicity, cancel the first active subscription found
    sub_id = subscriptions.data[0].id
    try:
        canceled_subscription = stripe.Subscription.modify(sub_id, cancel_at_period_end=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "Subscription cancellation initiated. Your subscription will cancel at the end of your billing period.",
        "subscription": canceled_subscription,
    }


@router.post("/api/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handles Stripe webhook events for subscription updates.
    Updates local Customer and UsageToken records based on subscription events.
    """
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

        billing_info = db_customer.billing_info or {}
        plan_data = PLANS.get(product_id)
        if plan_data:
            billing_info["plan_name"] = plan_data["name"]
            new_token_allotment = plan_data["tokens_allotment"]
        else:
            billing_info["plan_name"] = "Unknown"
            new_token_allotment = 1000

        db_customer.billing_info = billing_info
        db.commit()
        db.refresh(db_customer)

        usage_record = db.query(UsageToken).filter(
            UsageToken.customer_id == db_customer.id
        ).first()

        if not usage_record:
            usage_record = UsageToken(
                customer_id=db_customer.id,
                number_of_tokens=new_token_allotment,
                tokens_used=0,
                tokens_remaining=new_token_allotment
            )
            db.add(usage_record)
            db.commit()
            db.refresh(usage_record)
        else:
            usage_record.number_of_tokens = new_token_allotment
            usage_record.tokens_remaining = usage_record.number_of_tokens - usage_record.tokens_used
            db.commit()

    elif event_type in ["customer.subscription.deleted", "customer.subscription.cancelled"]:
        subscription = event["data"]["object"]
        stripe_customer_id = subscription["customer"]

        db_customer = db.query(Customer).filter(
            Customer.billing_info.op("->>")("stripe_customer_id") == stripe_customer_id
        ).first()

        if db_customer:
            billing_info = db_customer.billing_info or {}
            billing_info["plan_name"] = None
            db_customer.billing_info = billing_info
            db.commit()
            db.refresh(db_customer)

            usage_record = db.query(UsageToken).filter(
                UsageToken.customer_id == db_customer.id
            ).first()
            if usage_record:
                usage_record.number_of_tokens = 1000
                usage_record.tokens_remaining = usage_record.number_of_tokens - usage_record.tokens_used
                db.commit()

    return JSONResponse(content={"received": True})