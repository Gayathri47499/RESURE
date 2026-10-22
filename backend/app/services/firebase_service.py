from functools import lru_cache
from app.core.config import settings

@lru_cache(maxsize=1)
def _modules():
    try:
        import firebase_admin
        from firebase_admin import auth, credentials, firestore
        return firebase_admin, auth, credentials, firestore
    except Exception:
        return None, None, None, None

def _initialize():
    firebase_admin, auth, credentials, firestore = _modules()
    if not firebase_admin or not settings.firebase_project_id:
        return None, auth, firestore
    try:
        if not firebase_admin._apps:
            if settings.google_application_credentials:
                cred = credentials.Certificate(settings.google_application_credentials)
                firebase_admin.initialize_app(cred, {"projectId": settings.firebase_project_id})
            else:
                firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})
        return firebase_admin, auth, firestore
    except Exception:
        return None, auth, firestore

def verify_firebase_id_token(token: str):
    _, auth, _ = _initialize()
    if auth is None:
        return None
    try:
        return auth.verify_id_token(token, check_revoked=True)
    except Exception:
        return None

@lru_cache(maxsize=1)
def get_firestore_client():
    if not settings.firestore_enabled:
        return None
    _, _, firestore = _initialize()
    if firestore is None:
        return None
    try:
        return firestore.client()
    except Exception:
        return None
