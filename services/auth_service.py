# services/auth_service.py
import os
from datetime import datetime, timedelta
from passlib.hash import bcrypt
import jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.user import User
from models.customer import Customer
from db.session import get_db

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.verify(password, hashed_password)

def create_jwt_token(data: dict, expires_delta: timedelta = timedelta(hours=1)) -> str:
    payload = data.copy()
    payload.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def register_user(username: str, password: str, customer_name: str, contact_email: str, db: Session):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    customer = db.query(Customer).filter(Customer.name == customer_name).first()
    if not customer:
        customer = Customer(name=customer_name, contact_email=contact_email)
        db.add(customer)
        db.commit()
        db.refresh(customer)
    
    hashed_password = hash_password(password)
    user = User(username=username, password_hash=hashed_password, customer_id=customer.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def register_user_from_oauth(user_info: dict, db: Session):
    """
    Given user info from an OAuth provider, register the user if they don't exist.
    Expects at least an "email" key; uses "name" (or the email prefix) as the username.
    """
    email = user_info.get("email")
    username = user_info.get("name") or email.split('@')[0]
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    # Create a customer if one does not exist.
    customer_name = f"{username}'s Customer"
    customer = db.query(Customer).filter(Customer.name == customer_name).first()
    if not customer:
        customer = Customer(name=customer_name, contact_email=email)
        db.add(customer)
        db.commit()
        db.refresh(customer)
    # Create the user using a random dummy password
    import os
    dummy_password = os.urandom(16).hex()
    hashed_password = hash_password(dummy_password)
    user = User(username=username, password_hash=hashed_password, customer_id=customer.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt_token({
        "sub": user.username,
        "customer_id": str(user.customer_id),
        "user_id": str(user.id)
    })
    return token