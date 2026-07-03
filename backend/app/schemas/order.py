"""
Order Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AddressSchema(BaseModel):
    """Address schema"""
    full_name: str
    phone: str
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool = False

class OrderItemSchema(BaseModel):
    """Order item schema"""
    product_id: int
    product_name: str
    quantity: int
    price_usd: float
    price_egp: float
    total_price_usd: float
    total_price_egp: float
    image_url: Optional[str]

class OrderCreate(BaseModel):
    """Order creation schema"""
    items: List[OrderItemSchema]
    shipping_address: AddressSchema
    billing_address: Optional[AddressSchema] = None
    shipping_method: str = "bosta"  # bosta, aramex
    payment_method: str = "paymob"  # paymob, fawry
    notes: Optional[str] = None
    discount_code: Optional[str] = None

class OrderResponse(BaseModel):
    """Order response"""
    id: int
    order_number: str
    user_id: int
    items: List[OrderItemSchema]
    shipping_address: dict
    billing_address: Optional[dict]
    subtotal_usd: float
    subtotal_egp: float
    tax_amount: float
    shipping_cost: float
    discount_amount: float
    total_amount: float
    payment_method: str
    payment_status: str
    shipping_method: str
    tracking_number: Optional[str]
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    """Order list response"""
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class OrderUpdateStatus(BaseModel):
    """Order status update"""
    status: str
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
