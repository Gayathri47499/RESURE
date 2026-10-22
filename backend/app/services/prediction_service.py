
from functools import lru_cache
from pathlib import Path
from typing import Any
import logging
import uuid

import joblib
import numpy as np
import pandas as pd

from app.core.config import settings

logger = logging.getLogger(__name__)

EXPECTED_FEATURES = [
    "race",
    "gender",
    "age",
    "weight",
    "admission_type_id",
    "discharge_disposition_id",
    "admission_source_id",
    "time_in_hospital",
    "payer_code",
    "medical_specialty",
    "num_lab_procedures",
    "num_procedures",
    "num_medications",
    "number_outpatient",
    "number_emergency",
    "number_inpatient",
    "diag_1",
    "diag_2",
    "diag_3",
    "number_diagnoses",
    "max_glu_serum",
    "A1Cresult",
    "metformin",
    "repaglinide",
    "nateglinide",
    "chlorpropamide",
    "glimepiride",
    "acetohexamide",
    "glipizide",
    "glyburide",
    "tolbutamide",
    "pioglitazone",
    "rosiglitazone",
    "acarbose",
    "miglitol",
    "troglitazone",
    "tolazamide",
    "examide",
    "citoglipton",
    "insulin",
    "glyburide-metformin",
    "glipizide-metformin",
    "glimepiride-pioglitazone",
    "metformin-rosiglitazone",
    "metformin-pioglitazone",
    "change",
    "diabetesMed",
]

MODEL_FILENAME = "readmission_logistic_grouped_baseline.joblib"


def _model_path() -> Path | None:
    """Resolve the configured model path, with a local project fallback."""
    configured_path = settings.baseline_model_path.strip()

    if configured_path:
        return Path(configured_path).expanduser().resolve()

    # prediction_service.py is in backend/app/services/
    # The models directory is backend/models/
    return (
        Path(__file__).resolve().parents[2]
        / "models"
        / MODEL_FILENAME
    )


@lru_cache(maxsize=1)
def load_baseline_model():
    """Load the fitted sklearn Pipeline once per application process."""
    path = _model_path()

    if path is None or not path.is_file():
        logger.warning("HospiCare baseline model not found at: %s", path)
        return None

    try:
        model = joblib.load(path)

        if not hasattr(model, "predict"):
            raise TypeError("Loaded model does not implement predict().")

        if hasattr(model, "feature_names_in_"):
            model_features = list(model.feature_names_in_)
            if model_features != EXPECTED_FEATURES:
                raise ValueError(
                    "The saved model's input features do not match "
                    "the backend's expected feature list."
                )

        logger.info("HospiCare baseline model loaded from %s", path)
        return model

    except Exception:
        logger.exception("Failed to load HospiCare baseline model.")
        return None


def get_model_status() -> str:
    """Return whether the fitted baseline model is available."""
    return (
        "baseline_loaded"
        if load_baseline_model() is not None
        else "demo_mode_no_model"
    )


def predict(features: dict[str, Any]) -> dict:
    """
    Generate a research-only prediction from one encounter.

    The model's saved sklearn Pipeline performs preprocessing internally.
    Missing features are represented as NaN for the pipeline's imputers.
    """
    prediction_id = str(uuid.uuid4())

    common = {
        "prediction_id": prediction_id,
        "warnings": [
            "Research prototype only; not clinically validated.",
            "Do not use this output to make patient-care decisions.",
            "Predictions may be unreliable for incomplete or out-of-distribution inputs.",
        ],
        "explanation": [
            "This baseline does not provide validated clinical explanations.",
        ],
    }

    model = load_baseline_model()

    if model is None:
        return {
            **common,
            "model_name": "HospiCare AI logistic regression baseline",
            "model_mode": "demo",
            "readmission_within_30_days": None,
            "risk_label": "unavailable_model_not_configured",
            "confidence": None,
            "readmission_probability": None,
            "explanation": [
                "The fitted model could not be loaded. Check the model file "
                "and BASELINE_MODEL_PATH configuration."
            ],
        }

    # Preserve the exact column order used during training.
    row = {name: features.get(name, np.nan) for name in EXPECTED_FEATURES}
    frame = pd.DataFrame([row], columns=EXPECTED_FEATURES)

    try:
        # Use the complete saved Pipeline. Do not separately transform
        # the input with readmission_preprocessor.joblib.
        predicted = int(model.predict(frame)[0])

        probability = None
        confidence = None

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(frame)[0]
            classes = list(model.classes_)

            if 1 in classes:
                probability = float(probabilities[classes.index(1)])
                confidence = probability if predicted == 1 else 1.0 - probability

        return {
            **common,
            "model_name": "HospiCare AI grouped logistic regression baseline",
            "model_mode": "baseline",
            "readmission_within_30_days": predicted,
            "risk_label": (
                "positive_screen" if predicted == 1 else "negative_screen"
            ),
            "confidence": confidence,
            "readmission_probability": probability,
            "explanation": [
                "Prediction generated by the saved logistic regression pipeline.",
                "The probability is a model output, not a clinically validated risk estimate.",
                "No causal conclusion or treatment recommendation is provided.",
            ],
        }

    except (ValueError, TypeError, KeyError, AttributeError):
        logger.exception(
            "Prediction failed for prediction_id=%s", prediction_id
        )

        return {
            **common,
            "model_name": "HospiCare AI grouped logistic regression baseline",
            "model_mode": "error",
            "readmission_within_30_days": None,
            "risk_label": "prediction_error",
            "confidence": None,
            "readmission_probability": None,
            "explanation": [
                "The model could not process the supplied features. "
                "Check the input field names, data types, and model compatibility."
            ],
        }
