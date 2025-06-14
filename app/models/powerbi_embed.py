from sqlalchemy import Column, String, DateTime, ForeignKey
from app.db import Base

class PowerBIEmbed(Base):
    __tablename__ = "powerbi_embed"
    id = Column(String, primary_key=True, index=True)
    upload_id = Column(String, ForeignKey("upload.id"), nullable=False)
    report_id = Column(String)
    dataset_id = Column(String)
    embed_token = Column(String)
    expires_at = Column(DateTime) 