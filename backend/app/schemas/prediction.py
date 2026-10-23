
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, ConfigDict


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient_id: Optional[str] = Field(
        default=None,
        max_length=128,
        description="Use pseudonymous IDs only",
    )
    encounter_id: Optional[str] = Field(
        default=None,
        max_length=128,
    )
    features: dict[str, Any]


class PredictionResponse(BaseModel):
    prediction_id: str
    created_at: datetime
    model_name: str
    model_mode: str
    readmission_within_30_days: Optional[int] = None
    risk_label: str
    confidence: Optional[float] = None
    readmission_probability: Optional[float] = None

    # Relative model scores, NOT clinical risk probabilities.
    relative_class_0_score: Optional[float] = None
    relative_class_1_score: Optional[float] = None

    explanation: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    research_only: bool = True
