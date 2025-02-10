# routers/chat_history_router.py

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel, parse_obj_as

from models.chat_history import ChatHistory
from services.chat_history_service import (
    get_chat_history_by_chatbot, clear_chat_history_for_chatbot
)
from middleware import get_current_user
from db.session import get_db

class ChatHistoryEntry(BaseModel):
    id: UUID
    chatbot_id: UUID
    user_id: UUID | None
    question: str
    answer: str
    timestamp: str  # ISO8601 string

class ChatHistoryResponse(BaseModel):
    chat_history: List[ChatHistoryEntry]

chat_history_router = APIRouter()

@chat_history_router.get(
    "/{customer_id}/{chatbot_id}/history",
    response_model=ChatHistoryResponse,
    status_code=status.HTTP_200_OK
)
def retrieve_chat_history(
    customer_id: str,
    chatbot_id: UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET /api/{customer_id}/{chatbot_id}/history
    Retrieves the chat history for a specific chatbot, ensuring:
      - The route's customer_id == token's customer_id
      - The chatbot belongs to that customer
    """
    token_customer_id = user.get("customer_id")
    if token_customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access this customer's chat history."
        )

    chat_history = get_chat_history_by_chatbot(db, customer_id, chatbot_id)
    if chat_history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No chat history found for that chatbot."
        )

    # Convert SQLAlchemy objects -> Pydantic models
    chat_history_dicts = []
    for entry in chat_history:
        chat_history_dicts.append({
            "id": entry.id,
            "chatbot_id": entry.chatbot_id,
            "user_id": entry.user_id,
            "question": entry.question,
            "answer": entry.answer,
            "timestamp": entry.timestamp.isoformat() if entry.timestamp else None
        })

    chat_history_entries = parse_obj_as(List[ChatHistoryEntry], chat_history_dicts)
    return ChatHistoryResponse(chat_history=chat_history_entries)


@chat_history_router.delete(
    "/{customer_id}/{chatbot_id}/history",
    status_code=status.HTTP_204_NO_CONTENT
)
def clear_chat_history(
    customer_id: str,
    chatbot_id: UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    DELETE /api/{customer_id}/{chatbot_id}/history
    Clears all chat history for a specific chatbot.
    """
    token_customer_id = user.get("customer_id")
    if token_customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to clear this customer's chat history."
        )

    success = clear_chat_history_for_chatbot(db, customer_id, chatbot_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found or no history to clear."
        )