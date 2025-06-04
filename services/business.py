from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Tuple
from models.schemas import Product, User, Order, OrderItem, ProductCreate
from core.utils import generate_order_number
import math

class ProductService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_products_paginated(
        self, 
        category: Optional[str] = None, 
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 12
    ) -> Tuple[List[Product], int]:
        """Get paginated products with optional filtering"""
        query = self.db.query(Product).filter(Product.is_active == True)
        
        if category:
            query = query.filter(Product.category == category)
        
        if search:
            query = query.filter(
                or_(
                    Product.name.contains(search),
                    Product.description.contains(search)
                )
            )
        
        total_count = query.count()
        total_pages = math.ceil(total_count / per_page)
        
        products = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return products, total_pages
    
    def get_featured_products(self, limit: int = 8) -> List[Product]:
        """Get featured products"""
        return self.db.query(Product).filter(
            and_(Product.is_featured == True, Product.is_active == True)
        ).limit(limit).all()
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return self.db.query(Product).filter(
            and_(Product.id == product_id, Product.is_active == True)
        ).first()
    
    def get_related_products(self, category: str, exclude_id: int, limit: int = 4) -> List[Product]:
        """Get related products by category"""
        return self.db.query(Product).filter(
            and_(
                Product.category == category,
                Product.id != exclude_id,
                Product.is_active == True
            )
        ).limit(limit).all()
    
    def get_categories(self) -> List[str]:
        """Get all product categories"""
        categories = self.db.query(Product.category).filter(
            Product.is_active == True
        ).distinct().all()
        return [cat[0] for cat in categories]
    
    def create_product(self, product_data: ProductCreate) -> Product:
        """Create new product"""
        product = Product(**product_data.dict())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def update_product(self, product_id: int, product_data: dict) -> Optional[Product]:
        """Update product"""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product:
            for key, value in product_data.items():
                setattr(product, key, value)
            self.db.commit()
            self.db.refresh(product)
        return product

class CartService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_session_cart(self, request) -> List[dict]:
        """Get cart items from session (simplified for demo)"""
        # In a real app, you'd use proper session management
        # For demo purposes, returning empty cart
        return []
    
    def add_to_cart(self, request, product_id: int, quantity: int = 1):
        """Add item to cart"""
        # Simplified cart management for demo
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
        
        # In a real app, you'd store this in session or database
        return True
    
    def remove_from_cart(self, request, product_id: int):
        """Remove item from cart"""
        # Simplified for demo
        return True
    
    def clear_cart(self, request):
        """Clear all items from cart"""
        # Simplified for demo
        return True

class OrderService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_order(self, user_id: int, cart_items: List[dict], order_data: dict) -> Order:
        """Create new order"""
        total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
        
        order = Order(
            order_number=generate_order_number(),
            user_id=user_id,
            total_amount=total_amount,
            shipping_address=order_data['shipping_address'],
            billing_address=order_data['billing_address'],
            payment_method=order_data['payment_method']
        )
        
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        # Add order items
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=item['price']
            )
            self.db.add(order_item)
        
        self.db.commit()
        return order
    
    def get_user_orders(self, user_id: int) -> List[Order]:
        """Get all orders for a user"""
        return self.db.query(Order).filter(Order.user_id == user_id).all()
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        return self.db.query(Order).filter(Order.id == order_id).first()

def init_sample_data(db: Session):
    """Initialize sample data"""
    # Check if data already exists
    if db.query(Product).first():
        return
    
    # Sample ASICS products
    sample_products = [
        {
            "name": "ASICS GEL-KAYANO 30",
            "description": "Premium stability running shoe with advanced cushioning technology",
            "price": 159.99,
            "category": "Running",
            "size": "US 9",
            "color": "Black/White",
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop",
            "stock_quantity": 25,
            "is_featured": True
        },
        {
            "name": "ASICS GEL-NIMBUS 25",
            "description": "Maximum cushioning for long-distance running comfort",
            "price": 149.99,
            "category": "Running",
            "size": "US 10",
            "color": "Blue/Silver",
            "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop",
            "stock_quantity": 30,
            "is_featured": True
        },
        {
            "name": "ASICS GEL-CUMULUS 25",
            "description": "Versatile daily trainer with responsive cushioning",
            "price": 129.99,
            "category": "Running",
            "size": "US 8.5",
            "color": "Gray/Orange",
            "image_url": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop",
            "stock_quantity": 20,
            "is_featured": True
        },
        {
            "name": "ASICS COURT FF 3",
            "description": "Professional tennis shoe with superior court grip",
            "price": 139.99,
            "category": "Tennis",
            "size": "US 9.5",
            "color": "White/Navy",
            "image_url": "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=400&h=400&fit=crop",
            "stock_quantity": 15,
            "is_featured": False
        },
        {
            "name": "ASICS GEL-RESOLUTION 9",
            "description": "Durable tennis shoe built for aggressive players",
            "price": 149.99,
            "category": "Tennis",
            "size": "US 10.5",
            "color": "Black/Red",
            "image_url": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&h=400&fit=crop",
            "stock_quantity": 18,
            "is_featured": False
        },
        {
            "name": "ASICS METARISE",
            "description": "High-performance volleyball shoe with exceptional jump support",
            "price": 119.99,
            "category": "Volleyball",
            "size": "US 9",
            "color": "White/Blue",
            "image_url": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=400&h=400&fit=crop",
            "stock_quantity": 12,
            "is_featured": False
        },
        {
            "name": "ASICS UPCOURT 5",
            "description": "Affordable indoor court shoe for multiple sports",
            "price": 79.99,
            "category": "Volleyball",
            "size": "US 8",
            "color": "Black/White",
            "image_url": "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=400&h=400&fit=crop",
            "stock_quantity": 22,
            "is_featured": False
        },
        {
            "name": "ASICS NOVABLAST 4",
            "description": "Energy-returning running shoe for dynamic workouts",
            "price": 139.99,
            "category": "Running",
            "size": "US 11",
            "color": "Green/Black",
            "image_url": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&h=400&fit=crop",
            "stock_quantity": 16,
            "is_featured": True
        }
    ]
    
    for product_data in sample_products:
        product = Product(**product_data)
        db.add(product)
    
    # Create admin user
    from core.security import get_password_hash
    admin_user = User(
        email="admin@asicsstore.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        full_name="Store Administrator",
        is_admin=True
    )
    db.add(admin_user)
    
    db.commit()