from brain.tier.capabilities import Capability
from brain.tier.entitlement.service import TierEntitlementService
from brain.tier.models import BrainTier


def test_free_entitlement():
    service = TierEntitlementService()

    entitlement = service.get_entitlement(BrainTier.FREE)

    assert entitlement.tier == BrainTier.FREE
    assert Capability.REASONING in entitlement.allowed_capabilities
    assert Capability.RESEARCH not in entitlement.allowed_capabilities
    assert entitlement.max_complexity == 0.5


def test_thalamus_entitlement():
    service = TierEntitlementService()

    entitlement = service.get_entitlement(BrainTier.THALAMUS)

    assert entitlement.tier == BrainTier.THALAMUS
    assert Capability.TOOLS in entitlement.allowed_capabilities
    assert Capability.RESEARCH not in entitlement.allowed_capabilities
    assert entitlement.max_complexity == 0.75


def test_hippocampus_entitlement():
    service = TierEntitlementService()

    entitlement = service.get_entitlement(BrainTier.HIPPOCAMPUS)

    assert entitlement.tier == BrainTier.HIPPOCAMPUS
    assert Capability.RESEARCH in entitlement.allowed_capabilities
    assert Capability.AUTONOMOUS_WORK in entitlement.allowed_capabilities
    assert entitlement.max_complexity == 1.0


def test_capability_check():
    service = TierEntitlementService()

    assert service.has_capability(
        BrainTier.FREE,
        Capability.CODING,
    )

    assert not service.has_capability(
        BrainTier.FREE,
        Capability.RESEARCH,
    )

    assert service.has_capability(
        BrainTier.HIPPOCAMPUS,
        Capability.RESEARCH,
    )
def test_entitlement_capabilities_match_capability_policy():
    from brain.tier.capability_policy import CapabilityPolicy

    service = TierEntitlementService()

    for tier in BrainTier:
        entitlement = service.get_entitlement(tier)
        policy_capabilities = CapabilityPolicy.capabilities_for(tier)

        assert entitlement.allowed_capabilities == policy_capabilities