
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings
from app.core.security import get_current_user
from app.services.firebase_service import (
    get_firestore_client,
    verify_firebase_id_token,
)

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


def firebase_auth_url(method: str) -> str:
    key = settings.firebase_web_api_key
    if not key:
        raise HTTPException(
            status_code=503,
            detail="Firebase Authentication is not configured.",
        )
    return (
        "https://identitytoolkit.googleapis.com/v1/"
        f"accounts:{method}?key={key}"
    )


def save_user_profile(uid: str, email: str, display_name: str) -> None:
    db = get_firestore_client()
    if db is None:
        raise HTTPException(
            status_code=503,
            detail="Firestore is unavailable; user profile was not saved.",
        )

    now = datetime.now(timezone.utc).isoformat()
    db.collection("users").document(uid).set(
        {
            "uid": uid,
            "email": email,
            "display_name": display_name,
            "role": "user",
            "updated_at": now,
        },
        merge=True,
    )


@router.post("/auth/register", status_code=201)
async def register(payload: RegisterRequest):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                firebase_auth_url("signUp"),
                json={
                    "email": str(payload.email),
                    "password": payload.password,
                    "returnSecureToken": True,
                },
            )

        data = response.json()

        if response.is_error:
            code = data.get("error", {}).get("message", "")
            if code == "EMAIL_EXISTS":
                raise HTTPException(
                    status_code=409,
                    detail="An account with this email already exists.",
                )
            if code in {"WEAK_PASSWORD", "INVALID_PASSWORD"}:
                raise HTTPException(
                    status_code=400,
                    detail="Password does not meet Firebase requirements.",
                )
            raise HTTPException(
                status_code=400,
                detail="Firebase could not create this account.",
            )

        uid = data["localId"]
        email = data.get("email", str(payload.email))

        save_user_profile(uid, email, payload.display_name)

        return {
            "message": "Account created successfully.",
            "uid": uid,
            "email": email,
            "display_name": payload.display_name,
            "id_token": data["idToken"],
            "refresh_token": data.get("refreshToken"),
            "research_only": True,
        }

    except HTTPException:
        raise
    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Could not contact Firebase Authentication.",
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Account setup failed. Please check Firebase connectivity.",
        )


@router.post("/auth/login")
async def login(payload: LoginRequest):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                firebase_auth_url("signInWithPassword"),
                json={
                    "email": str(payload.email),
                    "password": payload.password,
                    "returnSecureToken": True,
                },
            )

        data = response.json()

        if response.is_error:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password.",
            )

        uid = data["localId"]
        email = data.get("email", str(payload.email))

        decoded = verify_firebase_id_token(data["idToken"])
        if not decoded:
            raise HTTPException(
                status_code=401,
                detail="Firebase ID token could not be verified.",
            )

        db = get_firestore_client()
        if db is None:
            raise HTTPException(
                status_code=503,
                detail="Firestore is unavailable.",
            )

        profile_ref = db.collection("users").document(uid)
        profile = profile_ref.get()

        if not profile.exists:
            save_user_profile(uid, email, email.split("@")[0])
            profile = profile_ref.get()

        profile_data = profile.to_dict() or {}

        return {
            "message": "Login successful.",
            "uid": uid,
            "email": email,
            "display_name": profile_data.get(
                "display_name", email.split("@")[0]
            ),
            "id_token": data["idToken"],
            "refresh_token": data.get("refreshToken"),
            "research_only": True,
        }

    except HTTPException:
        raise
    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Could not contact Firebase Authentication.",
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Login failed. Please check Firebase connectivity.",
        )


@router.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return {
        "user": user,
        "message": "Authentication status resolved.",
    }
