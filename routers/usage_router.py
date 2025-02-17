# routers/usage_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from services.usage_service import get_usage
from middleware import get_current_user
from db.session import get_db
from models.customer import Customer

usage_router = APIRouter()

@usage_router.get("/{customer_id}/usage", tags=["Usage"])
def get_customer_usage(
    customer_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Ensure token's customer_id matches the route
    token_customer_id = user.get("customer_id")
    if token_customer_id != customer_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this customer data")
    
    # 1) Get usage object
    usage = get_usage(db, customer_id)
    
    # 2) Also fetch the Customer to read billing_info
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    plan_name = None
    if customer and customer.billing_info:
        plan_name = customer.billing_info.get("plan_name", None)

    # Return usage + plan_name
    return {
        "tokens_used_total": usage.tokens_used,
        "tokens_used_input": usage.input_tokens_used,
        "tokens_used_output": usage.output_tokens_used,
        "tokens_remaining": usage.tokens_remaining,
        "last_updated": usage.last_updated,
        "plan_name": plan_name
    }