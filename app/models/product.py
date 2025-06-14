from sqlalchemy import Column, String
from app.db import Base

class Product(Base):
    __tablename__ = "product"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(String)
    script_ref = Column(String)
    output_type = Column(String) 