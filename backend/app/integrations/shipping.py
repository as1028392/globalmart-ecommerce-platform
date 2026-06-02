"""
Shipping & Logistics Integrations
Bosta (Egypt), Aramex (International)
Auto-generate waybills and tracking
"""
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
from app.core.config import settings

class BaseShippingProvider:
    """Abstract shipping provider"""

    def __init__(self):
        self.session = requests.Session()

    def create_shipment(self, order_data: Dict) -> Dict:
        raise NotImplementedError

    def track_shipment(self, tracking_number: str) -> Dict:
        raise NotImplementedError

    def cancel_shipment(self, tracking_number: str) -> bool:
        raise NotImplementedError

class BostaProvider(BaseShippingProvider):
    """
    Bosta API Integration (Egypt)
    Handles last-mile delivery within Egypt
    Docs: https://docs.bosta.co/
    """

    BASE_URL = "https://api.bosta.co/api/v0"

    def __init__(self):
        super().__init__()
        self.api_key = settings.BOSTA_API_KEY
        self.session.headers.update({
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        })

    def create_shipment(self, order_data: Dict) -> Dict:
        """
        Create domestic shipment when product arrives in Egypt
        """
        payload = {
            "pickupAddress": {
                "firstLine": "GlobalMart Warehouse",
                "city": "Cairo",
                "zone": "Nasr City",
                "district": "Makram Ebeid"
            },
            "dropOffAddress": {
                "firstLine": order_data["address"],
                "city": order_data["city"],
                "zone": order_data.get("zone", ""),
                "district": order_data.get("district", ""),
                "buildingNumber": order_data.get("building", ""),
                "floor": order_data.get("floor", ""),
                "apartment": order_data.get("apartment", "")
            },
            "receiver": {
                "firstName": order_data["customer_name"],
                "lastName": "",
                "phone": order_data["phone"]
            },
            "type": 10,  # Package delivery
            "cod": order_data.get("cod_amount", 0),
            "businessReferenceNumber": order_data["order_number"]
        }

        response = self.session.post(
            f"{self.BASE_URL}/deliveries",
            json=payload,
            timeout=15
        )

        data = response.json()

        return {
            "provider": "bosta",
            "tracking_number": data.get("trackingNumber"),
            "tracking_url": f"https://bosta.co/tracking/?tracking_number={data.get('trackingNumber')}",
            "status": data.get("state"),
            "estimated_delivery": data.get("estimatedDeliveryDate"),
            "label_url": data.get("packageLabel"),
            "cod_collected": data.get("cod", 0)
        }

    def track_shipment(self, tracking_number: str) -> Dict:
        """Get real-time tracking updates"""
        response = self.session.get(
            f"{self.BASE_URL}/deliveries/{tracking_number}",
            timeout=10
        )

        data = response.json()

        # Map Bosta states to our OrderStatus enum
        state_map = {
            "PICKED_UP": "shipped",
            "IN_TRANSIT": "shipped",
            "OUT_FOR_DELIVERY": "out_for_delivery",
            "DELIVERED": "delivered",
            "CANCELLED": "cancelled"
        }

        return {
            "current_status": state_map.get(data.get("state"), "shipped"),
            "detailed_status": data.get("state"),
            "last_update": data.get("updatedAt"),
            "tracking_history": data.get("timeline", []),
            "expected_delivery": data.get("estimatedDeliveryDate")
        }

    def cancel_shipment(self, tracking_number: str) -> bool:
        """Cancel delivery if needed"""
        response = self.session.delete(
            f"{self.BASE_URL}/deliveries/{tracking_number}",
            timeout=10
        )
        return response.status_code == 200

class AramexProvider(BaseShippingProvider):
    """
    Aramex International Shipping
    Handles cross-border shipping to Egypt
    """

    BASE_URL = "https://ws.aramex.net/ShippingAPI.V2/ShippingService.svc"

    def __init__(self):
        super().__init__()
        self.api_key = settings.ARAMEX_API_KEY

    def create_shipment(self, order_data: Dict) -> Dict:
        """
        Create international shipment from supplier country to Egypt
        """
        payload = {
            "ClientInfo": {
                "UserName": "api_user",
                "Password": "api_password",
                "Version": "v1.0",
                "AccountNumber": "123456",
                "AccountPin": "123456",
                "AccountEntity": "Cairo",
                "AccountCountryCode": "EG"
            },
            "Shipments": [{
                "Reference1": order_data["order_number"],
                "Shipper": {
                    "AccountNumber": "123456",
                    "PartyAddress": {
                        "Line1": order_data.get("supplier_address", "Supplier Warehouse"),
                        "City": order_data.get("supplier_city", "Guangzhou"),
                        "CountryCode": order_data.get("supplier_country", "CN")
                    },
                    "Contact": {
                        "PersonName": "Supplier",
                        "PhoneNumber1": "0000000000"
                    }
                },
                "Consignee": {
                    "PartyAddress": {
                        "Line1": order_data["address"],
                        "City": order_data["city"],
                        "CountryCode": "EG"
                    },
                    "Contact": {
                        "PersonName": order_data["customer_name"],
                        "PhoneNumber1": order_data["phone"]
                    }
                },
                "ShippingDateTime": datetime.utcnow().isoformat(),
                "DueDate": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "Details": {
                    "Dimensions": {
                        "Length": 10,
                        "Width": 10,
                        "Height": 10,
                        "Unit": "cm"
                    },
                    "ActualWeight": {
                        "Value": order_data.get("weight_kg", 1),
                        "Unit": "KG"
                    },
                    "ProductGroup": "EXP",
                    "ProductType": "PPX",
                    "PaymentType": "P",
                    "PaymentOptions": "CASH",
                    "Services": "CODS",
                    "NumberOfPieces": 1,
                    "DescriptionOfGoods": "E-commerce Products",
                    "GoodsOriginCountry": order_data.get("supplier_country", "CN")
                }
            }]
        }

        response = self.session.post(
            f"{self.BASE_URL}/json/CreateShipments",
            json=payload,
            timeout=20
        )

        data = response.json()
        shipment = data.get("Shipments", [{}])[0]

        return {
            "provider": "aramex",
            "tracking_number": shipment.get("ID"),
            "tracking_url": f"https://www.aramex.com/track?tracknumber={shipment.get('ID')}",
            "label_url": shipment.get("LabelURL"),
            "estimated_delivery": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "shipping_cost": shipment.get("ShipmentCharges", 0)
        }

    def track_shipment(self, tracking_number: str) -> Dict:
        """Track international shipment"""
        payload = {
            "ClientInfo": {
                "UserName": "api_user",
                "Password": "api_password"
            },
            "Shipments": [tracking_number]
        }

        response = self.session.post(
            f"{self.BASE_URL}/json/TrackShipments",
            json=payload,
            timeout=10
        )

        data = response.json()
        tracking = data.get("TrackingResults", [{}])[0]

        return {
            "current_status": tracking.get("UpdateCode", "in_transit"),
            "detailed_status": tracking.get("UpdateDescription", ""),
            "location": tracking.get("UpdateLocation", ""),
            "last_update": tracking.get("UpdateDateTime", ""),
            "tracking_history": tracking.get("TrackingDetails", [])
        }

class ShippingService:
    """Central shipping orchestrator"""

    PROVIDERS = {
        "bosta": BostaProvider,
        "aramex": AramexProvider
    }

    @staticmethod
    def get_provider(provider_name: str) -> BaseShippingProvider:
        provider_class = ShippingService.PROVIDERS.get(provider_name)
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")
        return provider_class()

    @staticmethod
    def create_domestic_delivery(order_data: Dict) -> Dict:
        """Create Bosta delivery for Egypt last-mile"""
        provider = ShippingService.get_provider("bosta")
        return provider.create_shipment(order_data)

    @staticmethod
    def create_international_shipment(order_data: Dict) -> Dict:
        """Create Aramex shipment from supplier to Egypt"""
        provider = ShippingService.get_provider("aramex")
        return provider.create_shipment(order_data)

    @staticmethod
    def auto_select_provider(order_data: Dict) -> str:
        """
        Auto-select shipping provider based on:
        - Product origin country
        - Customer location in Egypt
        - Cost optimization
        """
        supplier_country = order_data.get("supplier_country", "CN")

        # If product is already in Egypt, use Bosta
        if supplier_country == "EG":
            return "bosta"

        # International orders -> Aramex for cross-border
        return "aramex"
