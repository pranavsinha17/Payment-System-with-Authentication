from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from pydantic import validator

class UserBase(BaseModel):
    email: EmailStr
    phone: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: str
    is_active: bool
    registered_at: datetime
    has_used_trial: bool

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

class SubscriptionPlanOut(BaseModel):
    id: str
    name: str
    price: float
    duration: str
    product_ids: list[str]
    created_at: datetime

    @validator('product_ids', pre=True)
    def parse_product_ids(cls, v):
        if isinstance(v, str):
            # Remove brackets and quotes, then split by comma
            v = v.strip('[]').replace('"', '').replace("'", "").split(',')
            # Remove any empty strings
            v = [x.strip() for x in v if x.strip()]
        return v

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
    razorpay_order_id: str
    razorpay_signature: str
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

class CreateOrderRequest(BaseModel):
    subscription_id: str
    amount: float
    currency: str = "INR"

class CreateOrderResponse(BaseModel):
    order_id: str
    amount: float
    currency: str
    key_id: str

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

class ProductCreate(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: str | None = None
    script_ref: str | None = None
    output_type: str | None = None

class ProductOut(BaseModel):
    id: str
    name: str
    description: str | None
    type: str | None
    script_ref: str | None
    output_type: str | None

    class Config:
        from_attributes = True

class DetailedProductSelection(BaseModel):
    id: str
    product_id: str
    is_active: bool
    created_at: datetime
    product: ProductOut

    class Config:
        from_attributes = True

class DetailedSubscriptionResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    start_date: datetime
    end_date: datetime
    is_active: bool
    created_at: datetime
    plan: SubscriptionPlanOut
    product_selections: list[DetailedProductSelection]
    total_price: float
    number_of_products: int

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str 