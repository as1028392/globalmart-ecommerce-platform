"""
Cart Service - Business logic for shopping cart
"""
from sqlalchemy.orm import Session
from typing import Optional
from app.models.cart import Cart
from app.models.product import Product
from app.schemas.cart import CartItemInput
from app.core.config import settings

class CartService:
    """Shopping cart service"""
    
    @staticmethod
    def get_or_create_cart(db: Session, user_id: int) -> Cart:
        """Get or create cart for user"""
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        
        if not cart:
            cart = Cart(user_id=user_id, items=[])
            db.add(cart)
            db.commit()
            db.refresh(cart)
        
        return cart
    
    @staticmethod
    def add_item_to_cart(db: Session, user_id: int, item: CartItemInput) -> Cart:
        """Add item to cart"""
        cart = CartService.get_or_create_cart(db, user_id)
        
        # Get product
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise ValueError(f"Product {item.product_id} not found")
        
        # Convert items from JSON to list
        items = cart.items or []
        
        # Check if product already in cart
        existing_item = next((i for i in items if i["product_id"] == item.product_id), None)
        
        if existing_item:
            existing_item["quantity"] += item.quantity
        else:
            items.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price_usd": product.price_usd,
                "price_egp": product.price_egp
            })
        
        cart.items = items
        CartService._calculate_cart_totals(cart)
        
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart
    
    @staticmethod
    def remove_item_from_cart(db: Session, user_id: int, product_id: int) -> Cart:
        """Remove item from cart"""
        cart = CartService.get_or_create_cart(db, user_id)
        
        items = cart.items or []
        cart.items = [i for i in items if i["product_id"] != product_id]
        
        CartService._calculate_cart_totals(cart)
        
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart
    
    @staticmethod
    def update_item_quantity(db: Session, user_id: int, product_id: int, quantity: int) -> Cart:
        """Update item quantity"""
        cart = CartService.get_or_create_cart(db, user_id)
        
        items = cart.items or []
        for item in items:
            if item["product_id"] == product_id:
                if quantity <= 0:
                    items.remove(item)
                else:
                    item["quantity"] = quantity
                break
        
        cart.items = items
        CartService._calculate_cart_totals(cart)
        
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart
    
    @staticmethod
    def clear_cart(db: Session, user_id: int) -> Cart:
        """Clear cart"""
        cart = CartService.get_or_create_cart(db, user_id)
        cart.items = []
        CartService._calculate_cart_totals(cart)
        
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart
    
    @staticmethod
    def _calculate_cart_totals(cart: Cart):
        """Calculate cart totals"""
        items = cart.items or []
        
        subtotal_usd = sum(item["price_usd"] * item["quantity"] for item in items)
        subtotal_egp = sum(item["price_egp"] * item["quantity"] for item in items)
        
        # Calculate tax (14% in Egypt)
        tax_amount = subtotal_egp * 0.14
        
        # Add platform fee
        platform_fee = subtotal_usd * (settings.PLATFORM_FEE_PERCENTAGE / 100)
        
        cart.subtotal_usd = subtotal_usd
        cart.subtotal_egp = subtotal_egp
        cart.tax_amount = tax_amount
        cart.shipping_cost = 0  # Will be set based on address
        cart.discount_amount = 0  # Will be set with discount code
        cart.total_amount = subtotal_egp + tax_amount + platform_fee
