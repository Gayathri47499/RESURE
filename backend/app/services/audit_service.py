
import json
import os
from datetime import datetime, timezone

from app.core.config import settings


SENSITIVE_KEYS = {
    "password",
    "token",
    "id_token",
    "refresh_token",
    "authorization",
    "features",
    "patient_data",
}


def _sanitize_details(value):
    """Remove sensitive fields from nested audit details."""
    if isinstance(value, dict):
        return {
            key: _sanitize_details(item)
            for key, item in value.items()
            if key.lower() not in SENSITIVE_KEYS
        }

    if isinstance(value, list):
        return [_sanitize_details(item) for item in value]

    return value


def write_audit_event(
    event_type: str,
    actor_id: str,
    details: dict | None = None,
) -> None:
    path = settings.audit_log_path
    parent = os.path.dirname(path)

    if parent:
        os.makedirs(parent, exist_ok=True)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "actor_id": actor_id,
        "details": _sanitize_details(details or {}),
    }

    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(event, default=str) + "\n")
