# services/chatbot_service.py

import uuid
import secrets
from sqlalchemy.orm import Session
from models.chatbot import Chatbot
from datetime import datetime
from uuid import UUID
import uuid

def create_chatbot(name: str, description: str, customer_id: str, db: Session) -> Chatbot:
    """
    Creates and persists a new chatbot in the database.
    """
    try:
        customer_uuid = UUID(customer_id)

        # Generate a secure, random API key
        new_api_key = secrets.token_urlsafe(32)

        chatbot = Chatbot(
            id=uuid.uuid4(),
            name=name,
            description=description,
            customer_id=customer_uuid,
            created_at=datetime.utcnow(),
            api_key=new_api_key  # store the newly generated key
        )
        db.add(chatbot)
        db.commit()
        db.refresh(chatbot)

        initialize_vector_store(customer_id, chatbot.id)

        return chatbot
    except Exception as e:
        db.rollback()
        raise e

def list_chatbots(customer_id: str, db: Session) -> list[Chatbot]:
    """
    Retrieves all chatbots associated with a specific customer.
    
    Args:
        customer_id (str): The UUID of the customer.
        db (Session): The database session.
    
    Returns:
        list[Chatbot]: A list of chatbot instances.
    """
    try:
        return db.query(Chatbot).filter(Chatbot.customer_id == customer_id).all()
    except Exception as e:
        raise e

def get_chatbot_by_id(chatbot_id: UUID, db: Session) -> Chatbot:
    """
    Retrieves a chatbot by its ID.
    
    Args:
        chatbot_id (UUID): The UUID of the chatbot.
        db (Session): The database session.
    
    Returns:
        Chatbot or None: The chatbot instance if found, else None.
    """
    try:
        return db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    except Exception as e:
        raise e

def initialize_vector_store(customer_id: str, chatbot_id: UUID):
    """
    Initializes the vector store directory for the new chatbot.
    
    Args:
        customer_id (str): The UUID of the customer.
        chatbot_id (UUID): The UUID of the chatbot.
    """
    from utils.constants import get_vectorstore_path
    import os
    
    path = get_vectorstore_path(customer_id, str(chatbot_id))
    os.makedirs(path, exist_ok=True)
    # Initialize Chroma or any other vector store here if necessary