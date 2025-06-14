from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime
from uuid import uuid4

class UserSubscription(Base):
    __tablename__ = "user_subscription"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    plan_id = Column(String(36), ForeignKey("subscription_plan.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    product_selections = relationship("ProductSelection", back_populates="subscription") 