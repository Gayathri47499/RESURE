# API Guide

Base URL: `http://127.0.0.1:8000/api/v1`

- `GET /health` — application/model configuration status.
- `GET /auth/me` — current local developer identity or verified Firebase identity.
- `POST /predictions` — submits encounter features and returns a prediction or explicit demo placeholder.
- `GET /analytics/summary` — summary of event metadata if Firestore is configured.
- `GET /fhir/metadata` — draft CapabilityStatement-shaped metadata, not a certified FHIR server.

Prediction request:
```json
{
  "patient_id": "pseudonymous-001",
  "encounter_id": "enc-001",
  "features": {
    "race": "Caucasian",
    "gender": "Female",
    "age": "[60-70)",
    "time_in_hospital": 4,
    "number_inpatient": 1,
    "number_emergency": 0,
    "number_outpatient": 0,
    "num_lab_procedures": 40,
    "num_procedures": 1,
    "num_medications": 12,
    "number_diagnoses": 5
  }
}
```
For meaningful output, send the expected feature names from the training dataset. Missing features are filled as missing by the service. If `BASELINE_MODEL_PATH` is unset, the API deliberately returns no prediction instead of making up a result.

Firebase is optional for local development. Set `AUTH_REQUIRED=true` only after Firebase ID token verification is configured and tested. Do not expose local development mode on a public deployment.
