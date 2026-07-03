"""
Cart Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CartItemInput(BaseModel):
    """Cart item input"""
    product_id: int
    quantity: int = Field(..., gt=0)

class CartItem(BaseModel):
    """Cart item"""
    product_id: int
    product_name: str
    quantity: int
    price_usd: float
    price_egp: float
    subtotal_usd: float
    subtotal_egp: float
    image_url: Optional[str]

class CartResponse(BaseModel):
    """Cart response"""
    id: int
    user_id: int
    items: List[CartItem]
    subtotal_usd: float
    subtotal_egp: float
    tax_amount: float
    shipping_cost: float
    discount_amount: float
    total_amount: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CartUpdateRequest(BaseModel):
    """Cart update request"""
    items: List[CartItemInput]
    discount_code: Optional[str] = None
