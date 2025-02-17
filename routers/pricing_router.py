# routers/pricing_router.py
import stripe
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import os
from db.session import get_db
from sqlalchemy.orm import Session
from models.customer import Customer

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")

@router.get("/api/pricing")
def get_pricing():
    """
    Returns a list of active pricing plans.
    """
    try:
        prices = stripe.Price.list(active=True, limit=10, expand=["data.product"])
        plans = []
        for price in prices.data:
            plans.append({
                "id": price.id,
                "product": price.product,  # Contains details such as name, description, etc.
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
    Creates a Stripe Checkout session.
    Expects a JSON body with "customer_id" and "price_id".
    """
    customer_id = data.get("customer_id")
    price_id = data.get("price_id")
    if not customer_id or not price_id:
        raise HTTPException(status_code=400, detail="customer_id and price_id are required")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=f"{BASE_URL}/pricing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{BASE_URL}/pricing/cancel",
            client_reference_id=customer_id,
        )
        return {"session_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handles incoming Stripe webhook events (e.g. subscription updates).
    Make sure to set STRIPE_WEBHOOK_SECRET in your environment.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Process subscription events to update customer token allotment.
    if event["type"] in ["customer.subscription.updated", "customer.subscription.created"]:
        subscription = event["data"]["object"]
        customer_stripe_id = subscription["customer"]
        product_id = subscription["items"]["data"][0]["price"]["product"]
        customer = db.query(Customer).filter(
            Customer.billing_info["stripe_customer_id"].astext == customer_stripe_id
        ).first()
        if customer:
            # Example mapping—replace these product IDs with your actual ones:
            if product_id == "prod_BASIC_ID":
                customer.usage_tokens = 1000000
            elif product_id == "prod_STANDARD_ID":
                customer.usage_tokens = 2000000
            elif product_id == "prod_PREMIUM_ID":
                customer.usage_tokens = 3000000
            db.commit()
    elif event["type"] in ["customer.subscription.deleted", "customer.subscription.cancelled"]:
        subscription = event["data"]["object"]
        customer_stripe_id = subscription["customer"]
        customer = db.query(Customer).filter(
            Customer.billing_info["stripe_customer_id"].astext == customer_stripe_id
        ).first()
        if customer:
            customer.usage_tokens = 0
            db.commit()
    return JSONResponse(content={"received": True})

# -------------------------------
# New endpoint: Setup test pricing plans
# -------------------------------
@router.post("/api/pricing/setup")
def setup_pricing_plans():
    """
    Creates three test pricing plans in Stripe:
      - Basic: $9.99/month with 1,000,000 tokens
      - Standard: $19.99/month with 2,000,000 tokens
      - Premium: $29.99/month with 3,000,000 tokens
      
    This endpoint is for testing purposes only.
    """
    try:
        plans = []

        # Basic plan
        basic_product = stripe.Product.create(
            name="Basic", 
            description="Basic plan with 1,000,000 tokens per month"
        )
        basic_price = stripe.Price.create(
            product=basic_product.id,
            unit_amount=999,  # $9.99 in cents
            currency="usd",
            recurring={"interval": "month", "trial_period_days": 7}
        )
        plans.append({
            "id": basic_price.id,
            "product": {"name": basic_product.name, "description": basic_product.description},
            "unit_amount": basic_price.unit_amount,
            "currency": basic_price.currency,
            "interval": basic_price.recurring.interval,
            "trial_period_days": basic_price.recurring.trial_period_days,
            "token_allotment": 1000000
        })

        # Standard plan
        standard_product = stripe.Product.create(
            name="Standard", 
            description="Standard plan with 2,000,000 tokens per month"
        )
        standard_price = stripe.Price.create(
            product=standard_product.id,
            unit_amount=1999,  # $19.99 in cents
            currency="usd",
            recurring={"interval": "month", "trial_period_days": 7}
        )
        plans.append({
            "id": standard_price.id,
            "product": {"name": standard_product.name, "description": standard_product.description},
            "unit_amount": standard_price.unit_amount,
            "currency": standard_price.currency,
            "interval": standard_price.recurring.interval,
            "trial_period_days": standard_price.recurring.trial_period_days,
            "token_allotment": 2000000
        })

        # Premium plan
        premium_product = stripe.Product.create(
            name="Premium", 
            description="Premium plan with 3,000,000 tokens per month"
        )
        premium_price = stripe.Price.create(
            product=premium_product.id,
            unit_amount=2999,  # $29.99 in cents
            currency="usd",
            recurring={"interval": "month", "trial_period_days": 7}
        )
        plans.append({
            "id": premium_price.id,
            "product": {"name": premium_product.name, "description": premium_product.description},
            "unit_amount": premium_price.unit_amount,
            "currency": premium_price.currency,
            "interval": premium_price.recurring.interval,
            "trial_period_days": premium_price.recurring.trial_period_days,
            "token_allotment": 3000000
        })

        return {"plans": plans}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))