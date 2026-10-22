from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "HospiCare AI API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    host: str = "127.0.0.1"
    port: int = 8000
    auth_required: bool = False
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    baseline_model_path: str = ""
    firebase_project_id: str = ""
    firebase_web_api_key: str = ""
    google_application_credentials: str = ""
    firestore_enabled: bool = False
    audit_log_path: str = "./data/audit.jsonl"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
