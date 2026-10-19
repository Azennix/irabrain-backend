from brain.tier.models import BrainTier
from brain.tier.capabilities import Capability


class CapabilityPolicy:
    # Each tier = the tier below it + new capabilities.
    # A higher tier can never have less than a lower tier.

    # FREE: try the brain (cheap model, small memory limit enforced elsewhere)
    _FREE = frozenset({
        Capability.BASIC_CHAT,
        Capability.MEMORY,
        Capability.REASONING,
        Capability.ANALYSIS,

    })

    # STARTER: daily brain (full recall, plans, short summaries)
    _STARTER = _FREE | {
        Capability.REASONING,
    }

    # BRAIN_MINI: study and notes (PDFs, questions from own notes, longer answers)
    _BRAIN_MINI = _STARTER | {
        Capability.ANALYSIS,
        Capability.DOCUMENT_ANALYSIS,
        Capability.LARGE_CONTEXT,
    }

    # BRAIN_ORION: think and build (strong model, coding, one-page site + preview)
    _BRAIN_ORION = _BRAIN_MINI | {
        Capability.DEEP_REASONING,
        Capability.CODING,
    }

    # THALAMUS: publish (multi-page sites, GitHub publish, live link)
    _THALAMUS = _BRAIN_ORION | {
        Capability.ADVANCED_CODING,
        Capability.TOOLS,
    }

    # HIPPOCAMPUS: power user (strongest model, research, vision, deep analysis)
    _HIPPOCAMPUS = _THALAMUS | {
        Capability.DEEP_ANALYSIS,
        Capability.RESEARCH,
        Capability.VISION,
    }

    # IRAOS: not in V1. Not granted to any tier yet.
    # Show as "Coming soon" in the UI. When ready, add to HIPPOCAMPUS.
    COMING_SOON = frozenset({
        Capability.BROWSER,
        Capability.COMPUTER_USE,
        Capability.AUTONOMOUS_WORK,
    })

    _TIER_ORDER = (
        BrainTier.FREE,
        BrainTier.STARTER,
        BrainTier.BRAIN_MINI,
        BrainTier.BRAIN_ORION,
        BrainTier.THALAMUS,
        BrainTier.HIPPOCAMPUS,
    )

    _POLICY = {
        BrainTier.FREE: _FREE,
        BrainTier.STARTER: _STARTER,
        BrainTier.BRAIN_MINI: _BRAIN_MINI,
        BrainTier.BRAIN_ORION: _BRAIN_ORION,
        BrainTier.THALAMUS: _THALAMUS,
        BrainTier.HIPPOCAMPUS: _HIPPOCAMPUS,
    }

    @classmethod
    def allows(
        cls,
        tier: BrainTier,
        capability: Capability,
    ) -> bool:
        return capability in cls._POLICY.get(tier, frozenset())

    @classmethod
    def capabilities_for(
        cls,
        tier: BrainTier,
    ) -> frozenset[Capability]:
        return frozenset(cls._POLICY.get(tier, frozenset()))

    @classmethod
    def minimum_tier_for(
        cls,
        capability: Capability,
    ) -> BrainTier | None:
        """Lowest tier that unlocks a capability (for upgrade prompts)."""
        for tier in cls._TIER_ORDER:
            if capability in cls._POLICY[tier]:
                return tier
        return None