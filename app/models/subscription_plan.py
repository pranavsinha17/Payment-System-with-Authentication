from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from app.db import Base
from datetime import datetime
from uuid import uuid4

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plan"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    duration = Column(String(20), nullable=False)  # monthly, quarterly, yearly
    product_ids = Column(String(1000), nullable=False)  # Comma-separated list of product IDs
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="plan")