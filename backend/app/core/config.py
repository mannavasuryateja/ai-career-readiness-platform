import os
from functools import lru_cache
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv

load_dotenv()

_INSECURE_JWT_DEFAULTS = {"", "your-secret-key", "changeme", "secret"}


@dataclass(frozen=True)
class Settings:
    mongodb_url: str
    mongodb_db_name: str
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_expiration_hours: int
    frontend_urls: List[str]
    gemini_model: str
    openrouter_model: str
    analysis_daily_limit: int
    interview_daily_limit: int
    max_upload_bytes: int
    max_jd_chars: int
    max_interview_questions: int


def _parse_origins(raw: str) -> List[str]:
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    return origins or [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    secret = os.getenv("JWT_SECRET_KEY", "").strip()
    if secret.lower() in _INSECURE_JWT_DEFAULTS or len(secret) < 32:
        raise RuntimeError(
            "JWT_SECRET_KEY must be set to a random string of at least 32 characters. "
            "Copy backend/.env.example to backend/.env and replace the placeholder."
        )

    return Settings(
        mongodb_url=os.getenv("MONGODB_URL", "mongodb://localhost:27017"),
        mongodb_db_name=os.getenv("MONGODB_DB_NAME", "ai_career_platform"),
        jwt_secret_key=secret,
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_expiration_hours=int(os.getenv("JWT_EXPIRATION_HOURS", "2")),
        frontend_urls=_parse_origins(
            os.getenv(
                "FRONTEND_URLS",
                os.getenv("FRONTEND_URL", "")
                + ","
                + os.getenv("FRONTEND_URL_VITE", ""),
            )
        ),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        openrouter_model=os.getenv(
            "OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free"
        ),
        analysis_daily_limit=int(os.getenv("ANALYSIS_DAILY_LIMIT", "3")),
        interview_daily_limit=int(os.getenv("INTERVIEW_DAILY_LIMIT", "2")),
        max_upload_bytes=int(os.getenv("MAX_UPLOAD_BYTES", str(4 * 1024 * 1024))),
        max_jd_chars=int(os.getenv("MAX_JD_CHARS", "8000")),
        max_interview_questions=int(os.getenv("MAX_INTERVIEW_QUESTIONS", "6")),
    )
