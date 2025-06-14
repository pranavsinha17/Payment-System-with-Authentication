from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    phone: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: str
    is_active: bool
    registered_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class SubscriptionPlanBase(BaseModel):
    name: str
    price: float
    duration: str
    product_ids: List[str]

class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass

class SubscriptionPlanOut(SubscriptionPlanBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserSubscriptionBase(BaseModel):
    plan_id: str
    start_date: datetime
    end_date: datetime
    is_active: bool

class UserSubscriptionCreate(UserSubscriptionBase):
    pass

class UserSubscriptionOut(UserSubscriptionBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    subscription_id: str
    razorpay_payment_id: str
    amount: float
    status: str
    paid_at: datetime

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(PaymentBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class PlanChangeResponse(BaseModel):
    subscription: UserSubscriptionOut
    price_difference: float
    remaining_days: int

    class Config:
        from_attributes = True

class ProductSelectionBase(BaseModel):
    product_id: str

class ProductSelectionCreate(ProductSelectionBase):
    subscription_id: str

class ProductSelectionOut(ProductSelectionBase):
    id: str
    user_id: str
    subscription_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ProductSelectionBulkCreate(BaseModel):
    product_ids: List[str]
    subscription_id: str

class ProductSelectionBulkResponse(BaseModel):
    selections: List[ProductSelectionOut]
    total_price: float
    duration: str  # monthly, quarterly, yearly
    number_of_products: int 