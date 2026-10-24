from collections import defaultdict
from time import time
from typing import Dict, List

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from bson import ObjectId

from app.core.database import get_db
from app.core.security import decode_access_token

security = HTTPBearer()

_login_hits: Dict[str, List[float]] = defaultdict(list)


def current_user_id(user: dict) -> str:
    return str(user["_id"])


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    db = get_db()

    try:
        user = await db["users"].find_one({"_id": ObjectId(payload["user_id"])})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def enforce_login_rate_limit(request: Request, limit: int = 10, window_seconds: int = 60):
    ip = request.client.host if request.client else "unknown"
    now = time()
    recent = [stamp for stamp in _login_hits[ip] if now - stamp < window_seconds]
    if len(recent) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please wait a minute and try again.",
        )
    recent.append(now)
    _login_hits[ip] = recent
