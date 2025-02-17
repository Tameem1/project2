# routers/usage_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from middleware import get_current_user
from models.customer import Customer
from models.usage_token import UsageToken

usage_router = APIRouter()

@usage_router.get("/{customer_id}/usage", tags=["Usage"])
def get_customer_usage(
    customer_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1) Verify token's customer_id matches
    token_customer_id = user.get("customer_id")
    if token_customer_id != customer_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # 2) Grab the usage row from usage_tokens
    usage_record = db.query(UsageToken).filter(
        UsageToken.customer_id == customer_id
    ).first()

    # If no usage record, user is new or unsubscribed
    if not usage_record:
        return {
            "plan_name": "N/A",
            "number_of_tokens": 1000,
            "tokens_used": 0,
            "tokens_remaining": 1000,
            "input_tokens_used": 0,
            "output_tokens_used": 0
        }

    # 3) Also fetch the Customer to read plan name
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    plan_name = None
    if db_customer and db_customer.billing_info:
        plan_name = db_customer.billing_info.get("plan_name")

    return {
        "plan_name": plan_name if plan_name else "N/A",
        "number_of_tokens": usage_record.number_of_tokens,
        "tokens_used": usage_record.tokens_used,
        "tokens_remaining": usage_record.tokens_remaining,
        "input_tokens_used": usage_record.input_tokens_used,
        "output_tokens_used": usage_record.output_tokens_used
    }