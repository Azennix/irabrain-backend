from brain.payment.models import Payment, PaymentStatus
from brain.subscription.activation import SubscriptionActivationService


class PaymentSubscriptionActivationService:

    def __init__(
        self,
        subscription_activation_service: SubscriptionActivationService,
    ):
        if subscription_activation_service is None:
            raise ValueError(
                "Subscription activation service is required."
            )

        self._subscription_activation_service = (
            subscription_activation_service
        )

    def activate_from_payment(
        self,
        *,
        payment: Payment,
        billing_period_started_at,
        billing_period_ends_at,
    ):
        if payment is None:
            raise ValueError("Payment is required.")

        if payment.status != PaymentStatus.SUCCEEDED:
            raise ValueError(
                "Subscription requires a successful payment."
            )
        if payment.payment_id is None:
            raise ValueError(
                "A persisted payment is required for activation."
        )

        if billing_period_ends_at <= billing_period_started_at:
            raise ValueError(
                "Billing period end must be after its start."
        )

        return self._subscription_activation_service.activate(
            user_id=payment.user_id,
            tier=payment.tier,
            started_at=billing_period_started_at,
            current_period_started_at=billing_period_started_at,
            current_period_ends_at=billing_period_ends_at,
        )