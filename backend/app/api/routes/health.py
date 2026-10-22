from fastapi import APIRouter
from app.core.config import settings
from app.schemas.common import HealthResponse
from app.services.prediction_service import get_model_status

router = APIRouter()
@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", app=settings.app_name,
                          model_status=get_model_status(), auth_required=settings.auth_required)
