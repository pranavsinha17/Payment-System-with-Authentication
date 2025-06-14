from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.types import JSON
from app.db import Base
from datetime import datetime

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plan"
    id = Column(String(36), primary_key=True, index=True)  # UUID is 36 chars
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    duration = Column(String(20), nullable=False)  # e.g., 'monthly', 'quarterly', 'yearly'
    product_ids = Column(JSON)  # List of product IDs included in the plan
    created_at = Column(DateTime, default=datetime.utcnow)