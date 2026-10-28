from typing import List, Dict, Any

class VisualIntelligenceService:
    def __init__(self, chat_engine):
        self.chat_engine = chat_engine

    def should_generate(self, query: str) -> bool:
        return True # nee old logic unte pettu, ippudu always try for multi

    def generate(self, query: str, response: str, context) -> Dict[str, Any] | None:
        # backward compat
        res = self.generate_multi(query, response, context)
        return res[0] if res else None

    def generate_multi(self, query: str, response: str, context) -> List[Dict[str, Any]]:
        try:
            # NEW MULTI METHOD
            if hasattr(self.chat_engine, 'generate_visuals'):
                result = self.chat_engine.generate_visuals(
                    user_message=query,
                    assistant_response=response,
                    request_context=context
                )
                if result:
                    print(f"[VISUAL MULTI] Generated {len(result)} POVs")
                    return result

            # Fallback old single
            single = self.chat_engine.generate_visual(
                user_message=query,
                assistant_response=response,
                request_context=context
            )
            return [single] if single else []
        except Exception as e:
            print(f"[VISUAL MULTI SERVICE ERROR] {e}")
            return []
