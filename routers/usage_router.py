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
    """
    GET /api/{customer_id}/usage
    Retrieves the usage info (tokens used, remaining, etc.) for the 
    authenticated customer's ID.
    """
    token_customer_id = user.get("customer_id")
    if token_customer_id != customer_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this customer data")
    
    usage = get_usage(db, customer_id)
    return {
        "tokens_used": usage.tokens_used,
        "tokens_remaining": usage.tokens_remaining,
        "last_updated": usage.last_updated
    }