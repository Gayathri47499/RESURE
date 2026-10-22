
from fastapi.testclient import TestClient

from app.main import app

from app.core.security import get_current_user

app.dependency_overrides[get_current_user] = lambda: {
    "uid": "test-user",
    "email": "test@example.com",
    "role": "user",
    "auth_mode": "test",
}
from app.services.prediction_service import (
    EXPECTED_FEATURES,
    get_model_status,
    load_baseline_model,
)

client = TestClient(app)


def sample_features():
    """Synthetic example input for model integration testing."""
    return {
        "race": "Caucasian",
        "gender": "Female",
        "age": "[70-80)",
        "weight": "?",
        "admission_type_id": 1,
        "discharge_disposition_id": 1,
        "admission_source_id": 7,
        "time_in_hospital": 5,
        "payer_code": "?",
        "medical_specialty": "InternalMedicine",
        "num_lab_procedures": 45,
        "num_procedures": 1,
        "num_medications": 15,
        "number_outpatient": 0,
        "number_emergency": 1,
        "number_inpatient": 2,
        "diag_1": "250.13",
        "diag_2": "401",
        "diag_3": "276",
        "number_diagnoses": 7,
        "max_glu_serum": "None",
        "A1Cresult": ">7",
        "metformin": "Steady",
        "repaglinide": "No",
        "nateglinide": "No",
        "chlorpropamide": "No",
        "glimepiride": "No",
        "acetohexamide": "No",
        "glipizide": "No",
        "glyburide": "No",
        "tolbutamide": "No",
        "pioglitazone": "No",
        "rosiglitazone": "No",
        "acarbose": "No",
        "miglitol": "No",
        "troglitazone": "No",
        "tolazamide": "No",
        "examide": "No",
        "citoglipton": "No",
        "insulin": "Steady",
        "glyburide-metformin": "No",
        "glipizide-metformin": "No",
        "glimepiride-pioglitazone": "No",
        "metformin-rosiglitazone": "No",
        "metformin-pioglitazone": "No",
        "change": "Ch",
        "diabetesMed": "Yes",
    }


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_prediction_response_is_research_only():
    response = client.post(
        "/api/v1/predictions",
        json={
            "patient_id": "synthetic-test-001",
            "features": {
                "gender": "Female",
                "age": "[60-70)",
                "time_in_hospital": 4,
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["research_only"] is True
    assert response.json()["prediction_id"]


def test_saved_baseline_model_loads():
    model = load_baseline_model()

    assert model is not None, (
        "Baseline model did not load. Check BASELINE_MODEL_PATH "
        "and the model file."
    )
    assert get_model_status() == "baseline_loaded"


def test_real_model_prediction_response():
    assert load_baseline_model() is not None, (
        "Cannot run integration test because the saved baseline model "
        "is not available."
    )

    response = client.post(
        "/api/v1/predictions",
        json={
            "patient_id": "synthetic-test-002",
            "encounter_id": "synthetic-encounter-002",
            "features": sample_features(),
        },
    )

    assert response.status_code == 200, response.text

    result = response.json()

    assert result["research_only"] is True
    assert result["model_mode"] == "baseline"
    assert result["readmission_within_30_days"] in (0, 1)
    assert 0.0 <= result["readmission_probability"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["prediction_id"]
    assert len(EXPECTED_FEATURES) == 47
    assert any("not clinically validated" in warning.lower()
               for warning in result["warnings"])
