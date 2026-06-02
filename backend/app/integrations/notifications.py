"""
Communications and Notifications
Twilio (SMS), Firebase Cloud Messaging (Push)
"""
import requests
from typing import List, Dict, Optional
from app.core.config import settings

class SMSService:
    """
    Twilio SMS Integration
    For phone verification and order updates
    """

    def __init__(self):
        self.account_sid = settings.TWILIO_SID
        self.auth_token = settings.TWILIO_TOKEN
        self.from_number = settings.TWILIO_PHONE
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}"

    def send_sms(self, to_phone: str, message: str) -> Dict:
        """Send SMS to Egyptian number"""
        # Format Egyptian number (add +20 if needed)
        if to_phone.startswith("0"):
            to_phone = "+20" + to_phone[1:]
        elif not to_phone.startswith("+"):
            to_phone = "+20" + to_phone

        response = requests.post(
            f"{self.base_url}/Messages.json",
            auth=(self.account_sid, self.auth_token),
            data={
                "From": self.from_number,
                "To": to_phone,
                "Body": message,
                "MessagingServiceSid": "MGxxxxxxxx"  # Optional: Messaging Service
            },
            timeout=10
        )

        return {
            "success": response.status_code == 201,
            "message_sid": response.json().get("sid"),
            "status": response.json().get("status"),
            "error": response.json().get("error_message")
        }

    def send_verification_code(self, phone: str, code: str) -> Dict:
        """Send phone verification SMS"""
        message = f"Your GlobalMart verification code is: {code}. Valid for 10 minutes."
        return self.send_sms(phone, message)

    def send_order_confirmation(self, phone: str, order_number: str, total_egp: float) -> Dict:
        """Send order confirmation"""
        message = (
            f"✅ Order #{order_number} confirmed!
"
            f"Total: {total_egp:.2f} EGP
"
            f"Track: https://globalmart.com/track/{order_number}
"
            f"Thank you for shopping with GlobalMart!"
        )
        return self.send_sms(phone, message)

    def send_status_update(self, phone: str, order_number: str, status: str, tracking_url: str = "") -> Dict:
        """Send order status update"""
        status_messages = {
            "paid": f"💳 Payment received for order #{order_number}. Processing now!",
            "shipped": f"📦 Order #{order_number} has been shipped! Track: {tracking_url}",
            "in_customs": f"🛃 Order #{order_number} is in customs. Expected clearance soon.",
            "out_for_delivery": f"🚚 Order #{order_number} is out for delivery today!",
            "delivered": f"🎉 Order #{order_number} delivered! Rate your experience: https://globalmart.com/rate/{order_number}"
        }

        message = status_messages.get(status, f"Order #{order_number} status: {status}")
        return self.send_sms(phone, message)

class PushNotificationService:
    """
    Firebase Cloud Messaging (FCM)
    Real-time push notifications for mobile apps
    """

    def __init__(self):
        self.credentials_path = settings.FIREBASE_CREDENTIALS_PATH
        self.fcm_url = "https://fcm.googleapis.com/v1/projects/globalmart/messages:send"

    def _get_access_token(self) -> str:
        """Get OAuth2 token from Firebase credentials"""
        from google.oauth2 import service_account
        import google.auth.transport.requests

        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=["https://www.googleapis.com/auth/firebase.messaging"]
        )

        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token

    def send_push(self, token: str, title: str, body: str, data: Dict = None) -> Dict:
        """Send push notification to device"""
        access_token = self._get_access_token()

        payload = {
            "message": {
                "token": token,
                "notification": {
                    "title": title,
                    "body": body
                },
                "data": data or {},
                "android": {
                    "priority": "high",
                    "notification": {
                        "sound": "default",
                        "channel_id": "order_updates"
                    }
                },
                "apns": {
                    "payload": {
                        "aps": {
                            "sound": "default",
                            "badge": 1
                        }
                    }
                }
            }
        }

        response = requests.post(
            self.fcm_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=10
        )

        return {
            "success": response.status_code == 200,
            "message_id": response.json().get("name"),
            "error": response.json().get("error", {}).get("message")
        }

    def send_order_update_push(self, token: str, order_number: str, status: str) -> Dict:
        """Send order status push notification"""
        status_titles = {
            "paid": "Payment Confirmed ✅",
            "shipped": "Order Shipped 📦",
            "in_customs": "In Customs 🛃",
            "out_for_delivery": "Out for Delivery 🚚",
            "delivered": "Delivered! 🎉"
        }

        title = status_titles.get(status, "Order Update")
        body = f"Your order #{order_number} is now {status.replace('_', ' ').title()}"

        return self.send_push(
            token=token,
            title=title,
            body=body,
            data={
                "order_number": order_number,
                "status": status,
                "type": "order_update"
            }
        )

    def send_bulk_push(self, tokens: List[str], title: str, body: str) -> List[Dict]:
        """Send to multiple devices"""
        results = []
        for token in tokens:
            result = self.send_push(token, title, body)
            results.append(result)
        return results

class NotificationService:
    """Central notification orchestrator"""

    def __init__(self):
        self.sms = SMSService()
        self.push = PushNotificationService()

    def notify_order_status(self, user, order, status: str):
        """
        Send multi-channel notification for order status
        - SMS (always)
        - Push (if token available)
        """
        # SMS Notification
        if user.phone:
            self.sms.send_status_update(
                user.phone,
                order.order_number,
                status,
                order.tracking_url
            )

        # Push Notification
        if hasattr(user, 'fcm_token') and user.fcm_token:
            self.push.send_order_update_push(
                user.fcm_token,
                order.order_number,
                status
            )

    def verify_phone(self, phone: str, code: str):
        """Send verification code via SMS"""
        return self.sms.send_verification_code(phone, code)
