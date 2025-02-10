# models/chat_history.py
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from db.database import Base
from sqlalchemy.sql import func

# models/chat_history.py (example extension)

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chatbot_id = Column(UUID(as_uuid=True), ForeignKey("chatbots.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # New fields, if you want them:
    input_tokens = Column(Integer, nullable=True)   # e.g. tokens in question
    output_tokens = Column(Integer, nullable=True)  # e.g. tokens in answer
    source_docs = Column(Text, nullable=True)       # store as JSON or text, for doc references

    chatbot = relationship("Chatbot", back_populates="chat_history")
    user = relationship("User", back_populates="chat_history")