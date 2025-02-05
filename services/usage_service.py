# services/usage_service.py
from sqlalchemy.orm import Session
from models.usage_token import UsageToken
from models.customer import Customer
from fastapi import HTTPException

def get_usage(db: Session, customer_id: str):
    usage = db.query(UsageToken).filter(UsageToken.customer_id == customer_id).first()
    if not usage:
        usage = UsageToken(customer_id=customer_id, tokens_remaining=10000)  # Default tokens
        db.add(usage)
        db.commit()
        db.refresh(usage)
    return usage

def consume_tokens(db: Session, customer_id: str, tokens: int):
    usage = get_usage(db, customer_id)
    if usage.tokens_remaining < tokens:
        raise HTTPException(status_code=400, detail="Insufficient tokens")
    usage.tokens_used += tokens
    usage.tokens_remaining -= tokens
    db.commit()
    return usage