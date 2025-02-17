# models/customer.py
from sqlalchemy import Column, String, DateTime, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from db.database import Base
from sqlalchemy.sql import func

class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    contact_email = Column(String, unique=True, nullable=False)
    billing_info = Column(JSON, nullable=True)  # Alternatively, create a separate Billing table
    usage_tokens = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    users = relationship("User", back_populates="customer")
    chatbots = relationship("Chatbot", back_populates="customer")
    billing_records = relationship("Billing", back_populates="customer")
    usage_records = relationship("UsageToken", back_populates="customer")