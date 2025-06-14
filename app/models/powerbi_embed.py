from sqlalchemy import Column, String, DateTime, ForeignKey
from app.db import Base

class PowerBIEmbed(Base):
    __tablename__ = "powerbi_embed"
    id = Column(String(36), primary_key=True, index=True)  # UUID is 36 chars
    upload_id = Column(String(36), ForeignKey("upload.id"), nullable=False)
    report_id = Column(String(100))
    dataset_id = Column(String(100))
    embed_token = Column(String(255))
    expires_at = Column(DateTime) 