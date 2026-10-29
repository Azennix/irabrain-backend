
from typing import Any


class VisualIntelligenceService:
    """
    Coordinates visual generation for IRABRAIN.

    The LLM decides whether a visual is useful and chooses its
    representation. This service enforces the single-visual contract.
    """

    def __init__(self, chat_engine):
        self.chat_engine = chat_engine

    def should_generate(self, query: str) -> bool:
        """
        Delegate the semantic decision to the LLM.
        Do not hardcode message keywords or greeting rules here.
        """
        return bool(query and query.strip())

    def generate(
        self,
        query: str,
        response: str,
        context,
    ) -> dict[str, Any] | None:
        visuals = self.generate_multi(query, response, context)
        return visuals[0] if visuals else None

    def generate_multi(
        self,
        query: str,
        response: str,
        context,
    ) -> list[dict[str, Any]]:
        """
        Return zero or one visual object.

        A single visual may contain multiple connected nodes and edges.
        """
        if not self.should_generate(query):
            return []

        try:
            generator = getattr(
                self.chat_engine,
                "generate_visuals",
                None,
            )

            if not callable(generator):
                print(
                    "[VISUAL] No generate_visuals method is available; "
                    "skipping visual generation."
                )
                return []

            result = generator(
                user_message=query,
                assistant_response=response,
                request_context=context,
            )

            if result is None:
                return []

            # Support the expected single-object contract and legacy
            # one-item lists without allowing multiple visual cards.
            if isinstance(result, dict):
                visual = result
            elif isinstance(result, list):
                if len(result) != 1:
                    print(
                        "[VISUAL WARNING] Expected zero or one visual; "
                        f"received {len(result)}. Discarding result."
                    )
                    return []

                visual = result[0]
            else:
                print("[VISUAL WARNING] Invalid visual result type.")
                return []

            if not isinstance(visual, dict):
                return []

            if visual.get("type") in (None, "none"):
                return []

            if not isinstance(visual.get("title"), str):
                return []

            nodes = visual.get("nodes")
            edges = visual.get("edges")

            if not isinstance(nodes, list) or not nodes:
                return []

            if not isinstance(edges, list):
                return []

            # Do not alter the generated graph. The chat engine is
            # responsible for validating node IDs and edge references.
            print("[VISUAL] Generated one visual object.")
            return [visual]

        except Exception as exc:
            print(f"[VISUAL SERVICE ERROR] {exc}")
            return []
