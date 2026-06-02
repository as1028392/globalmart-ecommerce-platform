"""
Dynamic Pricing Engine - Core Business Logic
Calculates real-time EGP prices with all cost components
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import requests
from app.core.config import settings
from app.models import CurrencyRate, Product

@dataclass
class PriceBreakdown:
    """Transparent price breakdown for customer trust"""
    product_price_usd: float
    currency_rate: float
    product_price_egp: float
    international_shipping_usd: float
    international_shipping_egp: float
    custom_duties_usd: float
    custom_duties_egp: float
    platform_margin_usd: float
    platform_margin_egp: float
    final_price_egp: float
    final_price_usd: float

    def to_dict(self) -> Dict:
        return {
            "product_price": {
                "usd": round(self.product_price_usd, 2),
                "egp": round(self.product_price_egp, 2)
            },
            "international_shipping": {
                "usd": round(self.international_shipping_usd, 2),
                "egp": round(self.international_shipping_egp, 2)
            },
            "custom_duties": {
                "usd": round(self.custom_duties_usd, 2),
                "egp": round(self.custom_duties_egp, 2),
                "percentage": settings.CUSTOM_DUTIES_PERCENT
            },
            "platform_margin": {
                "usd": round(self.platform_margin_usd, 2),
                "egp": round(self.platform_margin_egp, 2),
                "percentage": settings.PLATFORM_MARGIN_PERCENT
            },
            "final_price": {
                "egp": round(self.final_price_egp, 2),
                "usd": round(self.final_price_usd, 2)
            },
            "currency_rate": self.currency_rate,
            "calculation_timestamp": datetime.utcnow().isoformat()
        }

class CurrencyService:
    """Real-time currency conversion service"""

    @staticmethod
    def get_current_rate() -> float:
        """
        Fetch current USD/EGP rate from Central Bank of Egypt API
        Fallback to settings if API fails
        """
        try:
            # Central Bank of Egypt API (example endpoint)
            response = requests.get(
                "https://www.cbe.org.eg/api/currency/usd",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return float(data["rate"])
        except Exception:
            pass

        # Fallback to configured rate
        return settings.USD_TO_EGP_RATE

    @staticmethod
    def convert_usd_to_egp(amount_usd: float, rate: Optional[float] = None) -> float:
        """Convert USD amount to EGP"""
        if rate is None:
            rate = CurrencyService.get_current_rate()
        return amount_usd * rate

class ShippingCalculator:
    """International shipping cost calculator"""

    @staticmethod
    def calculate_shipping(weight_kg: float, destination_country: str = "EG") -> float:
        """
        Calculate international shipping cost in USD
        Based on weight and destination
        """
        base_cost = settings.BASE_SHIPPING_COST_USD
        weight_cost = weight_kg * settings.SHIPPING_PER_KG_USD

        # Country-specific adjustments (expandable)
        country_multipliers = {
            "EG": 1.0,      # Egypt (base)
            "SA": 1.2,      # Saudi Arabia
            "AE": 1.1,      # UAE
            "KW": 1.3,      # Kuwait
        }

        multiplier = country_multipliers.get(destination_country, 1.5)
        total_shipping = (base_cost + weight_cost) * multiplier

        return round(total_shipping, 2)

class PricingEngine:
    """
    Core Dynamic Pricing Engine
    Executes in < 100ms for real-time product browsing
    """

    def __init__(self):
        self.currency_service = CurrencyService()
        self.shipping_calculator = ShippingCalculator()

    def calculate_price(
        self, 
        product: Product, 
        quantity: int = 1,
        destination_country: str = "EG",
        force_rate: Optional[float] = None
    ) -> PriceBreakdown:
        """
        Calculate final price with full transparency

        Formula:
        Final_Price_EGP = (Product_Price_USD * Currency_Rate) + 
                         International_Shipping + 
                         Custom_Duties + 
                         Platform_Margin
        """
        # 1. Get current exchange rate
        currency_rate = force_rate or self.currency_service.get_current_rate()

        # 2. Calculate product price in EGP
        product_price_usd = product.supplier_price_usd * quantity
        product_price_egp = CurrencyService.convert_usd_to_egp(product_price_usd, currency_rate)

        # 3. Calculate international shipping
        total_weight = product.weight_kg * quantity
        shipping_usd = self.shipping_calculator.calculate_shipping(total_weight, destination_country)
        shipping_egp = CurrencyService.convert_usd_to_egp(shipping_usd, currency_rate)

        # 4. Calculate custom duties (percentage of product price)
        custom_duties_usd = product_price_usd * (settings.CUSTOM_DUTIES_PERCENT / 100)
        custom_duties_egp = CurrencyService.convert_usd_to_egp(custom_duties_usd, currency_rate)

        # 5. Calculate platform margin (percentage of total cost)
        subtotal_usd = product_price_usd + shipping_usd + custom_duties_usd
        platform_margin_usd = subtotal_usd * (settings.PLATFORM_MARGIN_PERCENT / 100)
        platform_margin_egp = CurrencyService.convert_usd_to_egp(platform_margin_usd, currency_rate)

        # 6. Final calculation
        final_price_egp = product_price_egp + shipping_egp + custom_duties_egp + platform_margin_egp
        final_price_usd = product_price_usd + shipping_usd + custom_duties_usd + platform_margin_usd

        return PriceBreakdown(
            product_price_usd=product_price_usd,
            currency_rate=currency_rate,
            product_price_egp=product_price_egp,
            international_shipping_usd=shipping_usd,
            international_shipping_egp=shipping_egp,
            custom_duties_usd=custom_duties_usd,
            custom_duties_egp=custom_duties_egp,
            platform_margin_usd=platform_margin_usd,
            platform_margin_egp=platform_margin_egp,
            final_price_egp=final_price_egp,
            final_price_usd=final_price_usd
        )

    def calculate_cart_total(
        self, 
        cart_items: List[Dict], 
        destination_country: str = "EG"
    ) -> Dict:
        """
        Calculate total for entire shopping cart
        Returns aggregated breakdown
        """
        total_egp = 0
        total_usd = 0
        items_breakdown = []

        currency_rate = self.currency_service.get_current_rate()

        for item in cart_items:
            product = item["product"]
            quantity = item["quantity"]

            breakdown = self.calculate_price(
                product, 
                quantity, 
                destination_country,
                force_rate=currency_rate  # Use same rate for all items
            )

            total_egp += breakdown.final_price_egp
            total_usd += breakdown.final_price_usd

            items_breakdown.append({
                "product_id": product.id,
                "product_title": product.title,
                "quantity": quantity,
                "breakdown": breakdown.to_dict()
            })

        return {
            "items": items_breakdown,
            "cart_totals": {
                "egp": round(total_egp, 2),
                "usd": round(total_usd, 2)
            },
            "currency_rate": currency_rate,
            "item_count": len(cart_items)
        }

# Singleton instance
pricing_engine = PricingEngine()
