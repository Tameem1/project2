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
    """
    Public endpoint that only requires the Chatbot's API key, passed as
    X-CHATBOT-API-KEY. This allows end users to query the chatbot from
    a website snippet (without a JWT).
    """
    if not x_chatbot_api_key:
        raise HTTPException(status_code=401, detail="Missing X-CHATBOT-API-KEY header")
    
    # Look up the chatbot
    chatbot = get_chatbot_by_id(chatbot_id, db)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    # Check if the API key matches
    if chatbot.api_key != x_chatbot_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")

    # If everything’s good, process the query
    response = process_query(
        question=request.question,
        customer_id=str(chatbot.customer_id),  # from the chatbot record
        chatbot_id=str(chatbot_id),
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
    """
    Receives a user's question for a specific chatbot. Checks that
    the authenticated user belongs to the correct customer_id, and that
    the chatbot belongs to that customer.
    
    POST /api/{customer_id}/{chatbot_id}/query
    """

    # 1) Confirm token’s customer_id
    token_customer_id = user.get("customer_id")
    if token_customer_id != customer_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this customer's chatbot")

    # 2) Check that the chatbot belongs to that customer
    chatbot = get_chatbot_by_id(chatbot_id=chatbot_id, db=db)
    if not chatbot or str(chatbot.customer_id) != customer_id:
        raise HTTPException(status_code=404, detail="Chatbot not found for this customer")

    # 3) Check for user_id in token (optional, but helpful for logging)
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")
    
    # 4) Process the query
    response = process_query(
        question=request.question,
        customer_id=customer_id,
        chatbot_id=str(chatbot_id),
        user_id=user_id,
        db=db
    )
    return response