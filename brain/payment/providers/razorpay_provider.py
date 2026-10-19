import os
from decimal import Decimal

import razorpay

from brain.payment.providers.base import PaymentOrder, PaymentProvider
from brain.tier.models import BrainTier


class RazorpayPaymentProvider(PaymentProvider):

    def __init__(self):
        key_id = os.getenv("RAZORPAY_KEY_ID")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET")

        if not key_id:
            raise ValueError("RAZORPAY_KEY_ID is required.")

        if not key_secret:
            raise ValueError("RAZORPAY_KEY_SECRET is required.")

        self._client = razorpay.Client(
            auth=(key_id, key_secret)
        )

    _TIER_PRICES = {
        BrainTier.STARTER: Decimal("49"),
        BrainTier.BRAIN_MINI: Decimal("99"),
        BrainTier.BRAIN_ORION: Decimal("199"),
        BrainTier.THALAMUS: Decimal("499"),
        BrainTier.HIPPOCAMPUS: Decimal("999"),
    }

    def create_order(
        self,
        *,
        user_id: int,
        tier: BrainTier,
        amount: Decimal,
        currency: str,
    ) -> PaymentOrder:

        if user_id <= 0:
            raise ValueError("User ID must be positive.")

        expected_amount = self._TIER_PRICES.get(tier)

        if expected_amount is None:
            raise ValueError("Payment requires a paid Brain Tier.")

        if amount != expected_amount:
            raise ValueError(
                f"Invalid amount for {tier.value}. "
                f"Expected {expected_amount} {currency}."
            )

        if currency != "INR":
            raise ValueError("Only INR payments are supported.")

        order = self._client.order.create(
            {
                "amount": int(expected_amount * Decimal("100")),
                "currency": "INR",
                "receipt": f"irabrain_{user_id}_{tier.value.lower()}",
                "notes": {
                    "user_id": str(user_id),
                    "tier": tier.value,
                },
            }
        )

        return PaymentOrder(
            provider="razorpay",
            provider_order_id=order["id"],
            user_id=user_id,
            tier=tier,
            amount=expected_amount,
            currency="INR",
        )

    def verify_payment(
        self,
        *,
        provider_order_id: str,
        provider_payment_id: str,
        signature: str,
    ) -> bool:

        try:
            self._client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": provider_order_id,
                    "razorpay_payment_id": provider_payment_id,
                    "razorpay_signature": signature,
                }
            )
            return True

        except Exception:
            return False

    def verify_payment_details(
        self,
        *,
        provider_order_id: str,
        provider_payment_id: str,
        expected_amount: Decimal,
        expected_currency: str,
    ) -> bool:
        try:
            payment = self._client.payment.fetch(provider_payment_id)

            if payment.get("order_id") != provider_order_id:
                return False

            expected_amount_paise = int(
                expected_amount * Decimal("100")
        )

            if payment.get("amount") != expected_amount_paise:
                return False

            if payment.get("currency") != expected_currency:
                return False

            if payment.get("status") != "captured":
                return False

            return True

        except Exception:
            return False