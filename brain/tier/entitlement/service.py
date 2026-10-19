from brain.tier.models import BrainTier

from .models import TierEntitlement
from .policy import TierEntitlementPolicy


class TierEntitlementService:
    """Provides the effective entitlement for a Brain Tier."""

    def __init__(self, policy: TierEntitlementPolicy | None = None) -> None:
        self._policy = policy or TierEntitlementPolicy()

    def get_entitlement(self, tier: BrainTier) -> TierEntitlement:
        return self._policy.get_entitlement(tier)

    def has_capability(
        self,
        tier: BrainTier,
        capability,
    ) -> bool:
        entitlement = self.get_entitlement(tier)
        return capability in entitlement.allowed_capabilities

    def get_max_context_window(self, tier: BrainTier) -> int:
        return self.get_entitlement(tier).max_context_window

    def get_max_complexity(self, tier: BrainTier) -> float:
        return self.get_entitlement(tier).max_complexity