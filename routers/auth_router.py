# routers/auth_router.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from db.session import get_db
from services.auth_service import (
    authenticate_user,
    create_jwt_token,
    register_user
)

auth_router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    password: str
    business_name: str
    contact_email: str

@auth_router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user and creates a new Customer record.
    - 'business_name' can be shared among customers.
    - 'contact_email' must be unique.
    - 'username' must be unique.
    """
    user = register_user(
        username=request.username,
        password=request.password,
        business_name=request.business_name,
        contact_email=request.contact_email,
        db=db
    )
    # Create a JWT token for the newly registered user:
    token = create_jwt_token({
        "sub": user.username,
        "customer_id": str(user.customer_id),
        "user_id": str(user.id)
    })
    return {"message": "User registered successfully!", "token": token}

@auth_router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Standard OAuth2 password login to obtain a JWT bearer token.
    """
    token = authenticate_user(form_data.username, form_data.password, db)
    return {"access_token": token, "token_type": "bearer"}