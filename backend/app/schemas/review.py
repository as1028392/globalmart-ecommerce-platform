"""
Review Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewCreate(BaseModel):
    """Review creation schema"""
    product_id: int
    title: str = Field(..., min_length=3, max_length=255)
    content: str = Field(..., min_length=10)
    rating: float = Field(..., ge=1, le=5)

class ReviewUpdate(BaseModel):
    """Review update schema"""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    content: Optional[str] = Field(None, min_length=10)
    rating: Optional[float] = Field(None, ge=1, le=5)

class ReviewResponse(BaseModel):
    """Review response"""
    id: int
    product_id: int
    user_id: int
    user_name: str
    user_avatar: Optional[str]
    title: str
    content: str
    rating: float
    is_verified_purchase: bool
    helpful_count: int
    unhelpful_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ReviewListResponse(BaseModel):
    """Review list response"""
    items: List[ReviewResponse]
    total: int
    page: int
    page_size: int
    average_rating: float
