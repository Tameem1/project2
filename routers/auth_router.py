# routers/auth_router.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from services.auth_service import register_user, authenticate_user
from db.session import get_db
from sqlalchemy.orm import Session

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

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
    return {"message": "User registered successfully"}

@auth_router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token = authenticate_user(form_data.username, form_data.password, db)
    return {"access_token": token, "token_type": "bearer"}