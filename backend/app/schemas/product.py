"""
Product Schemas - Pydantic models for products
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ProductCreate(BaseModel):
    """Product creation schema"""
    name: str = Field(..., min_length=3, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    slug: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    category_id: int
    price_usd: float = Field(..., gt=0)
    discount_percentage: float = Field(default=0, ge=0, le=100)
    stock_quantity: int = Field(default=0, ge=0)
    sku: str
    barcode: Optional[str] = None
    image_url: Optional[str] = None
    images: List[str] = Field(default=[])
    video_url: Optional[str] = None
    specifications: dict = Field(default={})
    source: str = "local"
    source_product_id: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "iPhone 15 Pro",
                "name_ar": "أيفون 15 برو",
                "slug": "iphone-15-pro",
                "description": "Latest iPhone model",
                "category_id": 1,
                "price_usd": 999,
                "discount_percentage": 10,
                "stock_quantity": 100,
                "sku": "IPHONE15PRO-001",
                "specifications": {"color": "black", "storage": "256GB"}
            }
        }

class ProductUpdate(BaseModel):
    """Product update schema"""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    price_usd: Optional[float] = Field(None, gt=0)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    stock_quantity: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    video_url: Optional[str] = None
    specifications: Optional[dict] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None

class ProductResponse(BaseModel):
    """Product response schema"""
    id: int
    name: str
    name_ar: Optional[str]
    slug: str
    description: Optional[str]
    description_ar: Optional[str]
    category_id: int
    price_usd: float
    price_egp: float
    discount_percentage: float
    stock_quantity: int
    sku: str
    barcode: Optional[str]
    image_url: Optional[str]
    images: List[str]
    video_url: Optional[str]
    specifications: dict
    is_active: bool
    is_featured: bool
    rating: float
    review_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    """Product list response with pagination"""
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
