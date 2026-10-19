from enum import Enum


class Capability(str, Enum):
    BASIC_CHAT = "basic_chat"
    REASONING = "reasoning"
    DEEP_REASONING = "deep_reasoning"

    CODING = "coding"
    ADVANCED_CODING = "advanced_coding"

    ANALYSIS = "analysis"
    DEEP_ANALYSIS = "deep_analysis"

    MEMORY = "memory"
    LARGE_CONTEXT = "large_context"

    RESEARCH = "research"
    VISION = "vision"
    DOCUMENT_ANALYSIS = "document_analysis"

    TOOLS = "tools"
    BROWSER = "browser"
    COMPUTER_USE = "computer_use"

    AUTONOMOUS_WORK = "autonomous_work"