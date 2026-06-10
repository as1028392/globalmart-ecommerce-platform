"""
Category Model - Product categorization
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    name_ar = Column(String(255), nullable=True)  # Arabic name
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(String(500))
    icon = Column(String(255))  # Icon URL
    
    # Hierarchy
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Display
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    products = relationship("Product", back_populates="category")
