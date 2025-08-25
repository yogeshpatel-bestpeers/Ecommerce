from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime


class OrderItemBase(BaseModel):
    product_id:int
    quantity: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemOut(OrderItemBase):
    id: uuid.UUID
    price: float

    class Config:
        orm_mode = True


class OrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    customer_name: Optional[str]
    customer_email: Optional[EmailStr]
    status: Optional[str]


class OrderOut(BaseModel):
    id: uuid.UUID
    customer_name: str
    customer_email: EmailStr
    total_amount: float
    status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemOut]

    class Config:
        orm_mode = True
