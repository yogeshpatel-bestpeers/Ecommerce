from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.Models.products import Product, Category
from app.Schema.products import ProductCreate, CategoryCreate
from fastapi import Depends
from app.database import get_db


class Products:
    def __init__(self, db: AsyncSession):
        self.db = db

    @classmethod
    async def create(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)

    async def get_products(self, skip: int = 0, limit: int = 10):
        result = await self.db.execute(
            select(Product).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_product(self, product_id: int):
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def create_product(self, product: ProductCreate):
        db_product = Product(**product)
        self.db.add(db_product)
        await self.db.commit()
        await self.db.refresh(db_product)
        return db_product

    async def delete_product(self, product_id: int):
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        if product:
            await self.db.delete(product)
            await self.db.commit()
        return product

    async def update_product(self, product_id: int, update_data: dict):
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        if product:
            for key, value in update_data.items():
                setattr(product, key, value)
            await self.db.commit()
            await self.db.refresh(product)
        return product

  
    async def create_category(self, category: CategoryCreate):
        db_category = Category(**category)
        self.db.add(db_category)
        await self.db.commit()
        await self.db.refresh(db_category)
        return db_category

    async def get_categories(self):
        result = await self.db.execute(select(Category))
        return result.scalars().all()
