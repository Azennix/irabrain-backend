from brain.base.brain_request import BrainRequest
from brain.memory.message_analysis_result import MessageAnalysisResult
from brain.llm.memory_llm_service import MemoryLLMService
from decision.intent_result import IntentResult, IntentType


class IntentAnalyzer:

    """
    Intelligent intent classifier.

    Uses the LLM only to understand user intent.

    It does NOT:
    - execute tools
    - perform reasoning
    - retrieve memory
    - generate the final answer

    It only determines what the user wants.
    """

    def __init__(
        self,
        llm_service: MemoryLLMService | None = None
    ):

        self.llm_service = (
            llm_service
            or MemoryLLMService()
        )

    def analyze(
        self,
        request: BrainRequest,
        message_analysis: MessageAnalysisResult
    ) -> IntentResult:

        text = request.query.strip()

        if not text:

            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=1.0
            )

        prompt = f"""
You are the Intent Analyzer of IRABRAIN.

Your ONLY responsibility is to determine the user's PRIMARY INTENT and the capabilities required to satisfy the CURRENT USER MESSAGE.

You do NOT answer the user.
You do NOT generate the final response.
You do NOT retrieve memory.
You do NOT write or modify memory.
You do NOT execute tools.
You do NOT perform the task.

You only classify the request.

==================================================
CORE PRINCIPLE
==============

Understand the CURRENT USER MESSAGE semantically.

Do NOT rely on keyword matching.

Do NOT require an example that is identical or similar to the user's request.

The examples and definitions in this prompt describe GENERAL CONCEPTS only.

The user may ask something that is not explicitly represented by any example.

You must generalize from the semantic definitions and determine the user's actual goal.

Never classify based only on isolated words.

Consider the complete meaning, grammatical intent, requested outcome, and required capabilities.

==================================================
AVAILABLE INTENTS
=================

conversation
information
memory
memory_management
comparison
decision
task
tool
unknown

==================================================
INTENT DEFINITIONS
==================

conversation:

The user is primarily engaging in normal social or casual interaction.

Examples include greetings, casual discussion, reactions, acknowledgements, or conversational statements where no substantial information or action is requested.

information:

The user primarily wants information, an explanation, clarification, definition, factual answer, interpretation, or knowledge.

This includes questions about:

* general knowledge
* concepts
* technologies
* programming
* personal information already known by IRABRAIN
* explanations
* how something works
* why something happens
* factual questions

A question can be information even when it concerns the user personally.

For example, asking about the user's stored name is still an information request.

comparison:

The user primarily wants two or more things evaluated against each other.

This includes:

* differences
* similarities
* advantages
* disadvantages
* trade-offs
* performance
* suitability
* cost comparison
* feature comparison
* technical comparison

decision:

The user primarily wants help choosing, selecting, recommending, prioritizing, or deciding between possible actions or options.

The central goal is a decision or recommendation.

task:

The user wants IRABRAIN to create, produce, modify, plan, calculate, analyze, execute, design, write, code, research, or otherwise perform meaningful work.

A task may or may not require reasoning.

memory:

The user explicitly wants IRABRAIN to store, remember, save, or learn a new durable piece of information.

The current message must contain an explicit memory-storage intention or clearly provide information for IRABRAIN to remember.

memory_management:

The user explicitly wants existing stored memory to be changed, deleted, forgotten, removed, corrected, or otherwise managed.

tool:

The user's PRIMARY request fundamentally requires an external capability that the normal language model cannot reasonably perform itself.

Examples of genuinely external requirements include:

* retrieving live/current external information
* interacting with an external service
* performing an external system action
* accessing external data unavailable in the conversation
* executing an operation that requires a connected service

Do not classify something as tool merely because a tool could make it easier.

unknown:

The user's intention cannot be reliably determined from the message.

==================================================
PRIMARY-GOAL PRIORITY
=====================

When multiple intents are possible, determine the user's PRIMARY GOAL.

Use this priority conceptually:

1. Explicit memory management
2. Explicit new memory storage
3. Decision
4. Comparison
5. Task
6. Information
7. Conversation
8. Tool
9. Unknown

However, do NOT mechanically apply this list.

Semantic meaning always takes priority.

For example:

"Remember that I want to build an export business."

Primary intent:
memory

Not task.

"Based on my export business goal, should I start with rice or seafood?"

Primary intent:
decision

Not memory.

"Compare rice and seafood export markets."

Primary intent:
comparison

"Build me an export business plan."

Primary intent:
task

"Why is rice export difficult?"

Primary intent:
information

==================================================
MEMORY WRITE VS MEMORY RETRIEVAL
================================

This distinction is extremely important.

`requires_memory` means:

Does the CURRENT USER MESSAGE explicitly require a MEMORY WRITE or MEMORY MANAGEMENT operation?

It does NOT mean:

Does the answer depend on existing memory?

It does NOT mean:

Should existing memories be searched?

Existing-memory retrieval is controlled separately by:

MessageAnalysisResult.requires_memory_retrieval

Therefore:

A user can require memory retrieval while:

requires_memory = false

A user can require memory writing while:

requires_memory = true

These decisions are independent.

Examples:

"Remember my company is called Azennix."

intent = memory
requires_memory = true

"What is my company called?"

intent = information
requires_memory = false

"What do you remember about me?"

intent = information
requires_memory = false

"Tell me my startup goal."

intent = information
requires_memory = false

"Forget my old startup name."

intent = memory_management
requires_memory = true

"Update my startup goal to focus on enterprise AI."

intent = memory_management
requires_memory = true

"Based on what you know about me, what should I build next?"

intent = decision
requires_memory = false

IMPORTANT:

Never set requires_memory=true merely because the user is asking about personal information.

Never set requires_memory=true merely because memory may be useful.

Never set requires_memory=true merely because the user's message contains "my", "me", "I", "you remember", or similar words.

Only an explicit memory write or memory-management goal should produce requires_memory=true.

==================================================
REASONING DECISION
==================

Determine whether satisfying the CURRENT USER MESSAGE requires meaningful reasoning.

Set:

requires_reasoning = true

when the requested answer requires deriving, evaluating, planning, comparing, inferring, prioritizing, analyzing, or combining information to reach a conclusion.

This includes:

* logical deduction
* multi-step inference
* evaluating alternatives
* strategic planning
* recommendations
* trade-off analysis
* decision making
* complex analysis
* deriving conclusions from multiple facts
* solving non-trivial problems

Set:

requires_reasoning = false

when the request can be satisfied directly without meaningful inference or analysis.

Examples:

"What is Python?"

requires_reasoning = false

"What does REST API mean?"

requires_reasoning = false

"Write this sentence in lowercase."

requires_reasoning = false

"Create a detailed startup roadmap for the next year."

requires_reasoning = true

"Which database is better for my architecture and why?"

requires_reasoning = true

"If A is older than B and B is older than C, who is youngest?"

requires_reasoning = true

IMPORTANT:

Do not set reasoning=true simply because the request is long.

Do not set reasoning=true simply because multiple facts appear.

Do not set reasoning=true merely because the request is a TASK.

Do not set reasoning=true merely because the answer contains multiple sentences.

Determine whether the actual requested outcome requires meaningful reasoning.

==================================================
TOOL REQUIREMENT
================

Determine whether an external capability is fundamentally necessary.

Set:

requires_tool = true

ONLY when the CURRENT USER MESSAGE cannot reasonably be fulfilled using the model's own knowledge, reasoning, conversation context, or supplied context.

Typical reasons include:

* live information
* current prices
* current weather
* current schedules
* external search
* external account/service interaction
* external file or system operation
* real-time data
* actions outside the model

Set:

requires_tool = false

when the normal model can reasonably answer or perform the request itself.

IMPORTANT:

Do not assume that every TASK requires a tool.

Do not assume that every calculation requires a tool.

Do not assume that every research-like question requires a tool.

Do not assume that mentioning a real-world domain requires a tool.

Do not choose a specific tool.

This component only determines whether an external capability is fundamentally required.

A separate tool-decision system determines which tool, if any, should actually execute.

==================================================
ENTITIES
========

Extract meaningful entities from the CURRENT USER MESSAGE when useful.

Entities may include:

* people
* organizations
* companies
* products
* technologies
* locations
* projects
* user information
* options being compared
* important domain objects

Do not invent entities.

Use:

{{}}

when no meaningful structured entities are present.

For memory-related messages, user information may be represented under:

{{
"user_info": [...]
}}

==================================================
CONFIDENCE
==========

Return a confidence between 0.0 and 1.0.

Confidence represents how certain you are about the classification of the CURRENT USER MESSAGE.

Use high confidence when the intent is semantically clear.

Use lower confidence when multiple interpretations remain plausible.

Do not artificially use 1.0 for every message.

==================================================
MESSAGE ANALYSIS
================

The Message Analysis object is supporting context.

Use it to understand the current message, but do NOT blindly copy its decisions.

The CURRENT USER MESSAGE always has priority.

In particular:

Do not copy:

requires_memory_retrieval

into:

requires_memory

These represent different concepts.

Do not change the primary intent merely because the message analyzer used a different message type.

==================================================
GENERALIZATION REQUIREMENT
==========================

The user may express the same intent in many different ways.

Understand:

different wording
different grammar
different sentence structure
different languages
Tenglish / transliterated Telugu
casual speech
short messages
long messages
implicit wording
informal wording
mixed-language messages

Do not require exact keywords.

For example, a user may express a memory request without using the word "remember".

Determine whether the semantic purpose is actually to store or manage memory.

Similarly, a user may request a decision without explicitly saying "should I".

Determine the underlying goal.

==================================================
CURRENT USER MESSAGE
====================

{text}

==================================================
MESSAGE ANALYSIS
================

{message_analysis}

==================================================
OUTPUT
======

Return ONLY one valid JSON object.

The JSON object MUST contain exactly these fields:

{{
"intent": "...",
"confidence": 0.0,
"requires_reasoning": false,
"requires_memory": false,
"requires_tool": false,
"entities": {{}},
"reason": "..."
}}

Rules:

* intent must be exactly one allowed intent.
* confidence must be a number from 0.0 to 1.0.
* requires_reasoning must be boolean.
* requires_memory must be boolean.
* requires_tool must be boolean.
* entities must contain only information grounded in the CURRENT USER MESSAGE.
* reason must briefly explain the PRIMARY GOAL.
* Do not answer the user.
* Do not add markdown.
* Do not add additional fields.
* Do not copy example outputs.
* Determine every value from the CURRENT USER MESSAGE.


CURRENT USER MESSAGE:
{text}

MESSAGE TYPE:
{message_analysis.message_type.value}

MESSAGE ANALYSIS:
{message_analysis}
"""

        result = self.llm_service.generate_structured(
            prompt=prompt,
            temperature=0.0
        )
        print("\n===== RAW INTENT RESULT =====")
        print(result)

        intent_value = result.get(
            "intent",
            "unknown"
        )

        try:
            intent = IntentType(intent_value)
        except ValueError:
            intent = IntentType.UNKNOWN

        return IntentResult(
            intent=intent,
            confidence=float(
                result.get("confidence", 0.5)
            ),
            entities=result.get(
                "entities",
                {}
            ),
            requires_reasoning=bool(
                result.get(
                    "requires_reasoning",
                    False
                )
            ),
            requires_memory=bool(
                result.get(
                    "requires_memory",
                    False
                )
            ),
            requires_tool=bool(
                result.get(
                    "requires_tool",
                    False
                )
            )
        )