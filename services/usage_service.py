# services/usage_service.py
from sqlalchemy.orm import Session
from models.usage_token import UsageToken
from fastapi import HTTPException

def get_usage(db: Session, customer_id: str):
    usage = db.query(UsageToken).filter(UsageToken.customer_id == customer_id).first()
    if not usage:
        usage = UsageToken(
            customer_id=customer_id,
            tokens_remaining=10000  # or whatever default you want
        )
        db.add(usage)
        db.commit()
        db.refresh(usage)
    return usage

def consume_tokens(db: Session, customer_id: str, input_tokens: int, output_tokens: int):
    """
    Subtract the given input & output tokens from the user's balance,
    and update usage stats.
    """
    usage = get_usage(db, customer_id)

    total_new_tokens = input_tokens + output_tokens

    if usage.tokens_remaining < total_new_tokens:
        raise HTTPException(status_code=400, detail="Insufficient tokens")

    # Update the separate fields
    usage.input_tokens_used += input_tokens
    usage.output_tokens_used += output_tokens

    # Also update the total usage
    usage.tokens_used += total_new_tokens

    # Subtract from remaining
    usage.tokens_remaining -= total_new_tokens

    db.commit()
    return usage