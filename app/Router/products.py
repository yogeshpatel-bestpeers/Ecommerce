from fastapi import APIRouter, Depends
from app.Service.product import Products
from app.Schema.products import ProductCreate,CategoryCreate

router = APIRouter(
    tags=["products"]
)


@router.get("/products/get")
async def list_products(products: Products = Depends(Products.create)):
    return await products.get_products()

@router.post("/products/create")
async def create_products(request : ProductCreate,products: Products = Depends(Products.create)):
    return await products.create_product(request.model_dump())

@router.post("/categories/create")
async def create_categorie(request : CategoryCreate,products: Products = Depends(Products.create)):
    
    return await products.create_category(request.model_dump())
    


