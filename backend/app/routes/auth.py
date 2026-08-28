"""
CloudGuard AI – Authentication Routes
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
import bcrypt
from bson import ObjectId

from app.database import get_database
from app.schemas.auth import RegisterRequest, LoginRequest, ProfileUpdateRequest, TokenResponse
from app.auth.jwt_handler import create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _user_out(user: dict) -> dict:
    """Serialize user document for API response."""
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user.get("role", "user"),
        "created_at": user.get("created_at", datetime.utcnow()).isoformat(),
    }


# ── Register ──────────────────────────────────────────────────────────────────
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    db = get_database()

    # Check duplicate email
    existing = await db["users"].find_one({"email": payload.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Determine role – first user becomes admin
    count = await db["users"].count_documents({})
    role = "admin" if count == 0 else "user"

    user_doc = {
        "name": payload.name,
        "email": payload.email,
        "password_hash": _hash_password(payload.password),
        "role": role,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db["users"].insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    token = create_access_token({"sub": str(result.inserted_id)})
    return TokenResponse(access_token=token, user=_user_out(user_doc))


# ── Login ─────────────────────────────────────────────────────────────────────
@router.post("/login")
async def login(payload: LoginRequest):
    db = get_database()

    user = await db["users"].find_one({"email": payload.email})
    if not user or not _verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    token = create_access_token({"sub": str(user["_id"])})
    return TokenResponse(access_token=token, user=_user_out(user))


# ── Me ────────────────────────────────────────────────────────────────────────
@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return _user_out(current_user)


@router.patch("/me")
async def update_me(
    payload: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    db = get_database()
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        return _user_out(current_user)

    if "email" in updates:
        existing = await db["users"].find_one({
            "email": updates["email"],
            "_id": {"$ne": current_user["_id"]},
        })
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

    updates["updated_at"] = datetime.utcnow()
    await db["users"].update_one(
        {"_id": current_user["_id"]},
        {"$set": updates},
    )
    updated_user = {**current_user, **updates}
    return _user_out(updated_user)
