# models/usage_token.py

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from db.database import Base
from sqlalchemy.sql import func

class UsageToken(Base):
    __tablename__ = "usage_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)

    # The total number of tokens the user can consume (determined by plan)
    number_of_tokens = Column(Integer, default=1000, nullable=False)

    # How many tokens have actually been used
    tokens_used = Column(Integer, default=0)
    # If you store the current remaining physically, you can keep it in sync:
    tokens_remaining = Column(Integer, default=1000)

    # Additional details
    input_tokens_used = Column(Integer, default=0, nullable=False)
    output_tokens_used = Column(Integer, default=0, nullable=False)

    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="usage_records")