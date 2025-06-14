from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from app.db import Base
from datetime import datetime

class UserSubscription(Base):
    __tablename__ = "user_subscription"
    id = Column(String(36), primary_key=True, index=True)  # UUID is 36 chars
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    plan_id = Column(String(36), ForeignKey("subscription_plan.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow) 