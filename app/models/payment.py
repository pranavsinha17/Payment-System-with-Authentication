from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from app.db import Base

class Payment(Base):
    __tablename__ = "payment"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("user_subscription.id"), nullable=False)
    razorpay_payment_id = Column(String)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    paid_at = Column(DateTime) 