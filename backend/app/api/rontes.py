"""
FastAPI Routers - Complete REST API
Product browsing, cart, checkout, orders, tracking
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import random
import string

from app.models import get_db, Product, CartItem, Order, User, OrderStatus
from app.services.pricing import pricing_engine, PriceBreakdown
from app.integrations.suppliers import ProductSyncService
from app.integrations.payments import PaymentService
from app.integrations.shipping import ShippingService
from app.integrations.notifications import NotificationService

router = APIRouter(prefix="/api/v1")
security = HTTPBearer()

# ==================== PRODUCTS ====================

@router.get("/products")
async def list_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = True,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List products with dynamic EGP pricing
    Returns products with real-time calculated prices
    """
    query = db.query(Product).filter(Product.is_active == True)

    if category:
        query = query.filter(Product.category == category)

    if search:
        query = query.filter(
            Product.title.ilike(f"%{search}%") | 
            Product.title_ar.ilike(f"%{search}%")
        )

    if in_stock:
        query = query.filter(Product.stock_quantity > 0)

    # Pagination
    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    # Calculate dynamic prices for each product
    results = []
    for product in products:
        price_breakdown = pricing_engine.calculate_price(product)
        results.append({
            "id": product.id,
            "title": product.title,
            "title_ar": product.title_ar,
            "category": product.category,
            "images": product.images[:3] if product.images else [],
            "price": price_breakdown.to_dict(),
            "stock": product.stock_quantity,
            "variants": product.variants,
            "supplier": product.supplier.name
        })

    return {
        "products": results,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@router.get("/products/{product_id}")
async def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    """Get single product with full pricing breakdown"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Real-time stock verification
    sync_service = ProductSyncService()
    is_available = sync_service.real_time_stock_check(product_id)

    price_breakdown = pricing_engine.calculate_price(product)

    return {
        "id": product.id,
        "title": product.title,
        "title_ar": product.title_ar,
        "description": product.description,
        "images": product.images,
        "category": product.category,
        "subcategory": product.subcategory,
        "price": price_breakdown.to_dict(),
        "stock": {
            "quantity": product.stock_quantity,
            "status": "available" if is_available else "unavailable",
            "last_updated": product.last_stock_update
        },
        "variants": product.variants,
        "supplier": {
            "name": product.supplier.name,
            "type": product.supplier.supplier_type
        },
        "supplier_url": product.supplier_url
    }

# ==================== CART ====================

@router.post("/cart/add")
async def add_to_cart(
    product_id: int,
    quantity: int = 1,
    variant: Optional[dict] = None,
    user_id: int = 1,  # In production, get from JWT token
    db: Session = Depends(get_db)
):
    """Add item to cart with price calculation"""
    product = db.query(Product).get(product_id)
    if not product or product.stock_quantity < quantity:
        raise HTTPException(status_code=400, detail="Product unavailable")

    # Check if already in cart
    existing = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.product_id == product_id
    ).first()

    if existing:
        existing.quantity += quantity
        existing.selected_variant = variant
    else:
        cart_item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            selected_variant=variant
        )
        db.add(cart_item)

    db.commit()

    # Return updated cart
    return await get_cart(user_id, db)

@router.get("/cart")
async def get_cart(user_id: int = 1, db: Session = Depends(get_db)):
    """Get cart with dynamic pricing for all items"""
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()

    if not cart_items:
        return {"items": [], "totals": {"egp": 0, "usd": 0}, "item_count": 0}

    # Prepare items for pricing engine
    items_for_calculation = []
    for item in cart_items:
        items_for_calculation.append({
            "product": item.product,
            "quantity": item.quantity
        })

    cart_calculation = pricing_engine.calculate_cart_total(items_for_calculation)

    return cart_calculation

@router.delete("/cart/{item_id}")
async def remove_from_cart(item_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """Remove item from cart"""
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == user_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()

    return await get_cart(user_id, db)

# ==================== CHECKOUT ====================

@router.post("/checkout")
async def create_checkout(
    payment_method: str,  # vodafone_cash, meeza, visa
    shipping_address: dict,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """
    Create order and initialize payment
    """
    # Get cart
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Verify stock availability
    sync_service = ProductSyncService()
    for item in cart_items:
        if not sync_service.real_time_stock_check(item.product_id):
            raise HTTPException(
                status_code=400, 
                detail=f"Product '{item.product.title}' is no longer available"
            )

    # Calculate totals
    items_for_calculation = [
        {"product": item.product, "quantity": item.quantity}
        for item in cart_items
    ]
    cart_calculation = pricing_engine.calculate_cart_total(items_for_calculation)

    # Generate order number
    order_number = f"GM-{datetime.utcnow().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"

    # Create order
    first_item = cart_items[0].product
    order = Order(
        order_number=order_number,
        user_id=user_id,
        subtotal_usd=sum(item["breakdown"]["product_price"]["usd"] for item in cart_calculation["items"]),
        shipping_cost_usd=sum(item["breakdown"]["international_shipping"]["usd"] for item in cart_calculation["items"]),
        custom_duties_usd=sum(item["breakdown"]["custom_duties"]["usd"] for item in cart_calculation["items"]),
        platform_margin_usd=sum(item["breakdown"]["platform_margin"]["usd"] for item in cart_calculation["items"]),
        total_usd=cart_calculation["cart_totals"]["usd"],
        total_egp=cart_calculation["cart_totals"]["egp"],
        currency_rate_applied=cart_calculation["items"][0]["breakdown"]["currency_rate"],
        payment_method=payment_method,
        shipping_address=json.dumps(shipping_address),
        order_items=[{
            "product_id": item.product_id,
            "title": item.product.title,
            "quantity": item.quantity,
            "price_usd": item.product.supplier_price_usd,
            "variant": item.selected_variant
        } for item in cart_items]
    )

    db.add(order)
    db.commit()

    # Initialize payment
    user = db.query(User).get(user_id)
    payment_result = PaymentService.process_payment(
        method=payment_method,
        amount_egp=order.total_egp,
        order_id=order_number,
        customer_data={
            "first_name": user.full_name.split()[0] if user.full_name else "Customer",
            "last_name": user.full_name.split()[-1] if user.full_name else "User",
            "email": user.email,
            "phone": user.phone,
            "address": shipping_address.get("street", ""),
            "city": shipping_address.get("city", "Cairo"),
            "governorate": shipping_address.get("governorate", "Cairo")
        }
    )

    # Update order with payment reference
    order.payment_transaction_id = payment_result.get("payment_token") or payment_result.get("reference_number")
    db.commit()

    # Clear cart
    for item in cart_items:
        db.delete(item)
    db.commit()

    return {
        "order": {
            "order_number": order.order_number,
            "total_egp": order.total_egp,
            "total_usd": order.total_usd,
            "status": order.status.value,
            "created_at": order.created_at
        },
        "payment": payment_result,
        "price_breakdown": cart_calculation
    }

# ==================== ORDERS & TRACKING ====================

@router.get("/orders")
async def list_orders(user_id: int = 1, db: Session = Depends(get_db)):
    """Get user's order history"""
    orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()

    return {
        "orders": [{
            "order_number": o.order_number,
            "total_egp": o.total_egp,
            "status": o.status.value,
            "payment_status": o.payment_status,
            "tracking_number": o.tracking_number,
            "tracking_url": o.tracking_url,
            "created_at": o.created_at,
            "item_count": len(o.order_items)
        } for o in orders]
    }

@router.get("/orders/{order_number}")
async def get_order_detail(order_number: str, db: Session = Depends(get_db)):
    """Get detailed order with tracking"""
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "order_number": order.order_number,
        "status": order.status.value,
        "payment": {
            "method": order.payment_method.value if order.payment_method else None,
            "status": order.payment_status,
            "transaction_id": order.payment_transaction_id
        },
        "pricing": {
            "subtotal_usd": order.subtotal_usd,
            "shipping_usd": order.shipping_cost_usd,
            "custom_duties_usd": order.custom_duties_usd,
            "platform_margin_usd": order.platform_margin_usd,
            "total_usd": order.total_usd,
            "total_egp": order.total_egp,
            "currency_rate": order.currency_rate_applied
        },
        "shipping": {
            "carrier": order.shipping_carrier,
            "tracking_number": order.tracking_number,
            "tracking_url": order.tracking_url,
            "estimated_delivery": order.estimated_delivery
        },
        "items": order.order_items,
        "created_at": order.created_at,
        "updated_at": order.updated_at
    }

@router.get("/track/{tracking_number}")
async def track_shipment(tracking_number: str, carrier: Optional[str] = None):
    """Track shipment across carriers"""
    # Auto-detect carrier if not provided
    if not carrier:
        if tracking_number.startswith("BOSTA"):
            carrier = "bosta"
        else:
            carrier = "aramex"

    provider = ShippingService.get_provider(carrier)
    tracking_info = provider.track_shipment(tracking_number)

    return {
        "tracking_number": tracking_number,
        "carrier": carrier,
        **tracking_info
    }

# ==================== ADMIN/SYNC ====================

@router.post("/admin/sync-products")
async def sync_products(background_tasks: BackgroundTasks):
    """Trigger product sync from all suppliers (admin only)"""
    sync_service = ProductSyncService()
    background_tasks.add_task(sync_service.sync_all_suppliers)

    return {"message": "Product sync started in background", "status": "processing"}

@router.get("/admin/currency-rate")
async def get_currency_rate():
    """Get current USD/EGP rate"""
    from app.services.pricing import CurrencyService
    rate = CurrencyService.get_current_rate()
    return {"usd_to_egp": rate, "updated_at": datetime.utcnow()}
