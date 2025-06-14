from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.types import JSON
from app.db import Base

class Alert(Base):
    __tablename__ = "alert"
    id = Column(String, primary_key=True, index=True)
    upload_id = Column(String, ForeignKey("upload.id"), nullable=False)
    scheduled_time = Column(DateTime)
    sent_time = Column(DateTime)
    response = Column(JSON) 