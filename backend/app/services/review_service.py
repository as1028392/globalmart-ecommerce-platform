"""
Review Service - Business logic for product reviews
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import func
from app.models.review import Review
from app.models.product import Product
from app.schemas.review import ReviewCreate, ReviewUpdate

class ReviewService:
    """Review management service"""
    
    @staticmethod
    def create_review(db: Session, user_id: int, review_data: ReviewCreate) -> Review:
        """Create new review"""
        review = Review(
            product_id=review_data.product_id,
            user_id=user_id,
            title=review_data.title,
            content=review_data.content,
            rating=review_data.rating
        )
        
        db.add(review)
        db.commit()
        db.refresh(review)
        
        # Update product rating
        ReviewService._update_product_rating(db, review_data.product_id)
        
        return review
    
    @staticmethod
    def get_review_by_id(db: Session, review_id: int) -> Optional[Review]:
        """Get review by ID"""
        return db.query(Review).filter(Review.id == review_id).first()
    
    @staticmethod
    def get_product_reviews(
        db: Session,
        product_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Review], int]:
        """Get product reviews"""
        query = db.query(Review).filter(Review.product_id == product_id)
        total = query.count()
        reviews = query.order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
        return reviews, total
    
    @staticmethod
    def update_review(db: Session, review_id: int, review_data: ReviewUpdate) -> Optional[Review]:
        """Update review"""
        review = db.query(Review).filter(Review.id == review_id).first()
        
        if not review:
            return None
        
        update_dict = review_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(review, field, value)
        
        db.add(review)
        db.commit()
        db.refresh(review)
        
        # Update product rating
        ReviewService._update_product_rating(db, review.product_id)
        
        return review
    
    @staticmethod
    def delete_review(db: Session, review_id: int) -> bool:
        """Delete review"""
        review = db.query(Review).filter(Review.id == review_id).first()
        
        if not review:
            return False
        
        product_id = review.product_id
        db.delete(review)
        db.commit()
        
        # Update product rating
        ReviewService._update_product_rating(db, product_id)
        
        return True
    
    @staticmethod
    def _update_product_rating(db: Session, product_id: int):
        """Update product average rating"""
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return
        
        # Calculate average rating
        avg_rating = db.query(func.avg(Review.rating)).filter(
            Review.product_id == product_id
        ).scalar() or 0
        
        # Count reviews
        review_count = db.query(func.count(Review.id)).filter(
            Review.product_id == product_id
        ).scalar() or 0
        
        product.rating = float(avg_rating)
        product.review_count = review_count
        
        db.add(product)
        db.commit()
    
    @staticmethod
    def mark_helpful(db: Session, review_id: int) -> Optional[Review]:
        """Mark review as helpful"""
        review = db.query(Review).filter(Review.id == review_id).first()
        
        if not review:
            return None
        
        review.helpful_count += 1
        db.add(review)
        db.commit()
        db.refresh(review)
        return review
    
    @staticmethod
    def mark_unhelpful(db: Session, review_id: int) -> Optional[Review]:
        """Mark review as unhelpful"""
        review = db.query(Review).filter(Review.id == review_id).first()
        
        if not review:
            return None
        
        review.unhelpful_count += 1
        db.add(review)
        db.commit()
        db.refresh(review)
        return review
