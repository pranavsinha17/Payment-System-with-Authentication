from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from app.db import Base
from datetime import datetime
from uuid import uuid4
import json

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plan"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    duration = Column(String(20), nullable=False)  # monthly, quarterly, yearly
    product_ids = Column(String(1000), nullable=False)  # Store as JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="plan")

    def __init__(self, **kwargs):
        if 'product_ids' in kwargs and isinstance(kwargs['product_ids'], list):
            kwargs['product_ids'] = json.dumps(kwargs['product_ids'])
        super().__init__(**kwargs)