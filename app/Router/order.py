# app/api/order.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import uuid

from app.database import get_db
from app.Models.order import OrderModel, OrderItem
from app.Models.products import Product  
from app.Schema.orders import OrderCreate, OrderUpdate, OrderOut

route = APIRouter(prefix="/orders", tags=["Orders"])

@route.post("/", response_model=OrderOut)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):

  
    total = 0
    items = []
    for item in order.items:
        result=await db.execute(
            select(Product).where(Product.id== item.product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        total += product.price* item.quantity
        items.append(OrderItem(product_id=item.product_id,quantity=item.quantity, price=product.price))
        
    new_order = OrderModel(
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        total_amount=total,
        items=items,
    )
    db.add(new_order)
    await db.commit()
    
    await db.refresh(new_order)
    return new_order

@route.get("/", response_model=List[OrderOut])
async def get_orders(limit:int = 0,skip:int = 0,db: AsyncSession = Depends(get_db)):
    result = await db.execute(
    select(OrderModel).offset(skip).limit(limit)
)
    return result.scalars().all()


@route.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
 
    result =await db.execute(
        select(OrderModel).filter(OrderModel.id == order_id)
    )

    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@route.put("/{order_id}", response_model=OrderOut)
async def update_order(order_id: uuid.UUID, order_update: OrderUpdate, db: AsyncSession = Depends(get_db)):
    
    result =await db.execute(
        select(OrderModel).filter(OrderModel.id == order_id)
    )

    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    for key, value in order_update.dict(exclude_unset=True).items():
        setattr(order, key, value)

    await db.commit()
    await db.refresh(order)
    return order


@route.delete("/{order_id}")
async def delete_order(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
  

    result =await db.execute(
        select(OrderModel).filter(OrderModel.id == order_id)
    )

    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}