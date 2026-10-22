from typing import Optional
from fastapi import Header, HTTPException
from app.core.config import settings
from app.services.firebase_service import verify_firebase_id_token

async def get_current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    if not settings.auth_required:
        return {"uid": "local-developer", "role": "admin", "auth_mode": "development"}
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer Firebase ID token")
    decoded = verify_firebase_id_token(authorization.split(" ", 1)[1].strip())
    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid or expired Firebase ID token")
    return {"uid": decoded.get("uid") or decoded.get("user_id"),
            "email": decoded.get("email"), "role": decoded.get("role", "user"),
            "auth_mode": "firebase"}
