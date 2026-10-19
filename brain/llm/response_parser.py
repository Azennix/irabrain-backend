import json
import re


class ResponseParser:
    """
    Cleans and parses LLM responses.
    """
    @staticmethod
    def parse_json(response: str) -> dict:

     response = response.strip()

     start = response.find("{")
     end = response.rfind("}")

     if start == -1 or end == -1:
        raise ValueError("No JSON object found.")

     json_text = response[start:end + 1]

     return json.loads(json_text)
