from unittest.mock import MagicMock
from bson import ObjectId
from models.patients.mongo_models import create_patient, dob_to_age


def test_create_patient_with_mock():
    """Test create_patient using a mocked MongoDB collection."""

    # Mock collection
    mock_collection = MagicMock()

    clinician_id = 5
    patient_data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "gender": "Female",
        "date_of_birth": "1990-08-25",
        "hypertension": 0,
        "heart_disease": 1,
        "ever_married": "Yes",
        "work_type": "Private",
        "residence_type": "Urban",
        "avg_glucose_level": 85.5,
        "bmi": 22.5,
        "smoking_status": "never smoked",
        "stroke": 0,
    }

    # Call create_patient with mocked collection
    patient_id = create_patient(clinician_id, patient_data, collection=mock_collection)

    # Verify the ID is a string
    assert isinstance(patient_id, str)
    assert ObjectId.is_valid(patient_id)

    # Ensure insert_one was called exactly once
    mock_collection.insert_one.assert_called_once()

    # Check that the inserted document contains expected keys and values
    inserted_doc = mock_collection.insert_one.call_args[0][0]
    assert inserted_doc["first_name"] == "Alice"
    assert inserted_doc["last_name"] == "Smith"
    assert inserted_doc["created_by"] == clinician_id
    assert inserted_doc["age"] == dob_to_age("1990-08-25")
    assert inserted_doc["bmi"] == 22.5
    assert inserted_doc["stroke"] == 0
    assert inserted_doc["created_at"] is not None
    assert inserted_doc["updated_at"] is None
