class ConversationTitleGenerator:
    """
    Generates a short, human-readable title for a conversation.
    """

    def __init__(self, llm_service):
        self.llm_service = llm_service

    def generate(
        self,
        user_message: str,
        assistant_response: str | None = None,
    ) -> str:

        prompt = f"""
You are generating a short title for a user's conversation.

Understand the MAIN topic or purpose of the conversation.

Rules:
- Return ONLY valid JSON.
- The title must be 2 to 5 words.
- Keep it concise and natural.
- Do not use quotes around the title value.
- Do not include punctuation at the end.
- Do not mention "conversation", "chat", or "user".
- Do not copy the user's entire sentence.
- Use the actual topic, not generic filler.
- For simple greetings or casual small talk, use "Greeting".
- For unclear casual conversation, use "General Conversation".

Examples:

User: "hi ira"
Output: {{"title": "Greeting"}}

User: "how can I start exporting rice?"
Output: {{"title": "Rice Export Business"}}

User: "help me build IRABrain"
Output: {{"title": "IRABrain Development"}}

User: "what should I learn to become an AI engineer?"
Output: {{"title": "AI Learning Roadmap"}}

User: "explain artificial intelligence"
Output: {{"title": "Artificial Intelligence"}}

<user_message>
{user_message}
</user_message>

<assistant_response>
{assistant_response or ""}
</assistant_response>

Return ONLY:
{{"title": "..."}}
"""

        result = self.llm_service.generate_structured(
            prompt=prompt,
            temperature=0.2,
        )

        title = result.get("title")

        if not isinstance(title, str):
            return "General Conversation"

        title = " ".join(title.strip().split())

        if not title:
            return "General Conversation"

        return title[:255]