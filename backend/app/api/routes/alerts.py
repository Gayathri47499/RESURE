
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import get_current_user
from app.services.firebase_service import get_firestore_client

router = APIRouter()


@router.get("/alerts")
async def list_alerts(
    limit: int = Query(default=20, ge=1, le=100),
    user: dict = Depends(get_current_user),
):
    user_id = user.get("uid")
    if not user_id:
        raise HTTPException(status_code=401, detail="Authenticated user ID is missing.")

    db = get_firestore_client()
    if db is None:
        raise HTTPException(status_code=503, detail="Alert storage is unavailable.")

    try:
        query = (
            db.collection("alerts")
            .where("actor_id", "==", str(user_id))
            .limit(limit)
        )
        alerts = []
        for document in query.stream():
            item = document.to_dict() or {}
            alerts.append({
                "alert_id": document.id,
                "title": item.get("title", "Risk alert"),
                "message": item.get("message", ""),
                "severity": item.get("severity", "info"),
                "read": bool(item.get("read", False)),
                "created_at": item.get("created_at"),
                "research_only": True,
            })

        return {"count": len(alerts), "alerts": alerts, "research_only": True}

    except Exception:
        raise HTTPException(status_code=503, detail="Could not retrieve alerts.")


@router.patch("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: str,
    user: dict = Depends(get_current_user),
):
    user_id = user.get("uid")
    if not user_id:
        raise HTTPException(status_code=401, detail="Authenticated user ID is missing.")

    db = get_firestore_client()
    if db is None:
        raise HTTPException(status_code=503, detail="Alert storage is unavailable.")

    try:
        ref = db.collection("alerts").document(alert_id)
        snapshot = ref.get()

        if not snapshot.exists:
            raise HTTPException(status_code=404, detail="Alert not found.")

        alert = snapshot.to_dict() or {}
        if alert.get("actor_id") != str(user_id):
            raise HTTPException(status_code=404, detail="Alert not found.")

        ref.update({
            "read": True,
            "read_at": datetime.now(timezone.utc).isoformat(),
        })

        return {"message": "Alert marked as read.", "alert_id": alert_id}

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="Could not update alert.")
