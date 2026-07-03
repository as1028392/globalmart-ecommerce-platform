"""
Product Service - Business logic for products
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import and_, or_
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.config import settings

class ProductService:
    """Product management service"""
    
    @staticmethod
    def create_product(db: Session, product_data: ProductCreate) -> Product:
        """Create new product"""
        # Calculate EGP price
        price_egp = product_data.price_usd * settings.USD_TO_EGP_RATE
        
        product = Product(
            name=product_data.name,
            name_ar=product_data.name_ar,
            slug=product_data.slug,
            description=product_data.description,
            description_ar=product_data.description_ar,
            category_id=product_data.category_id,
            price_usd=product_data.price_usd,
            price_egp=price_egp,
            discount_percentage=product_data.discount_percentage,
            stock_quantity=product_data.stock_quantity,
            sku=product_data.sku,
            barcode=product_data.barcode,
            image_url=product_data.image_url,
            images=product_data.images,
            video_url=product_data.video_url,
            specifications=product_data.specifications,
            source=product_data.source,
            source_product_id=product_data.source_product_id,
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return db.query(Product).filter(Product.id == product_id).first()
    
    @staticmethod
    def get_product_by_slug(db: Session, slug: str) -> Optional[Product]:
        """Get product by slug"""
        return db.query(Product).filter(Product.slug == slug).first()
    
    @staticmethod
    def get_products(
        db: Session,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at"
    ) -> tuple[List[Product], int]:
        """Get products with filters"""
        query = db.query(Product).filter(Product.is_active == True)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        
        # Count total
        total = query.count()
        
        # Sort
        if sort_by == "price_asc":
            query = query.order_by(Product.price_egp.asc())
        elif sort_by == "price_desc":
            query = query.order_by(Product.price_egp.desc())
        elif sort_by == "rating":
            query = query.order_by(Product.rating.desc())
        else:
            query = query.order_by(Product.created_at.desc())
        
        products = query.offset(skip).limit(limit).all()
        return products, total
    
    @staticmethod
    def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Update product"""
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return None
        
        update_dict = product_data.model_dump(exclude_unset=True)
        
        # Recalculate EGP price if USD price changed
        if "price_usd" in update_dict:
            update_dict["price_egp"] = update_dict["price_usd"] * settings.USD_TO_EGP_RATE
        
        for field, value in update_dict.items():
            setattr(product, field, value)
        
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """Delete product"""
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return False
        
        db.delete(product)
        db.commit()
        return True
    
    @staticmethod
    def update_product_stock(db: Session, product_id: int, quantity: int) -> Optional[Product]:
        """Update product stock quantity"""
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return None
        
        product.stock_quantity = quantity
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def get_featured_products(db: Session, limit: int = 10) -> List[Product]:
        """Get featured products"""
        return db.query(Product).filter(
            and_(
                Product.is_active == True,
                Product.is_featured == True
            )
        ).limit(limit).all()
