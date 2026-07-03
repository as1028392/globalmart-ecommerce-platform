"""
Order Service - Business logic for orders
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import random
import string
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate
from app.core.config import settings

class OrderService:
    """Order management service"""
    
    @staticmethod
    def generate_order_number() -> str:
        """Generate unique order number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"ORD-{timestamp}-{random_suffix}"
    
    @staticmethod
    def create_order(db: Session, user_id: int, order_data: OrderCreate) -> Order:
        """Create new order"""
        # Generate order number
        order_number = OrderService.generate_order_number()
        
        # Calculate totals
        subtotal_usd = 0
        subtotal_egp = 0
        
        for item in order_data.items:
            subtotal_usd += item.price_usd * item.quantity
            subtotal_egp += item.price_egp * item.quantity
        
        # Calculate tax and fees
        tax_amount = subtotal_egp * 0.14  # 14% VAT
        platform_fee = subtotal_usd * (settings.PLATFORM_FEE_PERCENTAGE / 100)
        shipping_cost = 50  # Default shipping cost in EGP
        
        total_amount = subtotal_egp + tax_amount + platform_fee + shipping_cost
        
        # Create order
        order = Order(
            order_number=order_number,
            user_id=user_id,
            shipping_address=order_data.shipping_address.model_dump(),
            billing_address=order_data.billing_address.model_dump() if order_data.billing_address else None,
            subtotal_usd=subtotal_usd,
            subtotal_egp=subtotal_egp,
            tax_amount=tax_amount,
            shipping_cost=shipping_cost,
            discount_amount=0,
            total_amount=total_amount,
            payment_method=order_data.payment_method,
            shipping_method=order_data.shipping_method,
            status=OrderStatus.PENDING,
            notes=order_data.notes
        )
        
        # Create order items
        for item_data in order_data.items:
            order_item = OrderItem(
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                price_usd=item_data.price_usd,
                price_egp=item_data.price_egp,
                total_price_usd=item_data.price_usd * item_data.quantity,
                total_price_egp=item_data.price_egp * item_data.quantity
            )
            order.items.append(order_item)
            
            # Update product stock
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if product:
                product.stock_quantity -= item_data.quantity
        
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        return db.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def get_order_by_number(db: Session, order_number: str) -> Optional[Order]:
        """Get order by order number"""
        return db.query(Order).filter(Order.order_number == order_number).first()
    
    @staticmethod
    def get_user_orders(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> tuple[List[Order], int]:
        """Get user orders"""
        query = db.query(Order).filter(Order.user_id == user_id)
        total = query.count()
        orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        return orders, total
    
    @staticmethod
    def update_order_status(db: Session, order_id: int, status: str, tracking_number: Optional[str] = None) -> Optional[Order]:
        """Update order status"""
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return None
        
        order.status = status
        
        if tracking_number:
            order.tracking_number = tracking_number
        
        if status == OrderStatus.SHIPPED:
            order.shipped_at = datetime.utcnow()
        elif status == OrderStatus.DELIVERED:
            order.delivered_at = datetime.utcnow()
        
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def cancel_order(db: Session, order_id: int) -> Optional[Order]:
        """Cancel order"""
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return None
        
        # Restore product stock
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock_quantity += item.quantity
        
        order.status = OrderStatus.CANCELLED
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def get_orders_by_status(db: Session, status: str, skip: int = 0, limit: int = 20) -> tuple[List[Order], int]:
        """Get orders by status"""
        query = db.query(Order).filter(Order.status == status)
        total = query.count()
        orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        return orders, total
