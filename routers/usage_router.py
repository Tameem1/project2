# routers/usage_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from services.usage_service import get_usage
from middleware import get_current_user
from db.session import get_db

usage_router = APIRouter()

@usage_router.get("/{customer_id}/usage", tags=["Usage"])
def get_customer_usage(
    customer_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Ensure the token's customer matches
    token_customer_id = user.get("customer_id")
    if token_customer_id != customer_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this customer data")
    
    usage = get_usage(db, customer_id)
    return {
        "tokens_used_total": usage.tokens_used,  # total usage
        "tokens_used_input": usage.input_tokens_used,
        "tokens_used_output": usage.output_tokens_used,
        "tokens_remaining": usage.tokens_remaining,
        "last_updated": usage.last_updated
    }