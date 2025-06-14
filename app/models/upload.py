from sqlalchemy import Column, String, DateTime, ForeignKey
from app.db import Base

class Upload(Base):
    __tablename__ = "upload"
    id = Column(String(36), primary_key=True, index=True)  # UUID is 36 chars
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("product.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    upload_time = Column(DateTime, nullable=False)
    status = Column(String(50))
    output_url = Column(String(255))
    delete_after = Column(DateTime) 