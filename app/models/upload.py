from sqlalchemy import Column, String, DateTime, ForeignKey
from app.db import Base

class Upload(Base):
    __tablename__ = "upload"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    product_id = Column(String, ForeignKey("product.id"), nullable=False)
    file_name = Column(String, nullable=False)
    upload_time = Column(DateTime, nullable=False)
    status = Column(String)
    output_url = Column(String)
    delete_after = Column(DateTime) 