"""
Razorpay Service — Payment processing for booking feature.
Includes automatic retry with exponential backoff for transient failures.
"""

import hashlib
import hmac
import logging
from typing import Optional

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from app.core.config import settings

logger = logging.getLogger("careremind.services.razorpay")

# Shared HTTP client (will be set by main.py lifespan)
_http_client: Optional[httpx.AsyncClient] = None

def set_http_client(client: httpx.AsyncClient):
    """Set the shared HTTP client for connection pooling."""
    global _http_client
    _http_client = client


class RazorpayService:
    """Handles Razorpay payment operations."""

    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_SECRET
        self.base_url = settings.RAZORPAY_API_URL

    @property
    def is_configured(self) -> bool:
        """Check if Razorpay credentials are configured."""
        return bool(self.key_id and self.key_secret)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _send_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """
        Internal method to send HTTP request with retry logic.
        Retries on timeout and network errors with exponential backoff.
        """
        if _http_client:
            if method == "POST":
                return await _http_client.post(url, **kwargs)
            elif method == "GET":
                return await _http_client.get(url, **kwargs)
        else:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_DEFAULT) as client:
                if method == "POST":
                    return await client.post(url, **kwargs)
                elif method == "GET":
                    return await client.get(url, **kwargs)

    async def create_order(
        self,
        amount: float,
        currency: str = "INR",
        receipt: Optional[str] = None,
        notes: Optional[dict] = None,
        idempotency_key: Optional[str] = None,
    ) -> dict:
        """
        Create a Razorpay order for payment.
        
        Args:
            amount: Amount in rupees (will be converted to paise)
            currency: Currency code (default: INR)
            receipt: Optional receipt ID
            notes: Optional metadata
            idempotency_key: Optional idempotency key to prevent duplicate orders
        
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

        # Add idempotency key header if provided
        headers = {}
        if idempotency_key:
            headers["X-Prazorpay-Idempotency-Key"] = idempotency_key

        try:
            response = await self._send_request(
                "POST",
                f"{self.base_url}/orders",
                json=payload,
                auth=(self.key_id, self.key_secret),
                headers=headers if headers else None,
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
            logger.error("Razorpay API timeout (after retries)")
            return {
                "success": False,
                "error": "Payment gateway timeout after retries"
            }

        except Exception as e:
            logger.error("Razorpay error: %s", e, exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def verify_payment_signature(
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
            response = await self._send_request(
                "GET",
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

    async def verify_webhook_signature(
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

