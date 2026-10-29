import pytest
from ai_training.chat.output_validator import OutputValidator

sample_text = "{\"name\": \"Sarah\", \"date\": \"July 10\", \"amount\": 120} - Output is this."
sample_text1 = "{\"name\": \"Sarah\", \"amount\": 120} - Output is this."
data = {
        'name': 'Mike', 
        'date': 'January 5th', 
        'amount': 75
    }
data1 = {
        'name': 'Mike', 
        'amount': 75
    }
required_keys = ["name", "date", "amount"]

def test_parse_json_response_json():
    validator = OutputValidator()
    response = validator.parse_json_response(sample_text)

    assert isinstance(response, dict)
    assert response["amount"] == 120
    assert "date" in response

    response = validator.parse_json_response("")
    assert response == None

    response = validator.parse_json_response("This is the output.")
    assert response == None

def test_validate_extracted_fields_bool():
    validator = OutputValidator()
    response = validator.validate_extracted_fields(data= data, required_keys= required_keys)

    assert isinstance(response, bool)
    assert response == True

    response = validator.validate_extracted_fields(data= data1, required_keys= required_keys)

    assert response == False

def test_extract_structured_data():
    validator = OutputValidator()
    response = validator.extract_structured_data(response_text= sample_text, required_keys= required_keys)

    assert isinstance(response, dict)
    assert response["amount"] == 120
    assert "name" in response

    response = validator.extract_structured_data(response_text= sample_text1, required_keys= required_keys)
    assert response == None
    response = validator.extract_structured_data(response_text= "", required_keys= required_keys)
    assert response == None