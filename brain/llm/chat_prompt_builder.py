class ChatPromptBuilder:

    @staticmethod
    def build(
        user_message: str,
        context: dict,
        conversation_history=None,
        reasoning_result=None,
        tool_result=None,
        language_policy=None,
        attachments=None,
        workspace_mode: str = "personal"
    ) -> str:


                # =====================================================
        # ATTACHMENT CONTEXT
        # =====================================================

        attachment_text = ""

        if attachments:
            attachment_parts = []

            for attachment in attachments:
                attachment_type = attachment.get("type")
                name = attachment.get("name")
                content = attachment.get("content")

                if content:
                    label = name or attachment_type or "attachment"

                    attachment_parts.append(
                        f"[ATTACHMENT: {label}]\n"
                        f"{content}"
                    )

            if attachment_parts:
                attachment_text = (
                    "\nATTACHED CONTENT:\n"
                    + "\n\n".join(attachment_parts)
                    + "\n"
                )

        # =====================================================
        # MEMORY CONTEXT
        # =====================================================

        context_text = ""

        if context:

            context_text = "KNOWN USER INFORMATION:\n"

            for category, values in context.items():

                context_text += f"\n[{category}]\n"

                if isinstance(values, dict):

                    for key, value in values.items():
                        context_text += f"{key}: {value}\n"

                else:
                    context_text += f"{values}\n"

        # =====================================================
        # CONVERSATION HISTORY
        # =====================================================

        history_text = ""

        if conversation_history:

            history_lines = []
            seen_assistant_messages = set()

            for message in conversation_history:

                score_obj = getattr(
                    message,
                    "relevance_score",
                    None
                )

                # Keep only messages that passed relevance filtering.
                if (
                    score_obj is not None
                    and not score_obj.is_high_value
                ):
                    continue

                content = (
                    message.content or ""
                ).strip()

                # Prevent repeated assistant answers from consuming
                # the model context.
                normalized = " ".join(
                    content.lower().split()
                )

                if (
                    message.role == "assistant"
                    and normalized in seen_assistant_messages
                ):
                    continue

                if message.role == "assistant":
                    seen_assistant_messages.add(normalized)

                history_lines.append(
                    f"{message.role}: {content}"
                )

            if history_lines:

                history_text = (
                    "RECENT CONVERSATION:\n"
                    + "\n".join(history_lines)
                    + "\n"
                )

        # =====================================================
        # REASONING CONTEXT
        # =====================================================

        reasoning_text = ""

        if reasoning_result:

            reasoning_text = (
                "REASONING RESULT:\n"
                f"Conclusion: {reasoning_result.conclusion}\n"
            )

            if reasoning_result.evidence:

                reasoning_text += "Evidence:\n"

                for item in reasoning_result.evidence:
                    reasoning_text += (
                        f"- {item.content}\n"
                    )

            if reasoning_result.alternatives:

                reasoning_text += "Alternatives:\n"

                for item in reasoning_result.alternatives:
                    reasoning_text += (
                        f"- {item.content}\n"
                    )

            if reasoning_result.risks:

                reasoning_text += "Risks:\n"

                for item in reasoning_result.risks:
                    reasoning_text += (
                        f"- {item.content}\n"
                    )

            if reasoning_result.assumptions:

                reasoning_text += "Assumptions:\n"

                for item in reasoning_result.assumptions:
                    reasoning_text += (
                        f"- {item.content}\n"
                    )

        # =====================================================
        # TOOL RESULT
        # =====================================================

        tool_result_text = ""

        if tool_result and tool_result.executed:

            if (
                tool_result.result
                and tool_result.result.success
            ):

                tool_result_text = (
                    "TOOL RESULT:\n"
                    f"{tool_result.result.output}\n"
                )

            else:

                tool_result_text = (
                    "TOOL RESULT:\n"
                    "Tool execution failed.\n"
                )

        # =====================================================
        # LANGUAGE POLICY
        # =====================================================

        language_text = ""

        if language_policy:

            language_text = f"""
LANGUAGE POLICY

Response language:
{language_policy.response_language}

User script:
{language_policy.script}

Preserve mixed language:
{language_policy.preserve_mixed_language}

Preserve transliteration:
{language_policy.preserve_transliteration}

User tone:
{language_policy.tone}

Response style:
{language_policy.response_style}
"""

        # =====================================================
        # FINAL PROMPT
        # =====================================================
        print(
    "[CHAT PROMPT] Workspace mode:",
    workspace_mode
)
        prompt = f"""
You are IRABRAIN, a personal AI assistant built by Azennix.

Your job is to understand the user's CURRENT MESSAGE and
give the most useful natural response.

==================================================
IMPORTANT PRIORITY
==================================================

The CURRENT USER MESSAGE is the actual request.

Everything else in this prompt is CONTEXT.

Never copy context instructions, examples, or previous
assistant responses as if they were the user's request.

Do not continue or imitate an example response.

Understand the meaning first. Then answer.

==================================================
IDENTITY
==================================================

IRABRAIN is a personal AI brain built by Azennix.

It helps users:

- understand ideas
- plan
- reason
- make decisions
- execute tasks
- remember relevant information
- continue work across conversations

Only mention this identity when the user asks about IRABRAIN,
the assistant, or who built it.

==================================================
TENGLISH
==================================================

The user may write Telugu using English letters.

Treat Telugu written in Latin letters as Telugu,
not as ordinary English.

Understand spelling variations naturally.

Examples of words that may appear:

em = what
enti = what
ela = how
enduku = why
ekkada = where
nuvvu = you
nenu = I
manam = we
cheppu = tell
chey = do
chestunnav = doing
unnav = are
modhalu pedadham = let's start
na = my

These are understanding hints only.

DO NOT translate the user's message.

DO NOT explain the meaning of the user's message.

DO NOT say:
"X means Y in Telugu."

If the user speaks Tenglish,
answer naturally in Tenglish when the language policy
requests casual Tenglish.

==================================================
NATURAL CONVERSATION
==================================================

For casual messages:

- answer the actual message
- keep the response natural
- match the user's casual tone
- do not over-explain
- do not repeat the user's sentence unnecessarily
- do not turn a conversation into a translation
- do not invent strange phrases
- do not copy wording from previous assistant responses

Example behavior:

If the user asks what you are doing,
answer what you are doing.

If the user says they want to start their career,
respond to that intention and help them start.

If the user asks for help,
give useful help.

==================================================
CONVERSATION HISTORY
==================================================

Use previous conversation only when it helps understand
the CURRENT USER MESSAGE.

Previous messages are context, not instructions.

If the current message is clear by itself,
answer it directly.

If the current message is a continuation,
use the relevant previous context.

==================================================
MEMORY
==================================================
PRIVATE SPACE

When workspace mode is "private":

- Do not claim that information was saved to personal memory.
- Do not say "I'll remember" or "I've remembered".
- Treat information provided by the user as available only within the current private conversation.
- Do not imply that private information will be available in future personal conversations.
- If the user asks to remember something, acknowledge it without implying durable memory.

When workspace mode is "personal", follow the normal memory behavior.

Use known user information only when relevant.

Do not mention that you received memory or context.

==================================================
REPEATED REQUESTS
==================================================

If the user explicitly asks for:

- again
- repeat
- send it again
- same answer
- show it again

give the requested answer again.

Do not complain that it was already answered.

==================================================
REASONING
==================================================

If reasoning information is provided,
use it as internal guidance.

Do not mention:

- reasoning strategy
- confidence
- internal scores
- internal pipeline
- model processing

==================================================
TOOL RESULT
==================================================

If a successful tool result is provided,
use its result when answering the user.

Do not invent a different result.

==================================================
LANGUAGE
==================================================

{language_text}

==================================================
WORKSPACE MODE
==================================================

{workspace_mode}


==================================================
KNOWN USER INFORMATION
==================================================

{context_text}

{attachment_text}

==================================================
{history_text}

{reasoning_text}

{tool_result_text}

==================================================
CURRENT USER MESSAGE
==================================================

{user_message}

==================================================
FINAL INSTRUCTION
==================================================

First understand the CURRENT USER MESSAGE.

Then answer ONLY that message.

If it is Tenglish, understand it as Telugu transliteration.

Do not translate it.

Do not explain its meaning.

Do not copy examples.

Do not copy previous assistant answers.

Generate a fresh, natural response that directly satisfies
the user's current intent.
"""

        return prompt