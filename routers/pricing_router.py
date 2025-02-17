# routers/pricing_router.py
# "prod_Rn3o1Du3ssKMNv":"Basic"
# "prod_Rn3oIo22pSBsy3":"Standard"
# "prod_Rn3on3cd77DcnO":"Premium"

# routers/pricing_router.py

import os
import stripe
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db.session import get_db
from models.customer import Customer
from models.usage_token import UsageToken  # so we can update usage_tokens table

router = APIRouter()

# Pull from env or define directly (not recommended for production)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_XXXX")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_XXXX")
BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")

# Real Stripe product IDs => plan_name & tokens allotment
PLANS = {
    # Example product IDs from Stripe
    "prod_Rn3o1Du3ssKMNv": {
        "name": "Basic",
        "tokens_allotment": 1_000_000
    },
    "prod_Rn3oIo22pSBsy3": {
        "name": "Standard",
        "tokens_allotment": 2_000_000
    },
    "prod_Rn3on3cd77DcnO": {
        "name": "Premium",
        "tokens_allotment": 3_000_000
    }
}


@router.get("/api/pricing")
def get_pricing():
    """
    Returns a list of active pricing plans from Stripe.
    """
    try:
        prices = stripe.Price.list(active=True, limit=10, expand=["data.product"])
        plans = []
        for price in prices.data:
            plans.append({
                "id": price.id,
                "product": price.product,  # product object includes name, etc.
                "unit_amount": price.unit_amount,
                "currency": price.currency,
                "interval": price.recurring.interval,
                "trial_period_days": price.recurring.trial_period_days,
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

    # 1) Lookup your local DB 'Customer'
    db_customer = db.query(Customer).filter(Customer.id == customer_id_str).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    billing_info = db_customer.billing_info or {}
    stripe_customer_id = billing_info.get("stripe_customer_id")

    # 2) If there's no stripe_customer_id stored, create one in Stripe
    if not stripe_customer_id:
        stripe_customer = stripe.Customer.create(
            email=db_customer.contact_email,
            name=db_customer.name,
        )
        stripe_customer_id = stripe_customer.id
        billing_info["stripe_customer_id"] = stripe_customer_id
        db_customer.billing_info = billing_info
        db.commit()

    # 3) Create the Checkout Session
    try:
        session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=f"{BASE_URL}/pricing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{BASE_URL}/pricing/cancel",
            client_reference_id=customer_id_str,
        )
        return {"session_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handles Stripe webhook events for subscription creation/updates.
    We only store plan_name in the customers table, and update usage_tokens
    to reflect the new plan (i.e. set number_of_tokens).
    We do NOT reset tokens_used. We recalc tokens_remaining = number_of_tokens - tokens_used.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        print("[WEBHOOK] Signature verification failed.")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.get("type")
    print(f"[WEBHOOK] Received event type: {event_type}")

    if event_type in ["customer.subscription.created", "customer.subscription.updated"]:
        subscription = event["data"]["object"]  # The subscription object
        stripe_customer_id = subscription["customer"]
        product_id = subscription["items"]["data"][0]["price"]["product"]

        print(f"[WEBHOOK] subscription product_id => {product_id}")
        print(f"[WEBHOOK] subscription for stripe_customer_id => {stripe_customer_id}")

        # Look up local Customer by stripe_customer_id
        db_customer = db.query(Customer).filter(
            Customer.billing_info["stripe_customer_id"].astext == stripe_customer_id
        ).first()

        if not db_customer:
            print("[WEBHOOK] No matching local customer. Aborting update.")
            return {"status": "ignored"}

        billing_info = db_customer.billing_info or {}

        # 1) Figure out the plan from PLANS dict
        plan_data = PLANS.get(product_id)
        if plan_data:
            plan_name = plan_data["name"]
            new_token_allotment = plan_data["tokens_allotment"]
            billing_info["plan_name"] = plan_name
            print(f"[WEBHOOK] Matched plan {plan_name}, allotment {new_token_allotment}")
        else:
            billing_info["plan_name"] = "Unknown"
            new_token_allotment = 1000  # fallback if unknown product
            print("[WEBHOOK] Unknown product_id, setting plan_name to 'Unknown'")

        # 2) Update the 'customers' table with plan name
        db_customer.billing_info = billing_info
        db.commit()
        db.refresh(db_customer)

        # 3) Also update usage_tokens (only number_of_tokens + recalc tokens_remaining)
        usage_record = db.query(UsageToken).filter(
            UsageToken.customer_id == db_customer.id
        ).first()

        if not usage_record:
            # If no usage record, create one with the new plan
            usage_record = UsageToken(
                customer_id=db_customer.id,
                number_of_tokens=new_token_allotment,
                tokens_used=0,  # brand new, so zero used
                tokens_remaining=new_token_allotment,  # all available
            )
            db.add(usage_record)
            db.commit()
            db.refresh(usage_record)
            print("[WEBHOOK] Created new usage record.")
        else:
            # DO NOT reset tokens_used
            # Just update the new plan allotment
            usage_record.number_of_tokens = new_token_allotment
            usage_record.tokens_remaining = usage_record.number_of_tokens - usage_record.tokens_used
            db.commit()
            print("[WEBHOOK] Updated usage record with new plan allotment, tokens_used remains the same.")

    elif event_type in ["customer.subscription.deleted", "customer.subscription.cancelled"]:
        subscription = event["data"]["object"]
        stripe_customer_id = subscription["customer"]

        print("[WEBHOOK] Subscription cancelled/deleted:", stripe_customer_id)

        # find local customer
        db_customer = db.query(Customer).filter(
            Customer.billing_info["stripe_customer_id"].astext == stripe_customer_id
        ).first()

        if db_customer:
            # remove plan_name
            billing_info = db_customer.billing_info or {}
            billing_info["plan_name"] = None
            db_customer.billing_info = billing_info
            db.commit()
            db.refresh(db_customer)

            # Optionally set usage_record.number_of_tokens back to 1000 or 0
            usage_record = db.query(UsageToken).filter(
                UsageToken.customer_id == db_customer.id
            ).first()
            if usage_record:
                # keep tokens_used intact or set to 0? 
                # your choice. Example sets the plan to default 1000 again
                usage_record.number_of_tokens = 1000
                usage_record.tokens_remaining = usage_record.number_of_tokens - usage_record.tokens_used
                db.commit()
                print("[WEBHOOK] Reset usage tokens to default after cancellation.")

    return JSONResponse(content={"received": True})