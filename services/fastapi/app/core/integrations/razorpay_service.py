"""
Razorpay Service — Payment processing for booking feature.
"""

import hashlib
import hmac
import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger("careremind.services.razorpay")


class RazorpayService:
    """Handles Razorpay payment operations."""

    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_SECRET
        self.base_url = "https://api.razorpay.com/v1"

    @property
    def is_configured(self) -> bool:
        """Check if Razorpay credentials are configured."""
        return bool(self.key_id and self.key_secret)

    async def create_order(
        self,
        amount: float,
        currency: str = "INR",
        receipt: Optional[str] = None,
        notes: Optional[dict] = None,
    ) -> dict:
        """
        Create a Razorpay order for payment.
        
        Args:
            amount: Amount in rupees (will be converted to paise)
            currency: Currency code (default: INR)
            receipt: Optional receipt ID
            notes: Optional metadata
        
        Returns:
            {
                "success": True/False,
                "order_id": "order_xxx",
                "amount": 20000,  # in paise
                "currency": "INR",
                "error": "..." (if failed)
            }
        """
        if not self.is_configured:
            return {
                "success": False,
                "error": "Razorpay credentials not configured"
            }

        # Convert rupees to paise (Razorpay uses smallest currency unit)
        amount_paise = int(amount * 100)

        payload = {
            "amount": amount_paise,
            "currency": currency,
            "receipt": receipt or f"rcpt_{int(amount)}",
            "notes": notes or {},
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/orders",
                    json=payload,
                    auth=(self.key_id, self.key_secret),
                )

            data = response.json()

            if response.status_code == 200:
                logger.info("Created Razorpay order: %s", data.get("id"))
                return {
                    "success": True,
                    "order_id": data.get("id"),
                    "amount": data.get("amount"),
                    "currency": data.get("currency"),
                }
            else:
                error = data.get("error", {}).get("description", response.text)
                logger.error("Razorpay order creation failed: %s", error)
                return {
                    "success": False,
                    "error": error
                }

        except httpx.TimeoutException:
            logger.error("Razorpay API timeout")
            return {
                "success": False,
                "error": "Payment gateway timeout"
            }

        except Exception as e:
            logger.error("Razorpay error: %s", e, exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> bool:
        """
        Verify Razorpay payment signature for security.
        
        Args:
            razorpay_order_id: Order ID from Razorpay
            razorpay_payment_id: Payment ID from Razorpay
            razorpay_signature: Signature from Razorpay
        
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.is_configured:
            logger.warning("Cannot verify signature: Razorpay not configured")
            return False

        # Generate expected signature
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected_signature = hmac.new(
            self.key_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        # Compare signatures
        is_valid = hmac.compare_digest(expected_signature, razorpay_signature)

        if is_valid:
            logger.info("Payment signature verified: %s", razorpay_payment_id)
        else:
            logger.warning("Invalid payment signature: %s", razorpay_payment_id)

        return is_valid

    async def fetch_payment(self, payment_id: str) -> dict:
        """
        Fetch payment details from Razorpay.
        
        Returns:
            {
                "success": True/False,
                "payment": {...},
                "error": "..." (if failed)
            }
        """
        if not self.is_configured:
            return {
                "success": False,
                "error": "Razorpay credentials not configured"
            }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/payments/{payment_id}",
                    auth=(self.key_id, self.key_secret),
                )

            data = response.json()

            if response.status_code == 200:
                return {
                    "success": True,
                    "payment": data
                }
            else:
                error = data.get("error", {}).get("description", response.text)
                return {
                    "success": False,
                    "error": error
                }

        except Exception as e:
            logger.error("Failed to fetch payment: %s", e)
            return {
                "success": False,
                "error": str(e)
            }

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """
        Verify webhook signature from Razorpay.
        
        Args:
            payload: Raw request body
            signature: X-Razorpay-Signature header
        
        Returns:
            True if signature is valid, False otherwise
        """
        if not settings.RAZORPAY_WEBHOOK_SECRET:
            logger.warning("RAZORPAY_WEBHOOK_SECRET not configured")
            return False

        expected_signature = hmac.new(
            settings.RAZORPAY_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        is_valid = hmac.compare_digest(expected_signature, signature)

        if not is_valid:
            logger.critical("Invalid webhook signature! Possible spoof attack.")

        return is_valid


razorpay_service = RazorpayService()

