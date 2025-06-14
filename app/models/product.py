from sqlalchemy import Column, String
from app.db import Base

class Product(Base):
    __tablename__ = "product"
    id = Column(String(36), primary_key=True, index=True)  # UUID is 36 chars
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    type = Column(String(50))
    script_ref = Column(String(255))
    output_type = Column(String(50)) 