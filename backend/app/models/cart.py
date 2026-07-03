"""
Cart Model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User")
    
    # Cart data
    items = Column(JSON, default=[])  # [{product_id, quantity, price}]
    
    # Totals
    subtotal_usd = Column(Float, default=0)
    subtotal_egp = Column(Float, default=0)
    tax_amount = Column(Float, default=0)
    shipping_cost = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    total_amount = Column(Float, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
