from brain.tier.capability_policy import CapabilityPolicy
from brain.tier.capabilities import Capability
from brain.tier.models import BrainTier


class CapabilityEnforcer:
    @staticmethod
    def enforce(
        tier: BrainTier,
        capability: Capability,
    ) -> None:
        if not CapabilityPolicy.allows(tier, capability):
            raise PermissionError(
                f"Brain tier {tier.value} does not allow "
                f"capability {capability.value}."
            )