from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    phone: Optional[str]
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    phone: Optional[str]
    is_active: bool
    registered_at: Optional[datetime]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str 