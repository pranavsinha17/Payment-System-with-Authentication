import razorpay
from app.config.razorpay import razorpay_settings
from datetime import datetime
from typing import Dict, Any

class RazorpayService:
    def __init__(self):
        self.client = razorpay.Client(
            auth=(razorpay_settings.RAZORPAY_KEY_ID, razorpay_settings.RAZORPAY_KEY_SECRET)
        )
    
    def create_order(self, amount: float, currency: str = "INR", receipt: str = None) -> Dict[str, Any]:
        """
        Create a new Razorpay order
        """
        data = {
            "amount": int(amount * 100),  # Convert to paise
            "currency": currency,
            "receipt": receipt,
            "payment_capture": 1  # Auto capture payment
        }
        return self.client.order.create(data=data)
    
    def verify_payment(self, payment_id: str, order_id: str, signature: str) -> bool:
        """
        Verify the payment signature
        """
        try:
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            }
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except Exception as e:
            return False
    
    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment details from Razorpay
        """
        return self.client.payment.fetch(payment_id)

razorpay_service = RazorpayService() 