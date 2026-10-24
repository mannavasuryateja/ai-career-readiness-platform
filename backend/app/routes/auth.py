from fastapi import APIRouter, HTTPException, Depends, Request, status
from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.core.deps import get_current_user, enforce_login_rate_limit
from app.core.quota import get_user_quota_status
from app.models.auth_schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    ProfileUpdateRequest,
    ChangePasswordRequest,
)

from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


# ==================== REGISTER ====================

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    db = get_db()

    existing_user = await db["users"].find_one({"email": request.email.lower().strip()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = hash_password(request.password)

    user_doc = {
        "email": request.email.lower().strip(),
        "password": hashed_password,
        "full_name": request.full_name.strip(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db["users"].insert_one(user_doc)
    user_id = str(result.inserted_id)

    access_token = create_access_token(user_id, request.email.lower().strip())

    logger.info(f"New user registered: {request.email}")

    return TokenResponse(
        access_token=access_token,
        user_id=user_id,
        email=request.email.lower().strip(),
        full_name=request.full_name.strip(),
    )


# ==================== LOGIN ====================

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, raw_request: Request):
    enforce_login_rate_limit(raw_request)
    db = get_db()

    user = await db["users"].find_one({"email": request.email.lower().strip()})

    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user_id = str(user["_id"])
    access_token = create_access_token(user_id, user["email"])

    logger.info(f"User logged in: {request.email}")

    return TokenResponse(
        access_token=access_token,
        user_id=user_id,
        email=user["email"],
        full_name=user["full_name"],
    )


# ==================== GET PROFILE ====================

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
):
    return UserResponse(
        _id=str(current_user["_id"]),
        email=current_user["email"],
        full_name=current_user.get("full_name", ""),
        target_role=current_user.get("target_role", "Software Engineer"),
        years_of_experience=current_user.get("years_of_experience", 0),
        skills=current_user.get("skills", []),
        created_at=current_user["created_at"],
        updated_at=current_user.get("updated_at", current_user["created_at"]),
    )


# ==================== UPDATE PROFILE ====================

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    request: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    updates = {"updated_at": datetime.utcnow()}

    if request.full_name is not None and request.full_name.strip():
        updates["full_name"] = request.full_name.strip()
    if request.target_role is not None:
        updates["target_role"] = request.target_role.strip()
    if request.years_of_experience is not None:
        updates["years_of_experience"] = max(0, int(request.years_of_experience))
    if request.skills is not None:
        updates["skills"] = [str(s).strip() for s in request.skills if str(s).strip()]

    await db["users"].update_one(
        {"_id": current_user["_id"]},
        {"$set": updates},
    )

    updated_user = await db["users"].find_one({"_id": current_user["_id"]})
    return UserResponse(
        _id=str(updated_user["_id"]),
        email=updated_user["email"],
        full_name=updated_user.get("full_name", ""),
        target_role=updated_user.get("target_role", "Software Engineer"),
        years_of_experience=updated_user.get("years_of_experience", 0),
        skills=updated_user.get("skills", []),
        created_at=updated_user["created_at"],
        updated_at=updated_user.get("updated_at", updated_user["created_at"]),
    )


# ==================== GET QUOTA ====================

@router.get("/quota")
async def get_my_quota(
    current_user: dict = Depends(get_current_user),
):
    """Get today's usage and remaining quota for current user."""
    user_id = str(current_user["_id"])
    quota_info = await get_user_quota_status(user_id)
    return quota_info


# ==================== CHANGE PASSWORD ====================

@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()

    if not verify_password(request.current_password, current_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    hashed_new_password = hash_password(request.new_password)

    await db["users"].update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "password": hashed_new_password,
                "updated_at": datetime.utcnow(),
            }
        },
    )

    logger.info(f"Password changed: {current_user['email']}")

    return {"message": "Password changed successfully"}


# ==================== DELETE MY DATA (GDPR/PRIVACY) ====================

@router.delete("/my-data")
async def delete_my_data(
    current_user: dict = Depends(get_current_user),
):
    """Permanently delete all user data, resumes, analyses, interview sessions, and account."""
    db = get_db()
    user_id = str(current_user["_id"])

    # Delete all associated documents
    await db["resumes"].delete_many({"user_id": user_id})
    await db["job_descriptions"].delete_many({"user_id": user_id})
    await db["analysis_results"].delete_many({"user_id": user_id})
    await db["interview_sessions"].delete_many({"user_id": user_id})
    await db["usage_quotas"].delete_many({"user_id": user_id})
    await db["users"].delete_one({"_id": current_user["_id"]})

    logger.info(f"User and all associated data deleted permanently: {current_user['email']}")
    return {"message": "All user data and account records permanently deleted"}


# ==================== LOGOUT ====================

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    logger.info(f"User logged out: {current_user['email']}")
    return {"message": "Logged out successfully"}