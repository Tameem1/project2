# models/demo_usage.py
from db.database import Base
from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid

class DemoUsage(Base):
    __tablename__ = "demo_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    chatbot_id = Column(UUID(as_uuid=True), nullable=False)
    message_count = Column(Integer, default=0, nullable=False)