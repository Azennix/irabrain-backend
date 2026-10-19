from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from brain.tier.models import BrainTier


@dataclass(frozen=True, slots=True)
class PaymentOrder:
    provider: str
    provider_order_id: str
    user_id: int
    tier: BrainTier
    amount: Decimal
    currency: str


class PaymentProvider(ABC):

    @abstractmethod
    def create_order(
        self,
        *,
        user_id: int,
        tier: BrainTier,
        amount: Decimal,
        currency: str,
    ) -> PaymentOrder:
        raise NotImplementedError

    @abstractmethod
    def verify_payment(
        self,
        *,
        provider_order_id: str,
        provider_payment_id: str,
        signature: str,
    ) -> bool:
        raise NotImplementedError