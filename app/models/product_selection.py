from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime
from uuid import uuid4

class ProductSelection(Base):
    __tablename__ = "product_selections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    subscription_id = Column(String(36), ForeignKey("user_subscription.id"), nullable=False)
    product_id = Column(String(36), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="product_selections")
    subscription = relationship("UserSubscription", back_populates="product_selections") 