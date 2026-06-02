"""
Database Models for GlobalMart Platform
PostgreSQL with encrypted sensitive fields
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
from app.core.config import settings, encrypt_data, decrypt_data

Base = declarative_base()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    IN_CUSTOMS = "in_customs"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentMethod(enum.Enum):
    VODAFONE_CASH = "vodafone_cash"
    MEEZA = "meeza"
    VISA = "visa"
    PAYMOB = "paymob"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    _phone_encrypted = Column("phone_encrypted", String(500))
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # Encrypted address data
    _address_encrypted = Column("address_encrypted", Text)
    _id_number_encrypted = Column("id_number_encrypted", String(500))  # For customs

    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")

    @property
    def address(self):
        return decrypt_data(self._address_encrypted) if self._address_encrypted else None

    @address.setter
    def address(self, value):
        self._address_encrypted = encrypt_data(value) if value else None

    @property
    def id_number(self):
        return decrypt_data(self._id_number_encrypted) if self._id_number_encrypted else None

    @id_number.setter
    def id_number(self, value):
        self._id_number_encrypted = encrypt_data(value) if value else None

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # e.g., "AliExpress", "Turkish Factory A"
    api_endpoint = Column(String(500))
    api_key_encrypted = Column(String(500))
    supplier_type = Column(String(50))  # "aliexpress", "custom_api", "manual"
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    sync_interval_minutes = Column(Integer, default=30)

    products = relationship("Product", back_populates="supplier")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    external_id = Column(String(255), nullable=False)  # ID from supplier API
    title = Column(String(500), nullable=False)
    description = Column(Text)
    title_ar = Column(String(500))  # Arabic title for local market

    # Pricing (stored in USD from supplier)
    supplier_price_usd = Column(Float, nullable=False)
    weight_kg = Column(Float, default=0.5)

    # Categorization
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    tags = Column(JSON)

    # Media
    images = Column(JSON)  # Array of image URLs

    # Inventory
    stock_quantity = Column(Integer, default=0)
    stock_status = Column(String(20), default="in_stock")  # in_stock, low_stock, out_of_stock
    last_stock_update = Column(DateTime, default=datetime.utcnow)

    # Supplier metadata
    supplier_url = Column(String(1000))
    variants = Column(JSON)  # Color, size options from supplier

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = relationship("Supplier", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    selected_variant = Column(JSON)  # {"color": "red", "size": "XL"}
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Pricing breakdown (stored for audit/tranparency)
    subtotal_usd = Column(Float, nullable=False)
    shipping_cost_usd = Column(Float, nullable=False)
    custom_duties_usd = Column(Float, nullable=False)
    platform_margin_usd = Column(Float, nullable=False)
    total_usd = Column(Float, nullable=False)
    total_egp = Column(Float, nullable=False)
    currency_rate_applied = Column(Float, nullable=False)

    # Status tracking
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_method = Column(Enum(PaymentMethod))
    payment_status = Column(String(20), default="pending")  # pending, paid, failed, refunded
    payment_transaction_id = Column(String(255))

    # Shipping
    shipping_carrier = Column(String(50))  # "bosta", "aramex"
    tracking_number = Column(String(255))
    tracking_url = Column(String(500))
    estimated_delivery = Column(DateTime)

    # Encrypted shipping address
    _shipping_address_encrypted = Column("shipping_address_encrypted", Text)

    # Order items snapshot (in case product changes later)
    order_items = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="orders")

    @property
    def shipping_address(self):
        return decrypt_data(self._shipping_address_encrypted) if self._shipping_address_encrypted else None

    @shipping_address.setter
    def shipping_address(self, value):
        self._shipping_address_encrypted = encrypt_data(value) if value else None

class CurrencyRate(Base):
    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True, index=True)
    from_currency = Column(String(3), nullable=False)
    to_currency = Column(String(3), nullable=False)
    rate = Column(Float, nullable=False)
    source = Column(String(50))  # "central_bank", "api", "manual"
    updated_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=False)
    action = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE
    old_values = Column(JSON)
    new_values = Column(JSON)
    performed_by = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
