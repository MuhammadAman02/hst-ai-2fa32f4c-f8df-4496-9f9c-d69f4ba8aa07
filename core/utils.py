import os
import uuid
from PIL import Image
from typing import Optional

def save_uploaded_image(file, upload_dir: str = "static/images/products") -> Optional[str]:
    """Save uploaded image and return filename"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ['jpg', 'jpeg', 'png', 'webp']:
            return None
            
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save and optimize image
        with Image.open(file.file) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            max_size = (800, 800)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save with optimization
            img.save(file_path, optimize=True, quality=85)
        
        return filename
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:.2f}"

def generate_order_number() -> str:
    """Generate unique order number"""
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"