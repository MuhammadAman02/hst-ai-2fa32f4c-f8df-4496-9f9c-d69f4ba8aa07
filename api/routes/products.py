from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from services.business import ProductService
from models.schemas import ProductResponse

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get products with pagination and filtering"""
    product_service = ProductService(db)
    products, total_pages = product_service.get_products_paginated(
        category=category,
        search=search,
        page=page,
        per_page=per_page
    )
    return products

@router.get("/featured", response_model=List[ProductResponse])
async def get_featured_products(
    limit: int = Query(8, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get featured products"""
    product_service = ProductService(db)
    return product_service.get_featured_products(limit=limit)

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all product categories"""
    product_service = ProductService(db)
    return {"categories": product_service.get_categories()}

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    product_service = ProductService(db)
    product = product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product