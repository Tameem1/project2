from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from services.query_service import process_query
from middleware import get_current_user
from db.session import get_db
from sqlalchemy.orm import Session
from uuid import UUID
from services.chatbot_service import get_chatbot_by_id

query_router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@query_router.post("/public/{chatbot_id}/query")
def public_query_endpoint(
    chatbot_id: UUID,
    request: QueryRequest,
    x_chatbot_api_key: str = Header(None),
    db: Session = Depends(get_db)
):
    if not x_chatbot_api_key:
        raise HTTPException(status_code=401, detail="Missing X-CHATBOT-API-KEY header")
    
    # Look up the chatbot
    chatbot = get_chatbot_by_id(chatbot_id, db)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    # Check if the API key matches
    if chatbot.api_key != x_chatbot_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")

    # Process the query without converting chatbot_id to a string
    response = process_query(
        question=request.question,
        customer_id=str(chatbot.customer_id),
        chatbot_id=chatbot_id,  # <-- Pass the UUID directly!
        user_id=None,  # optional - or set to a "public user" if needed
        db=db
    )
    return response

@query_router.post("/{customer_id}/{chatbot_id}/query")
def query_endpoint(
    customer_id: str,
    chatbot_id: UUID,
    request: QueryRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Confirm token’s customer_id
    token_customer_id = user.get("customer_id")
    if token_customer_id != customer_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this customer's chatbot")

    # Check that the chatbot belongs to that customer
    chatbot = get_chatbot_by_id(chatbot_id=chatbot_id, db=db)
    if not chatbot or str(chatbot.customer_id) != customer_id:
        raise HTTPException(status_code=404, detail="Chatbot not found for this customer")

    # Process the query without converting chatbot_id to a string
    response = process_query(
        question=request.question,
        customer_id=customer_id,
        chatbot_id=chatbot_id,  # <-- Pass the UUID directly!
        user_id=user.get("user_id"),
        db=db
    )
    return response