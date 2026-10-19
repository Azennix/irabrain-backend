from brain.tier.capabilities import Capability
from brain.tier.capability_requirement import CapabilityRequirement


class CapabilityResolver:

    @staticmethod
    def resolve(analysis, intent) -> CapabilityRequirement:
        if analysis is None:
            raise ValueError("Message analysis is required.")

        if intent is None:
            raise ValueError("Intent result is required.")

        # Tool-dependent requests
        if intent.requires_tool:
            return CapabilityRequirement(
                capability=Capability.TOOLS,
                confidence=intent.confidence,
            )

        # Reasoning-dependent requests
        if intent.requires_reasoning:
            return CapabilityRequirement(
                capability=Capability.REASONING,
                confidence=intent.confidence,
            )

        # Memory-related requests
        if (
            intent.requires_memory
            or analysis.requires_memory_retrieval
        ):
            return CapabilityRequirement(
                capability=Capability.MEMORY,
                confidence=intent.confidence,
            )

        # Default conversational capability
        return CapabilityRequirement(
            capability=Capability.BASIC_CHAT,
            confidence=analysis.confidence,
        )