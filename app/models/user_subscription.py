from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from app.db import Base

class UserSubscription(Base):
    __tablename__ = "user_subscription"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    plan_id = Column(String, ForeignKey("subscription_plan.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True) 