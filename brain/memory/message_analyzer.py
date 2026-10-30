from typing import Any

from brain.memory.message_analysis_result import (
    MessageAnalysisResult,
    MessageType,
    ConversationScore,
)
from brain.semantic.semantic_analysis_result import (
    SemanticAnalysisResult,
)
from decision.intent_result import IntentType


class MessageAnalyzer:

    """
    Analyzes the user's message using ONE specialized LLM call.

    Responsibilities:

    1. Message classification
    2. Memory-pipeline decision
    3. LLM requirement decision
    4. Language classification
    5. Script detection
    6. Mixed-language detection
    7. Transliteration detection
    8. Tone detection
    9. Response-style detection
    10. Conversation relevance scoring

    This class DOES NOT:

    - generate the final response
    - execute tools
    - perform reasoning
    - retrieve memory
    - translate responses
    """

    def __init__(self, llm_service):

        self.llm_service = llm_service

    # =====================================================
    # MAIN ANALYSIS
    # =====================================================

    def analyze(
        self,
        request,
        conversation_history
    ) ->  SemanticAnalysisResult:

        current_message = (
            getattr(request, "query", None)
            or ""
        ).strip()
        fast_result = self._try_fast_path(current_message)

        if fast_result is not None:
            return fast_result


        prompt = f"""
You are the semantic message-analysis layer of IRABrain.

Your ONLY job is to analyze the CURRENT USER MESSAGE.

Do not answer the user.
Do not perform the requested task.
Do not give advice.
Do not retrieve memory.
Do not execute tools.
Do not generate the final response.

Return ONLY one valid JSON object matching the required schema.

==================================================
CORE PRINCIPLE
==================================================

Understand the CURRENT USER MESSAGE by its semantic meaning.

Do NOT classify using keyword matching.

Do NOT require a predefined example for every possible topic,
product, business, profession, project, technology, hobby,
goal, or situation.

The examples in this instruction are demonstrations of
semantic patterns, not an exhaustive vocabulary.

Generalize the semantic rules to new and unseen domains.

The topic of a message does NOT determine its intent.

For example, AI, export, healthcare, finance, education,
robotics, trading, software, or any other topic can appear
inside CHAT, QUESTION, COMMAND, MEMORY, TASK, or UNKNOWN.

Determine what the user is communicating or asking to do
with the topic.




intent:
Determine the PRIMARY intent of the CURRENT USER MESSAGE.

Allowed values:
conversation
information
memory
memory_management
comparison
decision
task
tool
unknown

intent_confidence:
Confidence in the primary intent.

entities:
Return meaningful entities grounded in the CURRENT USER MESSAGE.
Do not invent entities.
Return {{}} when none exist.

requires_reasoning:
Whether satisfying the request requires meaningful reasoning.

requires_memory:
TRUE only when the user explicitly wants memory to be
written, changed, deleted, forgotten, or otherwise managed.

requires_tool:
TRUE only when an external capability is fundamentally required.

IMPORTANT:
These fields describe the CURRENT USER MESSAGE.
Do not use memory retrieval requirements for requires_memory.

Memory retrieval remains ALWAYS-ON and is controlled by the
system architecture, not this analyzer.

==================================================
CURRENT USER MESSAGE
==================================================

{current_message}

==================================================
CONVERSATION CONTEXT
==================================================

{conversation_history}

Previous conversation is context only.

Never treat previous user messages or previous assistant
responses as the CURRENT USER MESSAGE.

Use previous conversation only when necessary to understand
the meaning of the current message or to evaluate relevance.

==================================================
1. MESSAGE TYPE
==================================================

Determine the primary semantic type of the CURRENT USER MESSAGE.

Allowed values:

CHAT
QUESTION
COMMAND
MEMORY
TASK
UNKNOWN

CHAT:
The user is mainly participating in ordinary conversation,
social interaction, greeting, acknowledgement, or casual talk.

QUESTION:
The user primarily asks for information, explanation,
knowledge, clarification, or a factual answer.

COMMAND:
The user directly asks IRABrain to perform an action,
change something, or manage something.

MEMORY:
The user communicates durable information about themselves
that may be useful to remember.

This includes durable:

- identity
- preferences
- goals
- plans
- education
- occupation
- career direction
- projects
- businesses
- relationships
- important constraints
- long-term interests
- persistent circumstances

A personal statement remains MEMORY even when expressed
casually, emotionally, indirectly, or with conversational
words.

A personal goal or intention is still personal information.

TASK:
The user asks IRABrain to perform meaningful work such as:

- planning
- creating
- analyzing
- researching
- calculating
- coding
- designing
- comparing
- solving
- generating
- organizing
- executing a substantive request

UNKNOWN:
The semantic purpose cannot be determined with reasonable
confidence.

==================================================
2. MEMORY-WRITE DECISION
==================================================

Determine whether the CURRENT USER MESSAGE contains a durable
personal fact that should potentially enter the memory pipeline.

Set:

should_enter_memory_pipeline = true

when the user communicates information about themselves that
could remain useful beyond the current turn.

This is a semantic decision.

Do not depend on specific keywords or examples.

Personal information may be expressed as:

- a statement
- a goal
- a preference
- a plan
- an intention
- a project description
- a business direction
- an ongoing activity
- a persistent constraint

IMPORTANT MEMORY-FIRST RULE:

If the CURRENT USER MESSAGE communicates information about
the user, treat it as eligible for the memory pipeline.

Do NOT reject personal information merely because it appears
temporary, casual, ordinary, emotional, or low-importance.

Examples:

"Today I ate cake."
→ should_enter_memory_pipeline = true

"I am tired today."
→ true

"I am working on my startup."
→ true

"I want to build an export business."
→ true

"I like dark mode."
→ true

"I am studying diploma."
→ true

"Bro I'm going to college tomorrow."
→ true

The purpose of this analyzer is to detect whether the message
contains user-related information that may be passed to the
memory system.

Memory importance, usefulness, retention priority, and whether
the information should ultimately be stored permanently MUST be
decided by the memory extraction / validation / importance
pipeline, not by this analyzer.

Therefore:

PERSONAL INFORMATION → should_enter_memory_pipeline = true

NON-PERSONAL INFORMATION → should_enter_memory_pipeline = false

A user can therefore communicate a durable fact without
explicitly saying "remember this".


==================================================
4. LLM REQUIREMENT
==================================================

Determine whether the normal language model is required to
produce the response.

Set:

requires_llm = true

when the response requires natural-language understanding,
generation, explanation, conversation, reasoning, planning,
creative work, interpretation, or substantive task handling.

Set:

requires_llm = false

ONLY when the request can be completely handled by a
deterministic system component without meaningful language
generation or interpretation.

Do not set requires_llm based merely on message type.

==================================================
5. LANGUAGE
==================================================

Identify the PRIMARY language of the CURRENT USER MESSAGE.

Allowed values:

en
te
hi
ta
kn
ml
other

Determine language from linguistic structure and meaning.

Do NOT infer language from:

- user location
- user identity
- previous conversation
- the word "bro"
- a topic such as AI or startup
- Latin script alone

English written naturally in Latin characters is English.

Telugu written using Latin characters is Telugu transliteration
when the linguistic structure is genuinely Telugu.

The same principle applies to Hindi, Tamil, Kannada, and Malayalam.

Do not confuse transliteration with ordinary English.

==================================================
6. SCRIPT
==================================================

Allowed values:

latin
telugu
devanagari
tamil
kannada
malayalam
other

Determine the actual writing system of the CURRENT USER MESSAGE.

Examples are not required for every language.

==================================================
7. MIXED LANGUAGE
==================================================

Determine whether the CURRENT USER MESSAGE genuinely contains
multiple languages.

Set:

is_mixed = true

only when two or more languages materially contribute to the
message.

Do not consider ordinary conversational words such as:

bro
hi
hello
okay
ok
yes
no
thanks

sufficient evidence of a second language.

Set secondary_language to the meaningful secondary language,
or null when there is none.

==================================================
8. TRANSLITERATION
==================================================

Set:

is_transliterated = true

when a language normally written in another script is written
using Latin characters.

For example, Telugu linguistic structure written with Latin
characters is Telugu transliteration.

Natural spelling variation in transliteration is allowed.

Latin script by itself does NOT mean transliteration.

==================================================
9. TONE
==================================================

Determine the user's overall tone.

Allowed values:

casual
neutral
formal
professional

Determine tone from the complete CURRENT USER MESSAGE.

Do not infer tone merely from one word such as "bro".

==================================================
10. RESPONSE STYLE
==================================================

Determine the style that best matches the CURRENT USER MESSAGE.

Allowed values:

casual_tenglish
telugu
casual_english
casual_mixed
formal_telugu
professional_english
standard

Response style must follow the actual linguistic and
conversational characteristics of the current message.

Do not select casual_tenglish merely because:

- the message uses Latin characters
- the message contains "bro"
- the user previously used Telugu

Do not select a style based on previous messages.

==================================================
11. CONVERSATION RELEVANCE
==================================================

For every supplied recent conversation message, return one
relevance score.

Score:

0.0 = irrelevant
0.5 = somewhat relevant
1.0 = highly relevant

Judge relevance to the CURRENT USER MESSAGE semantically.

Do not judge relevance using keyword overlap alone.

Return exactly one score object for every supplied recent
conversation message.

Each score object must contain:

message_id
score
reasoning

==================================================
12. SEMANTIC PRIORITY
==================================================

When signals appear to conflict, determine the user's actual
semantic purpose.

Do not let:

- casual wording
- greetings
- politeness
- "bro"
- punctuation
- topic vocabulary
- previous language
- previous intent
- message length

override the semantic meaning of the CURRENT USER MESSAGE.

A statement about the user's durable personal information is
MEMORY even when casual.

A request about stored personal information requires memory
retrieval even when classified as QUESTION or CHAT.

A task does not automatically require a tool.

A task does not automatically require reasoning.

A topic does not determine intent.

==================================================
13. IMPORTANT DISTINCTIONS
==================================================

Distinguish:

PERSONAL INFORMATION
from
REQUEST TO PERFORM WORK.

Distinguish:

MEMORY WRITE
from
MEMORY RETRIEVAL.

Distinguish:

TASK
from
TOOL REQUIREMENT.

Distinguish:

LANGUAGE
from
SCRIPT.

Distinguish:

TRANSLITERATION
from
LATIN-SCRIPT ENGLISH.

Distinguish:

TOPIC
from
INTENT.

These dimensions must be decided independently.

==================================================
14. TOOL REQUIREMENT
==================================================

Set:

requires_tool = true

ONLY when the CURRENT USER MESSAGE fundamentally requires an
external capability or external/current information that the
normal language model cannot reasonably provide by itself.

Examples of external dependencies include current external
information, live data, external services, or actions requiring
access outside the model.

Do NOT set requires_tool=true merely because:

- the message is a TASK
- the message contains an action
- the message concerns a business
- the message concerns a project
- the message concerns software
- the message concerns exports
- the message concerns AI
- the message sounds complicated

The existence of a task and the existence of an external-tool
requirement are separate decisions.

The specific tool must NOT be selected here.

A separate tool-decision system will determine which tool,
if any, should execute.

==================================================
15. REASONING
==================================================

Do not perform the user's requested reasoning.

This analyzer only determines the classification metadata.

requires_llm describes whether language-model generation is
needed for the eventual response.

Do not add a separate reasoning field to this analyzer schema.

==================================================
MEMORY RETRIEVAL ARCHITECTURE
==================================================

IMPORTANT:

This analyzer does NOT decide whether memory retrieval should
happen.

IRABrain uses an always-recall architecture.

Every valid CURRENT USER MESSAGE must be allowed to enter the
memory-retrieval system.

Therefore, memory retrieval MUST NOT be inferred from:

- message type
- intent
- keywords
- topic
- whether the user explicitly asks to remember something
- whether the message appears personal
- whether the message appears to need memory

The analyzer must focus only on its own classification
responsibilities.

The memory-retrieval pipeline is controlled by the system
architecture, not by this LLM classification.

The retrieval system will independently determine which
existing memories are relevant to the CURRENT USER MESSAGE.

The system should retrieve relevant memories for every user
message and allow the retrieval/ranking pipeline to filter
irrelevant memories.

Examples:

"hello bro"
→ retrieval is still performed

"what is Python?"
→ retrieval is still performed

"what am I working on?"
→ retrieval is still performed

"am I making progress?"
→ retrieval is still performed

"should I continue with this project?"
→ retrieval is still performed

"explain quantum physics"
→ retrieval is still performed

The analyzer MUST NOT output a memory-retrieval decision.

==================================================
15B. VISUAL
==================================================

needs_visual:
TRUE only when a diagram, graph or chart would help the user
understand the ANSWER better than text alone.
FALSE for greetings, thanks, casual chat, personal statements,
simple facts, opinions, short answers and plain advice.

visual_type_hint:
When needs_visual is true, choose the type that fits the
QUESTION. Do not default to flowchart.

- flowchart: a step-by-step process or algorithm
- system_architecture: components, layers, services, data flow
- connection_graph: relationships between many entities
- concept_map: one central idea with related parts
- hierarchy: levels, org structure, parent-child
- decision_tree: choices with branching outcomes
- comparison: two or more options against criteria
- timeline: events over time
- cycle: a repeating loop
- data_chart: numbers or statistics explicitly asked for
- steps: a simple ordered how-to

When needs_visual is false, visual_type_hint is null.

==================================================
16. OUTPUT
==================================================

Return ONLY one valid JSON object.

The object MUST contain exactly these fields:

message_type
should_enter_memory_pipeline
requires_llm
language
script
is_mixed
secondary_language
is_transliterated
tone
response_style
confidence
conversation_scores
intent
intent_confidence
entities
requires_reasoning
requires_memory
requires_tool
needs_visual
visual_type_hint

Types:

message_type:
one allowed message type string

should_enter_memory_pipeline:
boolean



requires_llm:
boolean

needs_visual:
boolean

visual_type_hint:
one allowed visual type string, or null

language:
one allowed language code
script:
one allowed script

is_mixed:
boolean

secondary_language:
allowed language code or null

is_transliterated:
boolean

tone:
one allowed tone

response_style:
one allowed response style

confidence:
number from 0.0 to 1.0

conversation_scores:
array containing one object per supplied recent conversation
message.

Each conversation score object must contain:

message_id
score
reasoning

==================================================
FINAL VALIDATION
==================================================

Before returning JSON:

1. Analyze only the CURRENT USER MESSAGE for message decisions.
2. Use conversation history only as context.
3. Determine message type semantically.
4. Determine memory writing independently.
5. Determine LLM requirement independently.
6. Determine tool requirement independently.
7. Determine language from linguistic structure.
8. Determine script from writing system.
9. Determine transliteration from language/script relationship.
10. Determine mixed language from genuine language presence.
11. Determine tone from the complete message.
12. Determine response style from actual language and tone.
13. Score every supplied conversation message.
14. Do not use topic-specific hardcoding.
15. Do not rely on examples as an exhaustive list.
16. Return valid JSON only.






"""



        result = self.llm_service.generate_structured(
            prompt=prompt,
            temperature=0.0
        )



        return self._normalize_result(
            result
        )







    # =====================================================
    # NORMALIZE RESULT
    # =====================================================

    def _normalize_result(
        self,
        result: dict[str, Any]
    ) ->  SemanticAnalysisResult:

        if not isinstance(result, dict):

            result = {}

        # =================================================
        # MESSAGE TYPE
        # =================================================

        message_type = self._normalize_message_type(
            result.get(
                "message_type",
                "UNKNOWN"
            )
        )



        # =================================================
        # CONVERSATION SCORES
        # =================================================

        conversation_scores = (
            self._normalize_conversation_scores(
                result.get(
                    "conversation_scores",
                    []
                )
            )
        )

        # =================================================
        # FINAL OBJECT
        # =================================================

        return SemanticAnalysisResult(
            message_type=message_type,

            intent=self._normalize_intent(
                result.get("intent", "unknown")
    ),

            intent_confidence=self._safe_float(
                result.get("intent_confidence", 0.0)
    ),

            entities=(
                result.get("entities", {})
                if isinstance(result.get("entities", {}), dict)
                else {}
    ),

            requires_reasoning=bool(
                result.get("requires_reasoning", False)
    ),

            requires_memory=bool(
                result.get("requires_memory", False)
    ),

            requires_tool=bool(
                result.get("requires_tool", False)
    ),

            should_enter_memory_pipeline=bool(
                result.get(
                    "should_enter_memory_pipeline",
                  False
        )
    ),

    # Always-on retrieval remains deterministic.
            requires_memory_retrieval=True,

            language=self._safe_string(
                result.get("language", "en"),
                "en"
            ).lower(),

            script=self._safe_string(
                result.get("script", "latin"),
               "latin"
               ).lower(),

            is_mixed=bool(
                result.get("is_mixed", False)
    ),

            secondary_language=(
                self._normalize_optional_language(
                    result.get("secondary_language")
        )
    ),

            is_transliterated=bool(
                result.get("is_transliterated", False)
    ),

            tone=self._safe_string(
                result.get("tone", "neutral"),
                "neutral"
            ).lower(),

            response_style=self._safe_string(
                result.get("response_style", "standard"),
                "standard"
            ).lower(),

            requires_llm=bool(
                result.get("requires_llm", True)
    ),
            needs_visual=bool(result.get("needs_visual", False)),

            visual_type_hint=self._normalize_visual_hint(
                result.get("visual_type_hint")
            ),

            confidence=self._safe_float(
                result.get("confidence", 0.7)
    ),

            conversation_scores=conversation_scores,
)
    @staticmethod
    def _normalize_intent(
    value
    ) -> IntentType:

        value = str(
            value or "unknown"
        ).strip().lower()

        allowed = {
        "conversation": IntentType.CONVERSATION,
        "information": IntentType.INFORMATION,
        "memory": IntentType.MEMORY,
        "memory_management": IntentType.MEMORY_MANAGEMENT,
        "comparison": IntentType.COMPARISON,
        "decision": IntentType.DECISION,
        "task": IntentType.TASK,
        "tool": IntentType.TOOL,
        "unknown": IntentType.UNKNOWN,
    }

        return allowed.get(
            value,
            IntentType.UNKNOWN
    )



    def to_message_analysis_result(
        self,
        result: SemanticAnalysisResult,
    ) -> MessageAnalysisResult:

        return MessageAnalysisResult(
            message_type=result.message_type,
            should_enter_memory_pipeline=(
                result.should_enter_memory_pipeline
        ),
            requires_memory_retrieval=(
                result.requires_memory_retrieval
        ),
            requires_llm=result.requires_llm,
            confidence=result.confidence,
            language=result.language,
            script=result.script,
            is_mixed=result.is_mixed,
            secondary_language=result.secondary_language,
            is_transliterated=result.is_transliterated,
            tone=result.tone,
            response_style=result.response_style,
            conversation_scores=result.conversation_scores,
    )


    def to_intent_result(
        self,
        result: SemanticAnalysisResult,
):
        from decision.intent_result import IntentResult

        return IntentResult(
            intent=result.intent,
            confidence=result.intent_confidence,
            entities=result.entities,
            requires_reasoning=result.requires_reasoning,
            requires_memory=result.requires_memory,
            requires_tool=result.requires_tool,
    )





















    # =====================================================
    # MESSAGE TYPE
    # =====================================================

    @staticmethod
    def _normalize_message_type(
        value
    ) -> MessageType:

        value = str(
            value or "UNKNOWN"
        ).strip().upper()

        allowed = {

            "CHAT": MessageType.CHAT,

            "QUESTION": MessageType.QUESTION,

            "COMMAND": MessageType.COMMAND,

            "MEMORY": MessageType.MEMORY,

            "TASK": MessageType.TASK,

            "UNKNOWN": MessageType.UNKNOWN,

            # Backward-compatible handling
            "GREETING": MessageType.CHAT,

            "OTHER": MessageType.UNKNOWN
        }

        return allowed.get(
            value,
            MessageType.UNKNOWN
        )

    # =====================================================
    # CONVERSATION SCORE NORMALIZATION
    # =====================================================

    @staticmethod
    def _normalize_conversation_scores(
        scores
    ) -> list[ConversationScore]:

        if not isinstance(
            scores,
            list
        ):

            return []

        normalized = []

        for item in scores:

            if not isinstance(
                item,
                dict
            ):

                continue

            message_id = item.get(
                "message_id"
            )

            if message_id is None:

                continue

            normalized.append(
                ConversationScore(

                    message_id=str(
                        message_id
                    ),

                    score=MessageAnalyzer._safe_float(
                        item.get(
                            "score",
                            0.0
                        )
                    ),

                    reasoning=str(
                        item.get(
                            "reasoning",
                            ""
                        )
                    )
                )
            )

        return normalized

    # =====================================================
    # STRING SAFETY
    # =====================================================

    @staticmethod
    def _safe_string(
        value,
        default: str
    ) -> str:

        if value is None:

            return default

        value = str(
            value
        ).strip()

        return value or default

    # =====================================================
    # FLOAT SAFETY
    # =====================================================

    @staticmethod
    def _safe_float(
        value
    ) -> float:

        try:

            value = float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            return 0.7

        return max(
            0.0,
            min(
                1.0,
                value
            )
        )

    # =====================================================
    # OPTIONAL LANGUAGE
    # =====================================================

    @staticmethod
    def _normalize_optional_language(
        value
    ):

        if value is None:

            return None

        value = str(
            value
        ).strip().lower()

        if not value:

            return None

        if value in {
            "none",
            "null",
            "unknown"
        }:

            return None

        return value

    @staticmethod
    def _normalize_visual_hint(value):
        allowed = {
            "flowchart", "system_architecture", "connection_graph",
            "concept_map", "hierarchy", "decision_tree", "comparison",
            "timeline", "cycle", "data_chart", "steps",
        }
        value = str(value or "").strip().lower()
        return value if value in allowed else None

    def _try_fast_path(self, message: str):
        """
        IRABRAIN lightweight conversational classifier.

        Supports:
          - English
          - Telugu transliteration

        Only classifies explicitly recognized, simple messages.
         Ambiguous or unsupported messages return None and continue
        through the existing semantic LLM analyzer.

        Memory retrieval remains ALWAYS-ON.
        """

        import re

        from brain.memory.message_analysis_result import MessageType
        from brain.semantic.semantic_analysis_result import (
        SemanticAnalysisResult,
    )
        from decision.intent_result import IntentType

        if not isinstance(message, str) or not message.strip():
            return None

    # -------------------------------------------------
    # 1. NORMALIZE
    # -------------------------------------------------

        normalized = message.casefold().strip()

    # Normalize common apostrophe variants.
        normalized = (
            normalized
            .replace("’", "'")
            .replace("‘", "'")
            .replace("`", "'")
    )

    # Remove harmless punctuation while preserving words.
        normalized = re.sub(r"[^\w\s']", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()

    # Normalize common English contractions for matching.
        normalized = re.sub(r"\bwhat's\b", "what is", normalized)
        normalized = re.sub(r"\bhow's\b", "how is", normalized)
        normalized = re.sub(r"\bthat's\b", "that is", normalized)
        normalized = re.sub(r"\bit's\b", "it is", normalized)
        normalized = re.sub(r"\bthat's\b", "that is", normalized)

        if not normalized:
            return None

    # -------------------------------------------------
    # 2. PHRASE CATEGORIES
    #
    # Exact normalized matching only.
    # Do not classify arbitrary sentences by keywords.
    # -------------------------------------------------

        categories = {
            "greeting": {
            "en": {
                "hi",
                "hello",
                "hey",
                "hey there",
                "hi there",
                "hello there",
                "hi bro",
                "hello bro",
                "hey bro",
                "good morning",
                "good afternoon",
                "good evening",
                "morning",
                "afternoon",
                "evening",
                "how are you",
                "how are you doing",
                "how have you been",
                "what is up",
                "what is up bro",
                "how is it going",
            },
            "te": {
                "ela unnav",
                "ela unnav bro",
                "ela unnaru",
                "ela unnaru bro",
                "bagunnava",
                "bagunnava bro",
                "bagunnara",
                "namaskaram",
                "namaste",
                "em chestunnav",
                "em chestunnav bro",
            },
        },

        "farewell": {
            "en": {
                "bye",
                "goodbye",
                "bye bro",
                "see you",
                "see you later",
                "talk later",
                "catch you later",
                "take care",
                "good night",
                "have a good day",
            },
            "te": {
                "vellostha",
                "vellostha bro",
                "malli kaluddam",
                "tarvata matladadam",
                "bye bro vellostha",
            },
        },

        "gratitude": {
            "en": {
                "thanks",
                "thank you",
                "thanks bro",
                "thank you bro",
                "thank you so much",
                "thanks a lot",
                "many thanks",
                "really appreciate it",
            },
            "te": {
                "dhanyavadalu",
                "thanks bro",
                "chala thanks",
                "thank you bro",
            },
        },

        "apology": {
            "en": {
                "sorry",
                "sorry bro",
                "my bad",
                "i am sorry",
                "my mistake",
                "please forgive me",
            },
            "te": {
                "sorry bro",
                "kshaminchu",
                "nannu kshaminchu",
                "na tappu",
            },
        },

        "acknowledgement": {
            "en": {
                "got it",
                "understood",
                "i understand",
                "okay got it",
                "ok got it",
                "alright",
                "all right",
                "okay thanks",
                "ok thanks",
                "okay thank you",
                "ok thank you",
            },
            "te": {
                "ardham ayyindi",
                "ardhamayindi",
                "ardham ayyindi bro",
                "sare bro",
                "sare",
                "alage",
                "avunu",
            },
        },

        "celebration": {
            "en": {
                "awesome",
                "great",
                "nice",
                "excellent",
                "amazing",
                "fantastic",
                "wonderful",
                "perfect",
                "super",
                "super bro",
                "that is great",
                "that is awesome",
            },
            "te": {
                "super bro",
                "chala bagundi",
                "bagundi bro",
                "adbhutam",
                "chaala baagundi",
            },
        },

        "affirmation": {
            "en": {
                "yes",
                "yes bro",
                "sure",
                "sure bro",
                "absolutely",
                "definitely",
                "of course",
            },
            "te": {
                "avunu bro",
                "kachitanga",
                "tappakunda",
            },
        },

        "negative_acknowledgement": {
            "en": {
                "nope",
                "no",
                "no bro",
                "not really",
            },
            "te": {
                "ledu",
                "ledu bro",
                "vaddu",
            },
        },
    }

    # -------------------------------------------------
    # 3. FIND AN EXACT PHRASE MATCH
    # -------------------------------------------------

        matched_category = None
        matched_language = None

        for category, languages in categories.items():
            if normalized in languages["en"]:
                matched_category = category
                matched_language = "en"
                break

            if normalized in languages["te"]:
                matched_category = category
                matched_language = "te"
                break

    # Unknown or potentially context-dependent messages
    # continue through the existing semantic analyzer.
        if matched_category is None:
            return None

    # -------------------------------------------------
    # 4. CONSERVATIVE SAFETY CHECK
    #
    # Generic yes/no/okay responses can imply consent
    # or depend on previous conversational context.
    # Do not fast-path them initially.
    # -------------------------------------------------

        context_sensitive_categories = {
        "acknowledgement",
        "affirmation",
        "negative_acknowledgement",
    }

        if matched_category in context_sensitive_categories:
            return None

    # -------------------------------------------------
    # 5. BUILD A VALID SEMANTIC RESULT
    # -------------------------------------------------

        is_telugu_transliteration = matched_language == "te"

        if is_telugu_transliteration:
            response_style = "casual_tenglish"
            tone = "casual"
        else:
            response_style = (
                "casual_english"
                if any(word in normalized.split() for word in ("bro",))
                else "standard"
            )
            tone = "casual" if "bro" in normalized.split() else "neutral"

        return SemanticAnalysisResult(
            message_type=MessageType.CHAT,
            intent=IntentType.CONVERSATION,
            intent_confidence=0.99,
            entities={},
            requires_reasoning=False,
            requires_memory=False,
            requires_tool=False,
            should_enter_memory_pipeline=False,
            requires_memory_retrieval=True,
            language=matched_language,
            script="latin",
            is_mixed=False,
            secondary_language=None,
            is_transliterated=is_telugu_transliteration,
            tone=tone,
            response_style=response_style,
            requires_llm=True,
            confidence=0.99,
            conversation_scores=[],
    )
