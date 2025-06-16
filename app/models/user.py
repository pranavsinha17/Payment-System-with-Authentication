from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = "user"
    id = Column(String(36), primary_key=True, index=True)  # UUID is 36 chars
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True)  # Adjust length as needed
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    registered_at = Column(DateTime)
    has_used_trial = Column(Boolean, default=False)  # Track if user has used their free trial

    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="user")
    product_selections = relationship("ProductSelection", back_populates="user") 