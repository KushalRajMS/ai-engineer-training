from __future__ import annotations
import json

class OutputValidator:
    def parse_json_response(self, response_text: str) -> dict|None:
        if not response_text:
            return None
        try:
            parse_index1 = response_text.index("{")
            parse_index2 = response_text.rindex("}")
            cleared_response = response_text[parse_index1 : parse_index2 + 1]
            response = json.loads(cleared_response)
            return response
        except json.JSONDecodeError:
            return None
        except ValueError:
            return None

    def validate_extracted_fields(self, data: dict, required_keys: list[str]) -> bool:
        if not data:
            return False
        
        for key in required_keys:
            if not (key in data):
                return False
        return True

    def extract_structured_data(self, response_text: str, required_keys: list[str]) -> dict|None:
        data = self.parse_json_response(response_text= response_text)
        is_valid_parse = self.validate_extracted_fields(data= data, required_keys= required_keys)

        if not is_valid_parse:
            return None

        return data