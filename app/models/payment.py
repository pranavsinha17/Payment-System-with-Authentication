from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from app.db import Base
from datetime import datetime

class Payment(Base):
    __tablename__ = "payment"
    id = Column(String(36), primary_key=True, index=True)  # UUID is 36 chars
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    subscription_id = Column(String(36), ForeignKey("user_subscription.id"), nullable=False)
    razorpay_payment_id = Column(String(100))
    razorpay_order_id = Column(String(100))
    razorpay_signature = Column(String(255))
    amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    paid_at = Column(DateTime) 
    created_at = Column(DateTime, default=datetime.utcnow)