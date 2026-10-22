# HospiCare AI — RESURE Frontend

Responsive frontend for the HospiCare AI readmission-risk research prototype. Includes animated dashboard, collapsible navigation, backend-backed notifications, sign-in and account registration screens.

## Run locally

Requirements: Node.js 20+ and npm.

1. Extract this folder into your project as `HospiCare_AI_Project/frontend`.
2. Start the FastAPI backend from the `backend` folder:
   ```powershell
   .venv\Scripts\Activate.ps1
   python -m uvicorn app.main:app --reload
   ```
3. In a second terminal, open the frontend folder and run:
   ```powershell
   npm install
   npm run dev
   ```
4. Open `http://127.0.0.1:5173`.

## Accounts

The Sign in form uses `POST /api/v1/auth/login`. New users can use **Create account**, which calls `POST /api/v1/auth/register` and then signs in through the login endpoint. The frontend does not contain demo credentials and never stores passwords. Registration requires the backend's Firebase Web API key configuration and Firebase Email/Password Authentication to be enabled. Use an email address you control; if an account already exists, switch to Sign in.

## Backend integration

The frontend calls these existing endpoints:
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/predictions`
- `GET /api/v1/predictions/history`
- `GET /api/v1/analytics/summary`
- `GET /api/v1/alerts`
- `PATCH /api/v1/alerts/{alert_id}/read`

The API base defaults to `http://127.0.0.1:8000/api/v1`. The backend CORS configuration should allow `http://127.0.0.1:5173` and `http://localhost:5173`.

## Important limitations

- Research prototype only; not clinically validated. Do not use outputs to diagnose, treat, discharge, or make patient-care decisions.
- Some dashboard patient rows and chart history are illustrative, not hospital records. The account prediction count uses the analytics API when available.
- FHIR Patient and Observation endpoints are prototype routes and currently return 404 because those resources are not implemented.
- The frontend cannot reset Firebase passwords because a password-reset endpoint is not implemented; use Firebase Console for account recovery.
