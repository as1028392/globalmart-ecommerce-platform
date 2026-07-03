"""
Order Model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from . import Base

class OrderStatus(str, PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User")
    
    # Order details
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    # Shipping address
    shipping_address = Column(JSON)
    billing_address = Column(JSON)
    
    # Pricing
    subtotal_usd = Column(Float, nullable=False)
    subtotal_egp = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0)
    shipping_cost = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    
    # Payment
    payment_method = Column(String(50))  # paymob, fawry, credit_card
    payment_status = Column(String(50), default="pending")  # pending, completed, failed
    transaction_id = Column(String(255), nullable=True)
    
    # Shipping
    shipping_method = Column(String(50))  # bosta, aramex, etc.
    tracking_number = Column(String(100), nullable=True, index=True)
    
    # Status
    status = Column(String(50), default=OrderStatus.PENDING)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Order
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order = relationship("Order", back_populates="items")
    
    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product = relationship("Product", back_populates="order_items")
    
    # Item details
    quantity = Column(Integer, nullable=False)
    price_usd = Column(Float, nullable=False)
    price_egp = Column(Float, nullable=False)
    total_price_usd = Column(Float, nullable=False)
    total_price_egp = Column(Float, nullable=False)
