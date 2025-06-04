from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db
from services.auth import get_current_admin_user
from services.business import ProductService
from models.schemas import User, ProductCreate, ProductResponse
from core.utils import save_uploaded_image

router = APIRouter()

@router.get("/products")
async def admin_get_products(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all products for admin"""
    product_service = ProductService(db)
    products, _ = product_service.get_products_paginated(page=1, per_page=100)
    return products

@router.post("/products", response_model=ProductResponse)
async def admin_create_product(
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    category: str = Form(...),
    size: str = Form(""),
    color: str = Form(""),
    stock_quantity: int = Form(0),
    is_featured: bool = Form(False),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create new product"""
    product_service = ProductService(db)
    
    # Handle image upload
    image_url = None
    if image:
        filename = save_uploaded_image(image)
        if filename:
            image_url = f"/static/images/products/{filename}"
    
    product_data = ProductCreate(
        name=name,
        description=description,
        price=price,
        category=category,
        size=size,
        color=color,
        stock_quantity=stock_quantity,
        is_featured=is_featured
    )
    
    product = product_service.create_product(product_data)
    
    # Update image URL if uploaded
    if image_url:
        product_service.update_product(product.id, {"image_url": image_url})
        product.image_url = image_url
    
    return product

@router.put("/products/{product_id}")
async def admin_update_product(
    product_id: int,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    category: str = Form(...),
    size: str = Form(""),
    color: str = Form(""),
    stock_quantity: int = Form(0),
    is_featured: bool = Form(False),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update product"""
    product_service = ProductService(db)
    
    update_data = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "size": size,
        "color": color,
        "stock_quantity": stock_quantity,
        "is_featured": is_featured,
        "is_active": is_active
    }
    
    # Handle image upload
    if image:
        filename = save_uploaded_image(image)
        if filename:
            update_data["image_url"] = f"/static/images/products/{filename}"
    
    product = product_service.update_product(product_id, update_data)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product