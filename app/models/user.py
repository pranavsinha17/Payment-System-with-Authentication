from sqlalchemy import Column, String, Boolean, DateTime
from app.db import Base

class User(Base):
    __tablename__ = "user"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    registered_at = Column(DateTime) 