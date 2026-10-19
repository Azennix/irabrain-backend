from types import SimpleNamespace

from brain.tier.capabilities import Capability
from brain.tier.capability_resolver import CapabilityResolver


def test_tool_intent_requires_tools():
    analysis = SimpleNamespace(
        requires_memory_retrieval=False,
        confidence=0.9,
    )

    intent = SimpleNamespace(
        requires_tool=True,
        requires_reasoning=False,
        requires_memory=False,
        confidence=0.95,
    )

    requirement = CapabilityResolver.resolve(
        analysis=analysis,
        intent=intent,
    )

    assert requirement.capability == Capability.TOOLS
    print("TOOL CAPABILITY PASS")


def test_reasoning_intent_requires_reasoning():
    analysis = SimpleNamespace(
        requires_memory_retrieval=False,
        confidence=0.9,
    )

    intent = SimpleNamespace(
        requires_tool=False,
        requires_reasoning=True,
        requires_memory=False,
        confidence=0.95,
    )

    requirement = CapabilityResolver.resolve(
        analysis=analysis,
        intent=intent,
    )

    assert requirement.capability == Capability.REASONING
    print("REASONING CAPABILITY PASS")


def test_memory_requirement_requires_memory():
    analysis = SimpleNamespace(
        requires_memory_retrieval=True,
        confidence=0.9,
    )

    intent = SimpleNamespace(
        requires_tool=False,
        requires_reasoning=False,
        requires_memory=False,
        confidence=0.95,
    )

    requirement = CapabilityResolver.resolve(
        analysis=analysis,
        intent=intent,
    )

    assert requirement.capability == Capability.MEMORY
    print("MEMORY CAPABILITY PASS")


def test_default_intent_requires_basic_chat():
    analysis = SimpleNamespace(
        requires_memory_retrieval=False,
        confidence=0.9,
    )

    intent = SimpleNamespace(
        requires_tool=False,
        requires_reasoning=False,
        requires_memory=False,
        confidence=0.95,
    )

    requirement = CapabilityResolver.resolve(
        analysis=analysis,
        intent=intent,
    )

    assert requirement.capability == Capability.BASIC_CHAT
    print("BASIC CHAT CAPABILITY PASS")


if __name__ == "__main__":
    test_tool_intent_requires_tools()
    test_reasoning_intent_requires_reasoning()
    test_memory_requirement_requires_memory()
    test_default_intent_requires_basic_chat()
    print("\nCAPABILITY RESOLVER TESTS PASS")