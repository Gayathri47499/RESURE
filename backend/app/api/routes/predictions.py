
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import get_current_user
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import predict
from app.services.audit_service import write_audit_event
from app.services.firebase_service import get_firestore_client

router = APIRouter()


@router.post("/predictions", response_model=PredictionResponse)
async def create_prediction(
    payload: PredictionRequest,
    user: dict = Depends(get_current_user),
):
    if not payload.features:
        raise HTTPException(status_code=422, detail="features must not be empty")

    user_id = user.get("uid")
    if not user_id:
        raise HTTPException(status_code=401, detail="Authenticated user ID is missing.")

    result = predict(payload.features)
    result["created_at"] = datetime.now(timezone.utc)
    response = PredictionResponse(**result)

    # Log metadata only; never include patient feature values.
    try:
        write_audit_event(
            "prediction_created",
            str(user_id),
            {
                "prediction_id": response.prediction_id,
                "model_mode": response.model_mode,
                "risk_label": response.risk_label,
            },
        )
    except Exception:
        pass

    db = get_firestore_client()

    if db is not None:
        # Save minimal prediction history.
        try:
            db.collection("prediction_events").document(
                response.prediction_id
            ).set({
                "prediction_id": response.prediction_id,
                "actor_id": str(user_id),
                "created_at": response.created_at.isoformat(),
                "model_name": response.model_name,
                "model_mode": response.model_mode,
                "risk_label": response.risk_label,
                "research_only": True,
            })
        except Exception:
            pass

        # Create a research-only in-app alert for high-risk labels.
        if response.risk_label == "high":
            try:
                db.collection("alerts").add({
                    "actor_id": str(user_id),
                    "title": "High readmission risk detected",
                    "message": (
                        "The research model flagged this prediction as high risk. "
                        "This result is for research only and must not guide patient care."
                    ),
                    "severity": "high",
                    "read": False,
                    "prediction_id": response.prediction_id,
                    "created_at": response.created_at.isoformat(),
                    "research_only": True,
                })
            except Exception:
                pass

    return response


@router.get("/predictions/history")
async def get_prediction_history(
    limit: int = Query(default=20, ge=1, le=100),
    user: dict = Depends(get_current_user),
):
    user_id = user.get("uid")
    if not user_id:
        raise HTTPException(status_code=401, detail="Authenticated user ID is missing.")

    db = get_firestore_client()
    if db is None:
        raise HTTPException(
            status_code=503,
            detail="Prediction history storage is unavailable.",
        )

    try:
        query = (
            db.collection("prediction_events")
            .where("actor_id", "==", str(user_id))
            .order_by("created_at", direction="DESCENDING")
            .limit(limit)
        )

        records = []
        for document in query.stream():
            record = document.to_dict() or {}
            records.append({
                "prediction_id": record.get("prediction_id"),
                "created_at": record.get("created_at"),
                "model_name": record.get("model_name"),
                "model_mode": record.get("model_mode"),
                "risk_label": record.get("risk_label"),
                "research_only": True,
            })

        return {
            "count": len(records),
            "predictions": records,
            "research_only": True,
        }
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve prediction history.",
        )
