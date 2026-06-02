"""
Payment Gateway Integrations
Paymob, Fawry, PayTabs Egypt
Supports Vodafone Cash, Meeza, Visa
"""
import requests
import json
from typing import Dict, Optional
from datetime import datetime
from app.core.config import settings

class BasePaymentGateway:
    """Abstract payment gateway"""

    def __init__(self):
        self.session = requests.Session()

    def create_payment(self, amount_egp: float, order_id: str, 
                      customer_data: Dict) -> Dict:
        raise NotImplementedError

    def verify_payment(self, transaction_id: str) -> bool:
        raise NotImplementedError

    def refund(self, transaction_id: str, amount: float) -> bool:
        raise NotImplementedError

class PaymobGateway(BasePaymentGateway):
    """
    Paymob Integration
    Supports: Vodafone Cash, Meeza, Visa/Mastercard
    Docs: https://docs.paymob.com/
    """

    BASE_URL = "https://accept.paymob.com/api"

    def __init__(self):
        super().__init__()
        self.api_key = settings.PAYMOB_API_KEY
        self.integration_id = settings.PAYMOB_INTEGRATION_ID

    def _get_auth_token(self) -> str:
        """Step 1: Authentication"""
        response = self.session.post(
            f"{self.BASE_URL}/auth/tokens",
            json={"api_key": self.api_key},
            timeout=10
        )
        return response.json().get("token")

    def create_payment(self, amount_egp: float, order_id: str, 
                      customer_data: Dict) -> Dict:
        """
        Create payment intention
        Returns payment URL/iframe for checkout
        """
        # Step 1: Auth
        auth_token = self._get_auth_token()

        # Step 2: Create Order
        order_response = self.session.post(
            f"{self.BASE_URL}/ecommerce/orders",
            json={
                "auth_token": auth_token,
                "delivery_needed": False,
                "amount_cents": int(amount_egp * 100),
                "currency": "EGP",
                "merchant_order_id": order_id,
                "items": []
            },
            timeout=10
        )
        paymob_order_id = order_response.json().get("id")

        # Step 3: Generate Payment Key
        payment_key_response = self.session.post(
            f"{self.BASE_URL}/acceptance/payment_keys",
            json={
                "auth_token": auth_token,
                "amount_cents": int(amount_egp * 100),
                "expiration": 3600,
                "order_id": paymob_order_id,
                "billing_data": {
                    "first_name": customer_data.get("first_name", "Customer"),
                    "last_name": customer_data.get("last_name", "User"),
                    "email": customer_data.get("email", "customer@example.com"),
                    "phone_number": customer_data.get("phone", "01000000000"),
                    "apartment": "NA",
                    "floor": "NA",
                    "street": customer_data.get("address", "NA"),
                    "building": "NA",
                    "shipping_method": "PKG",
                    "postal_code": "NA",
                    "city": customer_data.get("city", "Cairo"),
                    "country": "EG",
                    "state": customer_data.get("governorate", "Cairo")
                },
                "currency": "EGP",
                "integration_id": self.integration_id
            },
            timeout=10
        )

        payment_token = payment_key_response.json().get("token")

        return {
            "gateway": "paymob",
            "payment_token": payment_token,
            "iframe_url": f"https://accept.paymob.com/api/acceptance/iframes/
{self.integration_id}?payment_token={payment_token}",
            "wallet_url": f"https://accept.paymob.com/api/acceptance/payments/pay",
            "order_id": paymob_order_id
        }

    def verify_payment(self, transaction_id: str) -> bool:
        """Verify transaction status"""
        auth_token = self._get_auth_token()

        response = self.session.get(
            f"{self.BASE_URL}/acceptance/transactions/{transaction_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=10
        )

        data = response.json()
        return data.get("success") and data.get("pending") == False

    def process_vodafone_cash(self, payment_token: str, phone: str) -> Dict:
        """Process Vodafone Cash wallet payment"""
        response = self.session.post(
            f"{self.BASE_URL}/acceptance/payments/pay",
            json={
                "source": {
                    "identifier": phone,
                    "subtype": "WALLET"
                },
                "payment_token": payment_token
            },
            timeout=10
        )
        return response.json()

class FawryGateway(BasePaymentGateway):
    """
    Fawry Payment Integration
    Supports: Fawry Pay, Meeza cards
    """

    BASE_URL = "https://atfawry.com/fawrypay-api/api"

    def __init__(self):
        super().__init__()
        self.merchant_code = settings.FAWRY_MERCHANT_CODE

    def _generate_signature(self, data: str) -> str:
        """Generate SHA-256 signature"""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()

    def create_payment(self, amount_egp: float, order_id: str, 
                      customer_data: Dict) -> Dict:
        """Create Fawry payment request"""

        request_data = {
            "merchantCode": self.merchant_code,
            "merchantRefNumber": order_id,
            "customerMobile": customer_data.get("phone", ""),
            "customerEmail": customer_data.get("email", ""),
            "customerName": customer_data.get("name", ""),
            "paymentExpiry": 3600,
            "chargeItems": [{
                "itemId": order_id,
                "description": "Order Payment",
                "price": amount_egp,
                "quantity": 1
            }],
            "auth_token": settings.PAYMOB_API_KEY  # Or separate Fawry key
        }

        signature_data = f"{self.merchant_code}{order_id}{amount_egp}{settings.PAYMOB_API_KEY}"
        request_data["signature"] = self._generate_signature(signature_data)

        response = self.session.post(
            f"{self.BASE_URL}/payments/init",
            json=request_data,
            timeout=10
        )

        return {
            "gateway": "fawry",
            "reference_number": response.json().get("referenceNumber"),
            "payment_url": response.json().get("paymentUrl"),
            "status": response.json().get("status")
        }

    def verify_payment(self, reference_number: str) -> bool:
        """Check payment status"""
        response = self.session.get(
            f"{self.BASE_URL}/payments/status/{reference_number}",
            timeout=10
        )
        data = response.json()
        return data.get("paymentStatus") == "PAID"

class PaymentService:
    """Central payment orchestrator"""

    GATEWAYS = {
        "paymob": PaymobGateway,
        "fawry": FawryGateway
    }

    @staticmethod
    def get_gateway(gateway_name: str) -> BasePaymentGateway:
        gateway_class = PaymentService.GATEWAYS.get(gateway_name)
        if not gateway_class:
            raise ValueError(f"Unknown gateway: {gateway_name}")
        return gateway_class()

    @staticmethod
    def process_payment(
        method: str,  # vodafone_cash, meeza, visa
        amount_egp: float,
        order_id: str,
        customer_data: Dict
    ) -> Dict:
        """
        Route payment to appropriate gateway based on method
        """
        # Map payment methods to gateways
        method_gateway_map = {
            "vodafone_cash": "paymob",
            "meeza": "fawry",
            "visa": "paymob"
        }

        gateway_name = method_gateway_map.get(method, "paymob")
        gateway = PaymentService.get_gateway(gateway_name)

        result = gateway.create_payment(amount_egp, order_id, customer_data)
        result["payment_method"] = method

        return result
