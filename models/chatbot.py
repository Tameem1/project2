# models/chatbot.py
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from db.database import Base
from sqlalchemy.sql import func

class Chatbot(Base):
    __tablename__ = "chatbots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # **New field to store the API key**
    api_key = Column(String, unique=True, index=True, nullable=True)
    demo_message_count = Column(Integer, default=0, nullable=False)

    customer = relationship("Customer", back_populates="chatbots")
    documents = relationship("Document", back_populates="chatbot")
    chat_history = relationship("ChatHistory", back_populates="chatbot")