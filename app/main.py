from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
import os

from core.database import get_db, engine
from models.schemas import User, Product, CartItem, Order
from services.auth import get_current_user, create_access_token, verify_password, get_password_hash
from services.business import ProductService, CartService, OrderService
from api.routes.auth import router as auth_router
from api.routes.products import router as products_router
from api.routes.cart import router as cart_router
from api.routes.admin import router as admin_router

# Create database tables
from models.schemas import Base
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ASICS Shoe Store", description="Premium ASICS footwear e-commerce platform")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(products_router, prefix="/api/products", tags=["products"])
app.include_router(cart_router, prefix="/api/cart", tags=["cart"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page with featured products"""
    product_service = ProductService(db)
    featured_products = product_service.get_featured_products(limit=8)
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "products": featured_products,
        "page_title": "ASICS Shoe Store - Premium Running Shoes"
    })

@app.get("/products", response_class=HTMLResponse)
async def products_page(
    request: Request, 
    category: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    db: Session = Depends(get_db)
):
    """Products listing page"""
    product_service = ProductService(db)
    products, total_pages = product_service.get_products_paginated(
        category=category, 
        search=search, 
        page=page, 
        per_page=12
    )
    
    categories = product_service.get_categories()
    
    return templates.TemplateResponse("products.html", {
        "request": request,
        "products": products,
        "categories": categories,
        "current_category": category,
        "search_query": search,
        "current_page": page,
        "total_pages": total_pages,
        "page_title": "ASICS Shoes - All Products"
    })

@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: int, db: Session = Depends(get_db)):
    """Product detail page"""
    product_service = ProductService(db)
    product = product_service.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get related products
    related_products = product_service.get_related_products(product.category, product_id, limit=4)
    
    return templates.TemplateResponse("product_detail.html", {
        "request": request,
        "product": product,
        "related_products": related_products,
        "page_title": f"{product.name} - ASICS Shoe Store"
    })

@app.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request, db: Session = Depends(get_db)):
    """Shopping cart page"""
    # Get cart from session (simplified for demo)
    cart_service = CartService(db)
    cart_items = cart_service.get_session_cart(request)
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    return templates.TemplateResponse("cart.html", {
        "request": request,
        "cart_items": cart_items,
        "total": total,
        "page_title": "Shopping Cart - ASICS Shoe Store"
    })

@app.get("/checkout", response_class=HTMLResponse)
async def checkout_page(request: Request, db: Session = Depends(get_db)):
    """Checkout page"""
    cart_service = CartService(db)
    cart_items = cart_service.get_session_cart(request)
    
    if not cart_items:
        return RedirectResponse(url="/cart", status_code=302)
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "cart_items": cart_items,
        "total": total,
        "page_title": "Checkout - ASICS Shoe Store"
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "page_title": "Login - ASICS Shoe Store"
    })

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("register.html", {
        "request": request,
        "page_title": "Register - ASICS Shoe Store"
    })

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment"""
    return {"status": "healthy", "service": "ASICS Shoe Store"}

# Initialize sample data
@app.on_event("startup")
async def startup_event():
    """Initialize sample data on startup"""
    from services.business import init_sample_data
    db = next(get_db())
    init_sample_data(db)