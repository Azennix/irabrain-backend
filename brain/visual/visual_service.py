
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

    NODE_TYPES = {
        "flowchart", "concept_map", "system_architecture",
        "connection_graph", "hierarchy", "decision_tree", "cycle",
    }

    @classmethod
    def _is_renderable(cls, v: dict) -> bool:
        t = v.get("type")
        if t in cls.NODE_TYPES:
            return isinstance(v.get("nodes"), list) and bool(v["nodes"]) \
                and isinstance(v.get("edges"), list)
        if t == "comparison":
            return bool(v.get("columns")) and bool(v.get("comparisons"))
        if t == "timeline":
            return bool(v.get("timeline"))
        if t == "steps":
            return bool(v.get("steps"))
        if t == "data_chart":
            c = v.get("chart")
            return isinstance(c, dict) and bool(c.get("labels")) and bool(c.get("series"))
        return False

    def generate_multi(self, query, response, context, visual_type_hint=None):
        if not self.should_generate(query):
            return []
        try:
            generator = getattr(self.chat_engine, "generate_visuals", None)
            if not callable(generator):
                return []

            result = generator(
                user_message=query,
                assistant_response=response,
                request_context=context,
                visual_type_hint=visual_type_hint,
            )

            if result is None:
                return []
            if isinstance(result, list):
                if len(result) != 1:
                    return []
                result = result[0]
            if not isinstance(result, dict):
                return []
            if result.get("type") in (None, "none"):
                return []
            if not isinstance(result.get("title"), str):
                return []
            if not self._is_renderable(result):
                print(f"[VISUAL] Discarded non-renderable '{result.get('type')}' visual.")
                return []

            print("[VISUAL] Generated one visual object.")
            return [result]
        except Exception as exc:
            print(f"[VISUAL SERVICE ERROR] {exc}")
            return []