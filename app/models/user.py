from sqlalchemy import Column, String, Boolean, DateTime
from app.db import Base

class User(Base):
    __tablename__ = "user"
    id = Column(String(36), primary_key=True, index=True)  # UUID is 36 chars
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True)  # Adjust length as needed
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    registered_at = Column(DateTime) 