from datetime import datetime, timedelta, timezone

from brain.payment.models import Payment, PaymentStatus
from brain.payment.providers.base import PaymentProvider
from brain.payment.repository import PaymentRepository
from brain.payment.subscription_activation import (
    PaymentSubscriptionActivationService,
)
from brain.recharge.wallet.wallet_operations import BrainWalletOperations
from brain.tier.models import BrainTier


class PaymentVerificationService:

    def __init__(


        self,
        payment_repository: PaymentRepository,
        payment_provider: PaymentProvider,
        subscription_activation_service:
            PaymentSubscriptionActivationService,

        wallet_operations: BrainWalletOperations,
    ):



        if payment_repository is None:
            raise ValueError("Payment repository is required.")

        if payment_provider is None:
            raise ValueError("Payment provider is required.")

        if subscription_activation_service is None:
            raise ValueError(
                "Payment subscription activation service is required."
            )

        if wallet_operations is None:
            raise ValueError("Brain wallet operations are required.")


        self._payment_repository = payment_repository
        self._payment_provider = payment_provider
        self._subscription_activation_service = (
            subscription_activation_service
        )
        self._wallet_operations = wallet_operations


    _PURCHASE_CREDITS = {
        BrainTier.STARTER: 500,
        BrainTier.BRAIN_MINI: 1200,
        BrainTier.BRAIN_ORION: 3000,
        BrainTier.THALAMUS: 9000,
        BrainTier.HIPPOCAMPUS: 22000,
    }


    def _credit_wallet_for_payment(self, payment: Payment) -> None:
        units = self._PURCHASE_CREDITS.get(payment.tier)

        if units is None:
            raise ValueError(
                f"No purchase credit configured for tier: {payment.tier}"
            )

        self._wallet_operations.recharge(
            user_id=payment.user_id,
            units=units,
            reference_id=f"payment:{payment.payment_id}",
            metadata={
                "payment_id": payment.payment_id,
                "tier": payment.tier.value,
            },
        )

    def verify_payment(
        self,
        *,
        payment_id: int,
        user_id: int,
        provider_payment_id: str,
        signature: str,
    ) -> Payment:

        payment = self._payment_repository.get_by_id(
            payment_id,
            for_update=True,
)
        if payment is None:
            raise ValueError("Payment not found.")

        if payment.user_id != user_id:
            raise ValueError(
                "Payment does not belong to the current user."
            )

        if payment.status == PaymentStatus.SUCCEEDED:
            # Do not activate again here. A successful payment may
            # already have activated the subscription and capacity.
            self._credit_wallet_for_payment(payment)
            return payment

        if payment.status != PaymentStatus.CREATED:
            raise ValueError(
                "Payment is not awaiting verification."
            )

        verified = self._payment_provider.verify_payment(
            provider_order_id=payment.provider_order_id,
            provider_payment_id=provider_payment_id,
            signature=signature,
)

        if not verified:
            raise ValueError("Payment signature verification failed.")

        verify_details = getattr(
            self._payment_provider,
            "verify_payment_details",
            None,
)

        if not callable(verify_details):
            raise ValueError(
                "Payment provider does not support payment-details verification."
    )

        details_verified = verify_details(
            provider_order_id=payment.provider_order_id,
            provider_payment_id=provider_payment_id,
            expected_amount=payment.amount,
            expected_currency=payment.currency,
)

        if not details_verified:
            raise ValueError(
                "Payment amount, currency, order, or capture status is invalid."
    )

        now = datetime.now(timezone.utc)
        period_ends_at = now + timedelta(days=30)

        succeeded_payment = Payment(
            payment_id=payment.payment_id,
            user_id=payment.user_id,
            tier=payment.tier,
            amount=payment.amount,
            currency=payment.currency,
            status=PaymentStatus.SUCCEEDED,
            provider=payment.provider,
            provider_order_id=payment.provider_order_id,
            provider_payment_id=provider_payment_id,
            created_at=payment.created_at,
            updated_at=now,
        )

        # Both operations use the same database session supplied
        # through api.dependencies.py. If activation raises, the
        # request dependency can roll back the database transaction.
        updated_payment = self._payment_repository.update(
            succeeded_payment
        )

        self._subscription_activation_service.activate_from_payment(
            payment=updated_payment,
            billing_period_started_at=now,
            billing_period_ends_at=period_ends_at,
        )

        self._credit_wallet_for_payment(updated_payment)

        return updated_payment