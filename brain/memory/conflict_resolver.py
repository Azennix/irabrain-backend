class MemoryConflictResolver:

    def __init__(self, llm_service):

        self.llm = llm_service

    def resolve(
        self,
        existing,
        incoming
    ):

        prompt = f"""
You are the memory conflict resolution engine of IRABRAIN.

Compare the EXISTING memory with the INCOMING memory.

EXISTING:
category: {existing.category}
key: {existing.key}
value: {existing.value}
confidence: {existing.confidence}

INCOMING:
category: {incoming.category}
key: {incoming.key}
value: {incoming.value}
confidence: {incoming.confidence}

Decide what should happen.

Possible actions:

replace
merge
ignore

REPLACE:
The incoming information updates, corrects, or supersedes
the existing information.

MERGE:
Both pieces of information can remain true together.
Create one clean final value containing the useful information
from both.

IGNORE:
The incoming information adds nothing useful, is a duplicate,
or should not change the existing memory.

IMPORTANT:

- Do not invent information.
- Do not use hard-coded memory keys.
- Understand the semantic meaning of the memories.
- Do not automatically replace just because confidence is higher.
- Do not automatically merge just because values are different.
- Return the final value that should be stored.
- Preserve exact user-provided wording, spelling, and capitalization
- unless normalization is genuinely necessary.
- For IGNORE, final_value must be null.
- Return ONLY valid JSON.


VALUE PRESERVATION:

When replacing or merging a memory, preserve the original
user-provided spelling and capitalization whenever possible.

Do NOT lowercase names, company names, startup names,
programming languages, locations, product names, or other
proper nouns.

For example:

Existing:
Aneesh kumar

Incoming:
Rog

Correct:
{{
    "action": "replace",
    "final_value": "Rog"
}}

Incorrect:
{{
    "action": "replace",
    "final_value": "rog"
}}

OUTPUT:

{{
    "action": "replace",
    "final_value": "..."
}}

OR

{{
    "action": "merge",
    "final_value": "..."
}}

OR

{{
    "action": "ignore",
    "final_value": null
}}
"""

        result = self.llm.generate_structured(
            prompt=prompt,
            temperature=0.0
        )

        action = str(
            result.get("action", "ignore")
        ).lower().strip()

        final_value = result.get(
            "final_value"
        )

        return {
            "action": action,
            "final_value": final_value
        }