from pydantic import BaseModel
from typing import Optional

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    image_url: Optional[str] = None
    is_active: Optional[bool] = True
    category_id: Optional[int]

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    category: Optional[CategoryOut]

    class Config:
        orm_mode = True
