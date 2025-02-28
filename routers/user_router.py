# routers/user_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from db.session import get_db
from middleware import get_current_user
from models.user import User
from models.customer import Customer

user_router = APIRouter()

@user_router.get("/user/profile")
def get_user_profile(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns the current user's profile data:
      - username
      - business_name (customer's name)
      - contact_email
    """
    user_id = user.get("user_id")
    customer_id = user.get("customer_id")

    if not user_id or not customer_id:
        raise HTTPException(status_code=400, detail="Missing user_id or customer_id in token")

    user_obj = db.query(User).filter(User.id == user_id).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    customer_obj = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer_obj:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "username": user_obj.username,
        "business_name": customer_obj.name,
        "contact_email": customer_obj.contact_email
    }