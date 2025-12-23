import razorpay
from app.config import settings
import json
import hmac
import hashlib

class RazorpayService:
    def __init__(self):
        self.client = razorpay.Client(auth=(
            settings.razorpay_key_id,
            settings.razorpay_key_secret
        ))
    
    def create_order(self, amount: float, currency: str = "INR", 
                    receipt: str = None, notes: dict = None) -> dict:
        """
        Create a Razorpay order
        """
        data = {
            "amount": int(amount * 100),  # Razorpay expects amount in paise
            "currency": currency,
            "payment_capture": 1  # Auto capture payment
        }
        
        if receipt:
            data["receipt"] = receipt
        if notes:
            data["notes"] = notes
            
        return self.client.order.create(data)
    
    def verify_payment_signature(self, order_id: str, payment_id: str, signature: str) -> bool:
        """
        Verify payment signature to ensure authenticity
        """
        try:
            self.client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            return True
        except razorpay.errors.SignatureVerificationError:
            return False
    
    def verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        """
        Verify webhook signature
        """
        try:
            self.client.utility.verify_webhook_signature(
                body.decode('utf-8'),
                signature,
                settings.webhook_secret
            )
            return True
        except razorpay.errors.SignatureVerificationError:
            return False
    
    def fetch_payment(self, payment_id: str) -> dict:
        """
        Fetch payment details from Razorpay
        """
        return self.client.payment.fetch(payment_id)
    
    def create_refund(self, payment_id: str, amount: float = None, notes: dict = None) -> dict:
        """
        Create a refund for a payment
        """
        data = {}
        if amount:
            data["amount"] = int(amount * 100)
        if notes:
            data["notes"] = notes
            
        return self.client.payment.refund(payment_id, data)
    
    def fetch_refund(self, refund_id: str) -> dict:
        """
        Fetch refund details
        """
        return self.client.refund.fetch(refund_id)

# Singleton instance
razorpay_service = RazorpayService()