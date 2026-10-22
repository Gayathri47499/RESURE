from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import health, auth, predictions, analytics, fhir
from app.api.routes import alerts

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="HospiCare AI research prototype. Not clinically validated; not for patient-care decisions.",
)
origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(health.router, prefix=settings.api_v1_prefix, tags=["Health"])
app.include_router(auth.router, prefix=settings.api_v1_prefix, tags=["Authentication"])
app.include_router(predictions.router, prefix=settings.api_v1_prefix, tags=["Predictions"])
app.include_router(analytics.router, prefix=settings.api_v1_prefix, tags=["Analytics"])
app.include_router(fhir.router, prefix=settings.api_v1_prefix, tags=["FHIR"])
app.include_router(alerts.router, prefix="/api/v1", tags=["Alerts"])

@app.get("/", include_in_schema=False)
def root():
    return {"name": settings.app_name, "status": "running", "docs": "/docs",
            "disclaimer": "Research prototype only; not for clinical decisions."}
