from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime

class User(Base):
    __tablename__ = "user"
    id = Column(String(36), primary_key=True, index=True)  # UUID is 36 chars
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True)  # Adjust length as needed
    fullname = Column(String(255), nullable=False) 
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    registered_at = Column(DateTime)
    has_used_trial = Column(Boolean, default=False)  # Track if user has used their free trial
    password_reset_token = Column(String(255), nullable=True)
    password_reset_token_expiry = Column(DateTime, nullable=True)
    last_password_change = Column(DateTime, default=datetime.utcnow)
    role = Column(String(50), default="user")  # Add this line for RBAC

    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="user")
    product_selections = relationship("ProductSelection", back_populates="user") 