
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import auth, predictions, analytics, fhir, alerts, health
from app.core.config import settings


def make_protected_test_app():
    test_app = FastAPI()
    prefix = settings.api_v1_prefix

    test_app.include_router(health.router, prefix=prefix)
    test_app.include_router(auth.router, prefix=prefix)
    test_app.include_router(predictions.router, prefix=prefix)
    test_app.include_router(analytics.router, prefix=prefix)
    test_app.include_router(fhir.router, prefix=prefix)
    test_app.include_router(alerts.router, prefix=prefix)

    return test_app


def test_phase2_protected_endpoints_require_auth():
    client = TestClient(make_protected_test_app())

    paths = [
        ("/api/v1/auth/me", "GET"),
        ("/api/v1/predictions/history", "GET"),
        ("/api/v1/analytics/summary", "GET"),
        ("/api/v1/alerts", "GET"),
        ("/api/v1/fhir/metadata", "GET"),
    ]

    for path, method in paths:
        response = client.request(method, path)
        assert response.status_code == 401, (
            f"{method} {path}: expected 401, got {response.status_code}"
        )


def test_phase2_fhir_patient_not_found_after_auth():
    from app.core.security import get_current_user

    test_app = make_protected_test_app()
    test_app.dependency_overrides[get_current_user] = lambda: {
        "uid": "phase2-test-user",
        "role": "user",
    }

    client = TestClient(test_app)
    response = client.get("/api/v1/fhir/Patient/test-patient")

    assert response.status_code == 404
