from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import HTTPException, status
from pymongo import ReturnDocument

from app.core.config import get_settings
from app.core.database import get_db

KIND_ANALYSIS = "analyses"
KIND_INTERVIEW = "interviews"


def _today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


async def get_user_quota_status(user_id: str) -> Dict[str, Any]:
    """Retrieve today's quota usage and remaining allowance for the user."""
    settings = get_settings()
    today = _today_utc()
    db = get_db()
    
    doc = await db.usage_quotas.find_one({"user_id": user_id, "date": today}) or {}
    
    analyses_used = int(doc.get(KIND_ANALYSIS, 0))
    interviews_used = int(doc.get(KIND_INTERVIEW, 0))
    
    analyses_limit = settings.analysis_daily_limit
    interviews_limit = settings.interview_daily_limit
    
    return {
        "date": today,
        "analyses": {
            "used": analyses_used,
            "limit": analyses_limit,
            "remaining": max(0, analyses_limit - analyses_used),
        },
        "interviews": {
            "used": interviews_used,
            "limit": interviews_limit,
            "remaining": max(0, interviews_limit - interviews_used),
        }
    }


async def consume_daily_quota(user_id: str, kind: str) -> dict:
    settings = get_settings()
    limits = {
        KIND_ANALYSIS: settings.analysis_daily_limit,
        KIND_INTERVIEW: settings.interview_daily_limit,
    }
    if kind not in limits:
        raise ValueError(f"Unknown quota kind: {kind}")

    limit = limits[kind]
    today = _today_utc()
    db = get_db()
    doc = await db.usage_quotas.find_one({"user_id": user_id, "date": today})
    used = int((doc or {}).get(kind, 0))

    if used >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily {kind} limit reached ({limit}). Try again tomorrow.",
        )

    updated = await db.usage_quotas.find_one_and_update(
        {"user_id": user_id, "date": today},
        {
            "$inc": {kind: 1},
            "$setOnInsert": {"user_id": user_id, "date": today},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return {
        "date": today,
        kind: int((updated or {}).get(kind, used + 1)),
        "limit": limit,
    }

