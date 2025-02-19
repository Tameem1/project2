# services/auth_service.py
import os
from datetime import datetime, timedelta
from passlib.hash import bcrypt
import jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.user import User
from models.customer import Customer

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

def register_user(username: str, password: str, business_name: str, contact_email: str, db: Session):
    """
    Creates a new User and Customer record. Enforces:
      - Unique username (no duplicates in 'users')
      - Unique contact_email (no duplicates in 'customers')
      - Disallows the case where username == password
      - Allows repeated business_name (Customer.name)
    """
    # Disallow password equal to username for security reasons
    if username == password:
        raise HTTPException(
            status_code=400,
            detail="Registration failed: password cannot be the same as username."
        )

    # Check if the username is already taken
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Registration failed: This username is already taken."
        )

    # Check if the contact_email is already used by any customer
    existing_customer = db.query(Customer).filter(Customer.contact_email == contact_email).first()
    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="Registration failed: This email is already registered."
        )

    # Create the Customer (business_name can be repeated)
    new_customer = Customer(
        name=business_name,
        contact_email=contact_email,
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    # Hash password and create the User
    hashed_password = hash_password(password)
    user = User(
        username=username,
        password_hash=hashed_password,
        customer_id=new_customer.id
    )
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