from brain.tier.capability_requirement import CapabilityRequirement
from brain.tier.capability_policy import CapabilityPolicy

from .errors import TierEntitlementError
from .models import TierEntitlement


class TierEntitlementValidator:
    """Validates whether a task requirement fits a tier entitlement."""

    @staticmethod
    def validate(
        entitlement: TierEntitlement,
        requirement: CapabilityRequirement,
    ) -> None:
        if requirement.capability not in entitlement.allowed_capabilities:
            required_tier = CapabilityPolicy.minimum_tier_for(
                requirement.capability
            )

            raise TierEntitlementError(
                code="CAPABILITY_NOT_INCLUDED",
                message=(
                    f"Brain tier {entitlement.tier.value} does not allow "
                    f"capability {requirement.capability.value}."
                ),
                required_tier=(
                    required_tier.value if required_tier else None
                ),
            )

        if requirement.required_context_window > entitlement.max_context_window:
            raise TierEntitlementError(
                code="CONTEXT_LIMIT_EXCEEDED",
                message=(
                    f"Required context window "
                    f"{requirement.required_context_window} exceeds "
                    f"Brain tier {entitlement.tier.value} limit "
                    f"{entitlement.max_context_window}."
                ),
            )

        if requirement.complexity > entitlement.max_complexity:
            raise TierEntitlementError(
                code="COMPLEXITY_LIMIT_EXCEEDED",
                message=(
                    f"Required complexity {requirement.complexity} exceeds "
                    f"Brain tier {entitlement.tier.value} limit "
                    f"{entitlement.max_complexity}."
                ),
            )