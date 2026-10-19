from decimal import Decimal

from brain.tier.capability_policy import CapabilityPolicy
from brain.tier.models import BrainTier

from .models import (
    TierEntitlement,
    TierResetPeriod,
    TierUsagePolicy,
)


class TierEntitlementPolicy:
    """Defines product-level entitlement rules for each Brain Tier."""

    def get_entitlement(self, tier: BrainTier) -> TierEntitlement:
        capabilities = CapabilityPolicy.capabilities_for(tier)

        if tier == BrainTier.FREE:
            return TierEntitlement(
                tier=tier,
                allowed_capabilities=capabilities,
                max_context_window=64_000,
                max_complexity=0.5,
                usage_policy=TierUsagePolicy.LIMITED,
                included_brain_units=Decimal("100"),
                reset_period=TierResetPeriod.HOURLY,
                reset_interval_hours=24,
            )

        if tier == BrainTier.STARTER:
            return TierEntitlement(
                tier=tier,
                allowed_capabilities=capabilities,
                max_context_window=64_000,
                max_complexity=0.5,
                usage_policy=TierUsagePolicy.LIMITED,
                included_brain_units=Decimal("500"),
                reset_period=TierResetPeriod.BILLING_CYCLE,
            )

        if tier == BrainTier.BRAIN_MINI:
            return TierEntitlement(
                tier=tier,
                allowed_capabilities=capabilities,
                max_context_window=100_000,
                max_complexity=0.6,
                usage_policy=TierUsagePolicy.STANDARD,
                included_brain_units=Decimal("1200"),
                reset_period=TierResetPeriod.BILLING_CYCLE,
            )

        if tier == BrainTier.BRAIN_ORION:
            return TierEntitlement(
                tier=tier,
                allowed_capabilities=capabilities,
                max_context_window=128_000,
                max_complexity=0.7,
                usage_policy=TierUsagePolicy.STANDARD,
                included_brain_units=Decimal("3000"),
                reset_period=TierResetPeriod.BILLING_CYCLE,
            )

        if tier == BrainTier.THALAMUS:
            return TierEntitlement(
                tier=tier,
                allowed_capabilities=capabilities,
                max_context_window=128_000,
                max_complexity=0.75,
                usage_policy=TierUsagePolicy.STANDARD,
                included_brain_units=Decimal("9000"),
                reset_period=TierResetPeriod.BILLING_CYCLE,
            )

        if tier == BrainTier.HIPPOCAMPUS:
            return TierEntitlement(
                tier=tier,
                allowed_capabilities=capabilities,
                max_context_window=200_000,
                max_complexity=1.0,
                usage_policy=TierUsagePolicy.HIGH,
                included_brain_units=Decimal("22000"),
                reset_period=TierResetPeriod.BILLING_CYCLE,
            )

        raise ValueError(f"Unsupported Brain Tier: {tier}")