"""
Supplier API Integration Hub
Handles real-time product sync from global markets
"""
import requests
import hashlib
import time
import json
from typing import List, Dict, Optional
from datetime import datetime
from app.core.config import settings
from app.models import Product, Supplier, SessionLocal

class BaseSupplierAPI:
    """Abstract base class for supplier integrations"""

    def __init__(self, supplier: Supplier):
        self.supplier = supplier
        self.session = requests.Session()

    def authenticate(self) -> Dict:
        """Override in subclass"""
        raise NotImplementedError

    def fetch_products(self, page: int = 1, limit: int = 50) -> List[Dict]:
        """Override in subclass"""
        raise NotImplementedError

    def fetch_product_details(self, external_id: str) -> Dict:
        """Override in subclass"""
        raise NotImplementedError

    def check_stock(self, external_id: str) -> int:
        """Override in subclass"""
        raise NotImplementedError

class AliExpressAPI(BaseSupplierAPI):
    """
    AliExpress Open Platform API Integration
    Documentation: https://open.aliexpress.com/
    """

    BASE_URL = "https://api-sg.aliexpress.com/sync"

    def __init__(self, supplier: Supplier):
        super().__init__(supplier)
        self.app_key = settings.ALIEXPRESS_APP_KEY
        self.app_secret = settings.ALIEXPRESS_APP_SECRET

    def _sign_request(self, params: Dict) -> str:
        """Generate API signature using HMAC-SHA256"""
        import hmac

        sorted_params = sorted(params.items())
        query_string = "".join([f"{k}{v}" for k, v in sorted_params])

        sign = hmac.new(
            self.app_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest().upper()

        return sign

    def authenticate(self) -> Dict:
        """Get access token (simplified - implement OAuth flow)"""
        return {"access_token": "token_placeholder"}

    def fetch_products(self, category_id: Optional[str] = None, page: int = 1) -> List[Dict]:
        """
        Fetch products from AliExpress
        Maps to our Product model structure
        """
        params = {
            "app_key": self.app_key,
            "timestamp": str(int(time.time() * 1000)),
            "method": "aliexpress.ds.product.get",
            "category_id": category_id or "",
            "page_no": str(page),
            "page_size": "50"
        }

        params["sign"] = self._sign_request(params)

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            data = response.json()

            if data.get("success"):
                products = []
                for item in data.get("result", {}).get("products", []):
                    products.append({
                        "external_id": str(item["productId"]),
                        "title": item["productTitle"],
                        "title_ar": "",  # Will be translated if needed
                        "description": item.get("productDescription", ""),
                        "supplier_price_usd": float(item["targetSalePrice"]),
                        "weight_kg": self._estimate_weight(item),
                        "category": item.get("categoryId", "general"),
                        "images": [img["url"] for img in item.get("productImages", [])[:5]],
                        "stock_quantity": item.get("availableStock", 0),
                        "variants": self._parse_variants(item),
                        "supplier_url": item.get("productDetailUrl", "")
                    })
                return products
        except Exception as e:
            print(f"AliExpress API Error: {e}")

        return []

    def _estimate_weight(self, item: Dict) -> float:
        """Estimate weight from category if not provided"""
        category_weights = {
            "clothing": 0.3,
            "electronics": 0.8,
            "beauty": 0.2,
            "home": 1.5
        }
        return category_weights.get(item.get("categoryId"), 0.5)

    def _parse_variants(self, item: Dict) -> List[Dict]:
        """Parse color/size variants"""
        variants = []
        if "skuInfos" in item:
            for sku in item["skuInfos"]:
                variants.append({
                    "sku_id": sku["skuId"],
                    "price": sku.get("skuPrice", 0),
                    "stock": sku.get("skuStock", 0),
                    "attributes": sku.get("skuAttributes", {})
                })
        return variants

    def check_stock(self, external_id: str) -> int:
        """Real-time stock check"""
        product = self.fetch_product_details(external_id)
        return product.get("stock_quantity", 0)

class TurkishTextileAPI(BaseSupplierAPI):
    """
    Custom API integration for Turkish textile factories
    Typically uses REST/JSON or EDI formats
    """

    def __init__(self, supplier: Supplier):
        super().__init__(supplier)
        self.base_url = supplier.api_endpoint

    def authenticate(self) -> Dict:
        """API Key authentication"""
        return {"Authorization": f"Bearer {self.supplier.api_key_encrypted}"}

    def fetch_products(self, page: int = 1) -> List[Dict]:
        """Fetch textile products"""
        headers = self.authenticate()

        try:
            response = self.session.get(
                f"{self.base_url}/products",
                headers=headers,
                params={"page": page, "limit": 50},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return [self._map_product(p) for p in data.get("products", [])]
        except Exception as e:
            print(f"Turkish API Error: {e}")

        return []

    def _map_product(self, raw: Dict) -> Dict:
        """Map Turkish API format to our standard"""
        return {
            "external_id": str(raw["id"]),
            "title": raw["name_en"],
            "title_ar": raw.get("name_ar", ""),
            "description": raw.get("description_en", ""),
            "supplier_price_usd": float(raw["price_usd"]),
            "weight_kg": float(raw.get("weight_kg", 0.3)),
            "category": "textile",
            "subcategory": raw.get("type", "general"),
            "images": raw.get("images", []),
            "stock_quantity": raw.get("stock", 0),
            "variants": raw.get("sizes", []),
            "supplier_url": raw.get("catalog_url", "")
        }

class KoreanBeautyAPI(BaseSupplierAPI):
    """
    Korean beauty platform integration
    (Olive Young, StyleKorean, etc.)
    """

    def __init__(self, supplier: Supplier):
        super().__init__(supplier)
        self.base_url = supplier.api_endpoint or "https://api.stylekorean.com/v1"

    def authenticate(self) -> Dict:
        return {
            "X-API-Key": self.supplier.api_key_encrypted,
            "X-API-Secret": settings.ALIEXPRESS_APP_SECRET  # Reuse or separate
        }

    def fetch_products(self, page: int = 1) -> List[Dict]:
        headers = self.authenticate()

        try:
            response = self.session.get(
                f"{self.base_url}/products",
                headers=headers,
                params={"page": page, "per_page": 50},
                timeout=30
            )

            if response.status_code == 200:
                return [self._map_product(p) for p in response.json().get("data", [])]
        except Exception as e:
            print(f"Korean API Error: {e}")

        return []

    def _map_product(self, raw: Dict) -> Dict:
        return {
            "external_id": str(raw["product_code"]),
            "title": raw["name"],
            "title_ar": "",  # Korean beauty rarely has Arabic
            "description": raw.get("description", ""),
            "supplier_price_usd": float(raw["sale_price"]),
            "weight_kg": float(raw.get("shipping_weight", 0.2)),
            "category": "beauty",
            "subcategory": raw.get("category", "skincare"),
            "images": raw.get("thumbnail_images", []),
            "stock_quantity": raw.get("quantity", 0),
            "variants": raw.get("options", []),
            "supplier_url": raw.get("product_url", "")
        }

class ProductSyncService:
    """
    Central service for syncing products from all suppliers
    Runs on scheduled intervals (every 30 minutes)
    """

    SUPPLIER_API_MAP = {
        "aliexpress": AliExpressAPI,
        "turkish_textile": TurkishTextileAPI,
        "korean_beauty": KoreanBeautyAPI
    }

    def __init__(self):
        self.db = SessionLocal()

    def sync_all_suppliers(self):
        """Sync products from all active suppliers"""
        suppliers = self.db.query(Supplier).filter(Supplier.is_active == True).all()

        for supplier in suppliers:
            try:
                self.sync_supplier(supplier)
            except Exception as e:
                print(f"Sync failed for {supplier.name}: {e}")

    def sync_supplier(self, supplier: Supplier):
        """Sync single supplier"""
        api_class = self.SUPPLIER_API_MAP.get(supplier.supplier_type)
        if not api_class:
            print(f"Unknown supplier type: {supplier.supplier_type}")
            return

        api = api_class(supplier)
        page = 1
        total_synced = 0

        while True:
            products = api.fetch_products(page=page)
            if not products:
                break

            for product_data in products:
                self._upsert_product(supplier.id, product_data)
                total_synced += 1

            page += 1
            if page > 10:  # Safety limit
                break

        supplier.last_sync = datetime.utcnow()
        self.db.commit()

        print(f"Synced {total_synced} products from {supplier.name}")

    def _upsert_product(self, supplier_id: int, data: Dict):
        """Insert or update product"""
        existing = self.db.query(Product).filter(
            Product.supplier_id == supplier_id,
            Product.external_id == data["external_id"]
        ).first()

        if existing:
            # Update existing
            existing.title = data["title"]
            existing.supplier_price_usd = data["supplier_price_usd"]
            existing.stock_quantity = data["stock_quantity"]
            existing.stock_status = "in_stock" if data["stock_quantity"] > 0 else "out_of_stock"
            existing.last_stock_update = datetime.utcnow()
            existing.images = data["images"]
            existing.variants = data["variants"]
        else:
            # Create new
            product = Product(
                supplier_id=supplier_id,
                **data
            )
            self.db.add(product)

        self.db.commit()

    def real_time_stock_check(self, product_id: int) -> bool:
        """Check if product is available before order"""
        product = self.db.query(Product).get(product_id)
        if not product:
            return False

        supplier = product.supplier
        api_class = self.SUPPLIER_API_MAP.get(supplier.supplier_type)

        if api_class:
            api = api_class(supplier)
            current_stock = api.check_stock(product.external_id)

            # Update local cache
            product.stock_quantity = current_stock
            product.stock_status = "in_stock" if current_stock > 0 else "out_of_stock"
            product.last_stock_update = datetime.utcnow()
            self.db.commit()

            return current_stock > 0

        return product.stock_quantity > 0
