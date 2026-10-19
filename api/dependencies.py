from fastapi import Depends
from sqlalchemy.orm import Session
from database.user_repository import UserRepository
from database.dependencies import get_db
from services.brain_service import BrainService

from brain.self_development.integration.core_integration_service import (
    CoreIntegrationService,
)
from brain.self_development.integration.self_development_factory import (
    create_self_development_gateway,
)

from brain.recharge.balance_service import BrainBalanceService
from brain.recharge.entitlement.consumption import (
    FreeBrainConsumptionPolicy,
)
from brain.recharge.entitlement.repository import (
    FreeBrainEntitlementRepository,
)
from brain.recharge.entitlement.reset_policy import (
    FreeBrainResetPolicy,
)
from brain.recharge.entitlement.service import (
    FreeBrainEntitlementService,
)
from brain.recharge.wallet.repository import (
    BrainWalletRepository,
)
from brain.recharge.wallet.transaction_repository import (
    BrainTransactionRepository,
)
from brain.recharge.wallet.service import BrainWalletService
from brain.recharge.wallet.wallet_operations import BrainWalletOperations


from brain.tier.capacity.activation import (
    TierCapacityActivationService,
)
from brain.tier.capacity.coordinator import (
    TierCapacityCoordinator,
)
from brain.tier.capacity.period import (
    TierCapacityPeriodResolver,
)
from brain.tier.capacity.provisioning import (
    TierCapacityProvisioningService,
)
from brain.tier.capacity.repository import (
    TierBrainCapacityRepository,
)
from brain.tier.entitlement.service import (
    TierEntitlementService,
)

from brain.payment.repository import PaymentRepository
from brain.payment.service import PaymentService
from brain.payment.providers.razorpay_provider import (
    RazorpayPaymentProvider,
)
from brain.payment.verification_service import (
    PaymentVerificationService,
)
from brain.payment.subscription_activation import (
    PaymentSubscriptionActivationService,
)

from brain.subscription.activation import (
    SubscriptionActivationService,
)
from brain.subscription.repository import SubscriptionRepository
from brain.subscription.service import SubscriptionService


def get_brain_service(
    db: Session = Depends(get_db),
) -> BrainService:
    self_development_gateway = create_self_development_gateway()

    core_integration_service = CoreIntegrationService(
        signal_handler=self_development_gateway.process,
    )

    return BrainService(
        db=db,
        core_integration_service=core_integration_service,
    )


def get_brain_balance_service(
    db: Session = Depends(get_db),
) -> BrainBalanceService:


    return BrainBalanceService(
        wallet_repository=BrainWalletRepository(db),
    )


def get_payment_service(
    db: Session = Depends(get_db),
) -> PaymentService:
    return PaymentService(
        payment_repository=PaymentRepository(db),
        payment_provider=RazorpayPaymentProvider(),
    )


def create_payment_subscription_activation_service(
    db: Session,
) -> PaymentSubscriptionActivationService:
    entitlement_service = TierEntitlementService()

    capacity_repository = TierBrainCapacityRepository(db)

    provisioning_service = TierCapacityProvisioningService(
        repository=capacity_repository,
    )

    period_resolver = TierCapacityPeriodResolver(
        entitlement_service=entitlement_service,
    )

    coordinator = TierCapacityCoordinator(
        entitlement_service=entitlement_service,
        provisioning_service=provisioning_service,
        period_resolver=period_resolver,
    )

    capacity_activation_service = TierCapacityActivationService(
        coordinator=coordinator,
    )

    subscription_service = SubscriptionService(
        repository=SubscriptionRepository(db),
    )

    subscription_activation_service = SubscriptionActivationService(
        subscription_service=subscription_service,
        tier_capacity_activation_service=capacity_activation_service,
        user_repository=UserRepository(db),
    )

    return PaymentSubscriptionActivationService(
        subscription_activation_service=subscription_activation_service,
    )


def get_payment_verification_service(
    db: Session = Depends(get_db),
) -> PaymentVerificationService:

    wallet_operations = BrainWalletOperations(
        wallet_repository=BrainWalletRepository(db),
        transaction_repository=BrainTransactionRepository(db),
        wallet_service=BrainWalletService(),
    )



    return PaymentVerificationService(
        payment_repository=PaymentRepository(db),
        payment_provider=RazorpayPaymentProvider(),
        subscription_activation_service=(
            create_payment_subscription_activation_service(db)
        ),
        wallet_operations=wallet_operations,
    )