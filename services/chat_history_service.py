# services/chat_history_service.py

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from models.chat_history import ChatHistory

from uuid import UUID
def log_chat(
    db: Session, 
    chatbot_id: UUID, 
    user_id: Optional[str], 
    question: str, 
    answer: str,
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    source_docs: Optional[list[str]] = None
) -> ChatHistory:
    chat = ChatHistory(
        chatbot_id=chatbot_id,
        user_id=user_id,
        question=question,
        answer=answer
    )

    # If these columns exist in ChatHistory, set them:
    if input_tokens is not None:
        chat.input_tokens = input_tokens
    if output_tokens is not None:
        chat.output_tokens = output_tokens
    if source_docs is not None:
        # e.g. store as JSON-serialized string
        chat.source_docs = ", ".join(source_docs)

    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

def get_chat_history_by_chatbot(
    db: Session,
    customer_id: str,  # still a string from the token
    chatbot_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> Optional[List[ChatHistory]]:
    """
    Retrieve chat history entries for a specific chatbot belonging to a customer.
    """
    try:
        # Convert customer_id string to a UUID for proper comparison
        customer_uuid = UUID(customer_id)
        
        # Verify that the chatbot belongs to the customer using the correct UUID type
        chatbot_exists = db.query(ChatHistory).filter(
            ChatHistory.chatbot_id == chatbot_id,
            ChatHistory.chatbot.has(customer_id=customer_uuid)
        ).first()
        
        if not chatbot_exists:
            return None
        
        # Retrieve chat history entries
        chat_history = db.query(ChatHistory).filter(
            ChatHistory.chatbot_id == chatbot_id,
            ChatHistory.chatbot.has(customer_id=customer_uuid)
        ).order_by(ChatHistory.timestamp.desc()).offset(skip).limit(limit).all()
        
        return chat_history
    except SQLAlchemyError as e:
        print(f"Error retrieving chat history: {e}")
        return None

def clear_chat_history_for_chatbot(
    db: Session,
    customer_id: UUID,
    chatbot_id: UUID
) -> bool:
    """
    Delete all chat history entries for a specific chatbot belonging to a customer.
    
    :param db: Database session.
    :param customer_id: UUID of the customer.
    :param chatbot_id: UUID of the chatbot.
    :return: True if deletion was successful, False otherwise.
    """
    try:
        # Verify that the chatbot belongs to the customer
        chatbot_exists = db.query(ChatHistory).filter(
            ChatHistory.chatbot_id == chatbot_id,
            ChatHistory.chatbot.has(customer_id=customer_id)
        ).first()
        
        if not chatbot_exists:
            return False
        
        # Delete chat history entries
        db.query(ChatHistory).filter(
            ChatHistory.chatbot_id == chatbot_id,
            ChatHistory.chatbot.has(customer_id=customer_id)
        ).delete(synchronize_session=False)
        
        db.commit()
        return True
    except SQLAlchemyError as e:
        # Log the error (optional)
        print(f"Error deleting chat history: {e}")
        db.rollback()
        return False