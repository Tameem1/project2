# routers/auth_router.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.auth_service import register_user, create_jwt_token
from db.session import get_db
from sqlalchemy.orm import Session

auth_router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    password: str
    customer_name: str
    contact_email: str

@auth_router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(
        username=request.username,
        password=request.password,
        customer_name=request.customer_name,
        contact_email=request.contact_email,
        db=db
    )
    # Create a JWT token for the newly registered user:
    token = create_jwt_token({
        "sub": user.username,
        "customer_id": str(user.customer_id),
        "user_id": str(user.id)
    })
    return {"message": "User registered successfully", "token": token}