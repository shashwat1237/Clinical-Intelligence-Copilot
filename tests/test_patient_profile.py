def test_profile_api_schema():
    from app.schemas.patient_and_timeline import PatientProfileSchema
    
    data = {
        "conditions": [{"id": "1", "name": "Asthma"}],
        "medications": [],
        "labs": []
    }
    profile = PatientProfileSchema(**data)
    assert profile.conditions[0].name == "Asthma"

