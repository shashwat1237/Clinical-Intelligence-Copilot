from app.ai.extraction import extract_clinical_entities_from_text

def test_json_structure(mocker):
    # Mock Groq client to prevent API calls during CI
    mock_response = {
        "entities": [{"category": "Condition", "normalized_name": "Hypertension", "value": ""}],
        "timeline": []
    }
    mocker.patch("app.ai.groq_client.GroqClient.generate_json", return_value=mock_response)
    
    res = extract_clinical_entities_from_text("Patient has high blood pressure.")
    assert "entities" in res
    assert res["entities"][0]["normalized_name"] == "Hypertension"

