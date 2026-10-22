from pydantic import BaseModel
class HealthResponse(BaseModel):
    status: str
    app: str
    model_status: str
    auth_required: bool
