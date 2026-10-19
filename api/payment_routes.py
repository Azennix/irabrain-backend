from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import (
    get_payment_service,
    get_payment_verification_service,
)
from api.schemas.payment_schema import PaymentVerificationRequest
from brain.payment.service import PaymentService
from brain.payment.verification_service import (
    PaymentVerificationService,
)
from brain.tier.models import BrainTier
from security.dependencies import get_current_user


router = APIRouter(
    prefix="/payment",
    tags=["Payment"],
)


PAID_TIER_PRICES = {
    BrainTier.STARTER: Decimal("49"),
    BrainTier.BRAIN_MINI: Decimal("99"),
    BrainTier.BRAIN_ORION: Decimal("199"),
    BrainTier.THALAMUS: Decimal("499"),
    BrainTier.HIPPOCAMPUS: Decimal("999"),
}


@router.post("/orders")
def create_payment_order(
    tier: BrainTier,
    payment_service: PaymentService = Depends(
        get_payment_service
    ),
    current_user=Depends(get_current_user),
):

    if not current_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Your account is inactive.",
    )
    amount = PAID_TIER_PRICES.get(tier)

    if amount is None:
        raise HTTPException(
            status_code=400,
            detail="Unsupported paid Brain Tier.",
        )

    payment = payment_service.create_payment(
        user_id=current_user.user_id,
        tier=tier,
        amount=amount,
        currency="INR",
    )

    return {
        "payment_id": payment.payment_id,
        "provider": payment.provider,
        "provider_order_id": payment.provider_order_id,
        "tier": payment.tier.value,
        "amount": str(payment.amount),
        "currency": payment.currency,
        "status": payment.status.value,
    }


@router.post("/verify")
def verify_payment(
    request: PaymentVerificationRequest,
    payment_service: PaymentVerificationService = Depends(
        get_payment_verification_service
    ),
    current_user=Depends(get_current_user),
):

    if not current_user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Your account is inactive.",
    )
    payment = payment_service.verify_payment(
        payment_id=request.payment_id,
        user_id=current_user.user_id,
        provider_payment_id=request.provider_payment_id,
        signature=request.signature,
    )

    return {
        "payment_id": payment.payment_id,
        "status": payment.status.value,
        "provider_payment_id": payment.provider_payment_id,
    }