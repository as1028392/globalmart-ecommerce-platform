"""
Product Model
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False, index=True)
    name_ar = Column(String(255), nullable=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text)
    description_ar = Column(Text, nullable=True)
    
    # Category
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    category = relationship("Category", back_populates="products")
    
    # Pricing
    price_usd = Column(Float, nullable=False)  # Original price in USD
    price_egp = Column(Float, nullable=False)  # Converted price in EGP
    cost_price = Column(Float, nullable=True)  # Cost for profit calculation
    discount_percentage = Column(Float, default=0)  # Discount %
    
    # Inventory
    stock_quantity = Column(Integer, default=0)
    sku = Column(String(100), unique=True, nullable=False)
    barcode = Column(String(100), unique=True, nullable=True)
    
    # Media
    image_url = Column(String(500), nullable=True)
    images = Column(JSON, default=[])  # Array of image URLs
    video_url = Column(String(500), nullable=True)
    
    # Specifications
    specifications = Column(JSON, default={})  # Product specs
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    rating = Column(Float, default=0)  # Average rating
    review_count = Column(Integer, default=0)
    
    # Source
    source = Column(String(50))  # aliexpress, local, etc.
    source_product_id = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
