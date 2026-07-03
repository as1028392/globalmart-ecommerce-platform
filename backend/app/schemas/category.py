"""
Category Schemas - Pydantic models for categories
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CategoryCreate(BaseModel):
    """Category creation schema"""
    name: str = Field(..., min_length=2, max_length=255, description="Category name")
    name_ar: Optional[str] = Field(None, max_length=255, description="Arabic category name")
    slug: str = Field(..., min_length=2, max_length=255, description="URL slug")
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, description="Icon URL")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    order: int = Field(default=0, description="Display order")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Electronics",
                "name_ar": "الإلكترونيات",
                "slug": "electronics",
                "description": "Electronic products",
                "icon": "https://example.com/icons/electronics.png",
                "parent_id": None,
                "order": 1
            }
        }

class CategoryUpdate(BaseModel):
    """Category update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None)
    order: Optional[int] = Field(None)
    is_active: Optional[bool] = Field(None)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Electronics & Gadgets",
                "name_ar": "الإلكترونيات والأجهزة",
                "order": 2,
                "is_active": True
            }
        }

class CategoryResponse(BaseModel):
    """Category response schema"""
    id: int
    name: str
    name_ar: Optional[str]
    slug: str
    description: Optional[str]
    icon: Optional[str]
    parent_id: Optional[int]
    is_active: bool
    order: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Electronics",
                "name_ar": "الإلكترونيات",
                "slug": "electronics",
                "description": "Electronic products",
                "icon": "https://example.com/icons/electronics.png",
                "parent_id": None,
                "is_active": True,
                "order": 1,
                "created_at": "2026-06-10T16:00:00Z",
                "updated_at": "2026-06-10T16:00:00Z"
            }
        }

class CategoryWithSubcategories(CategoryResponse):
    """Category response with subcategories"""
    subcategories: List["CategoryResponse"] = Field(default=[], description="List of subcategories")
    
    class Config:
        from_attributes = True

# Update forward reference
CategoryWithSubcategories.model_rebuild()
