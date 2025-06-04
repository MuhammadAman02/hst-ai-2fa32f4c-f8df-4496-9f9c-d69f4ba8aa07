from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from core.database import get_db
from services.business import CartService
from fastapi import Request

router = APIRouter()

@router.post("/add")
async def add_to_cart(
    request: Request,
    product_id: int = Form(...),
    quantity: int = Form(1),
    db: Session = Depends(get_db)
):
    """Add item to cart"""
    cart_service = CartService(db)
    success = cart_service.add_to_cart(request, product_id, quantity)
    
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Item added to cart", "success": True}

@router.delete("/remove/{product_id}")
async def remove_from_cart(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    cart_service = CartService(db)
    cart_service.remove_from_cart(request, product_id)
    return {"message": "Item removed from cart", "success": True}

@router.delete("/clear")
async def clear_cart(
    request: Request,
    db: Session = Depends(get_db)
):
    """Clear all items from cart"""
    cart_service = CartService(db)
    cart_service.clear_cart(request)
    return {"message": "Cart cleared", "success": True}