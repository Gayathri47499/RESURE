# HospiCare AI — Backend Starter

This scaffold follows the uploaded project plan: FastAPI backend, Firebase Auth/Firestore integration points, prediction API, analytics endpoint, audit events, and a minimal FHIR-shaped metadata route.

**Research prototype only.** The current model has low precision and has not been clinically validated. Do not use predictions for patient-care decisions. No model weights, Firebase credentials, or patient datasets are included in this scaffold.

## Structure
```text
HospiCare_AI_Project/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── schemas/
│   │   └── services/
│   ├── tests/
│   ├── .env.example
│   ├── requirements.txt
│   └── Dockerfile
├── docs/API_GUIDE.md
└── frontend/README.md
```

## Run locally (Windows PowerShell)
1. Extract ZIP and open `HospiCare_AI_Project` in VS Code.
2. In terminal:
```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```
3. Visit `http://127.0.0.1:8000/docs`.

## Configure your existing baseline
Set `BASELINE_MODEL_PATH` in `backend/.env` to the absolute path of your existing file `readmission_logistic_grouped_baseline.joblib`. Example:
```env
BASELINE_MODEL_PATH=C:/Users/your-user/HospiCare_AI/models/readmission_logistic_grouped_baseline.joblib
```
If no fitted model is configured, the API returns an explicit demo placeholder, not a fabricated prediction. Your Qwen adapter is not a standalone model; it requires `Qwen/Qwen3-4B` and a compatible inference environment.

## Firebase
Local mode defaults to `AUTH_REQUIRED=false`. This is only for local development. Configure Firebase project credentials and test token verification before setting `AUTH_REQUIRED=true`. Never commit `.env`, service-account JSON, model weights, or patient data.

## Before deployment
Configure strict CORS, authentication, role-based authorization, HTTPS, rate limits, secret management, persistent audit storage, privacy/retention policies, model monitoring, full test-set evaluation, and independent clinical validation. The FHIR route is only a prototype, not a certified FHIR server.
