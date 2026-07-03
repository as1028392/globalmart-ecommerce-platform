"""
Review Model
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    product = relationship("Product", back_populates="reviews")
    
    # User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User")
    
    # Review content
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Float, nullable=False)  # 1-5
    
    # Verification
    is_verified_purchase = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    unhelpful_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
