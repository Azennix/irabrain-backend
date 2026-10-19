class ResponseValidator:

    def validate(self, response: str) -> str:

        if response is None:
            return ""

        response = str(response).strip()

        if not response:
            return "I’m sorry, I couldn’t generate a response."

        return response