
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.services.firebase_service import get_firestore_client

router = APIRouter()


@router.get("/analytics/summary")
async def analytics_summary(
    user: dict = Depends(get_current_user),
):
    user_id = user.get("uid")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user ID is missing.",
        )

    db = get_firestore_client()

    if db is None:
        raise HTTPException(
            status_code=503,
            detail="Analytics storage is unavailable.",
        )

    try:
        query = (
            db.collection("prediction_events")
            .where("actor_id", "==", str(user_id))
        )

        total = 0
        risk_counts = {}

        for document in query.stream():
            record = document.to_dict() or {}
            total += 1

            label = str(record.get("risk_label", "unknown"))
            risk_counts[label] = risk_counts.get(label, 0) + 1

        return {
            "total_predictions": total,
            "risk_label_counts": risk_counts,
            "research_only": True,
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve analytics.",
        )
