"""
CloudGuard AI – AWS Account Connection Routes
POST /api/aws/connect
GET  /api/aws/status
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId

from app.database import get_database
from app.schemas.aws import AWSConnectRequest, AWSStatusResponse
from app.auth.dependencies import get_current_user
from app.services.scan_service import validate_aws_connection
from app.utils.helpers import encrypt_credential

router = APIRouter(prefix="/api/aws", tags=["AWS Connection"])


# ── Connect AWS Account ───────────────────────────────────────────────────────
@router.post("/connect", status_code=status.HTTP_201_CREATED)
async def connect_aws(
    payload: AWSConnectRequest,
    current_user: dict = Depends(get_current_user),
):
    db = get_database()
    user_id = str(current_user["_id"])

    # Build account document
    account_doc = {
        "user_id": user_id,
        "account_name": payload.account_name,
        "region": payload.region,
        "role_arn": payload.role_arn,
        "access_key_id": payload.access_key_id,
        "secret_access_key_encrypted": (
            encrypt_credential(payload.secret_access_key)
            if payload.secret_access_key else None
        ),
        "is_demo": payload.use_demo,
        "connection_status": "pending",
        "created_at": datetime.utcnow(),
    }

    # Validate connection (skip for demo mode)
    if not payload.use_demo:
        account_data = {
            "role_arn": payload.role_arn,
            "access_key_id": payload.access_key_id,
            "secret_access_key": payload.secret_access_key,
            "region": payload.region,
        }
        is_valid = await validate_aws_connection(account_data)
        account_doc["connection_status"] = "connected" if is_valid else "failed"
        account_doc["last_validated"] = datetime.utcnow()

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="AWS connection validation failed. Check your credentials.",
            )
    else:
        account_doc["connection_status"] = "connected"
        account_doc["last_validated"] = datetime.utcnow()

    # Upsert – one account per user (update if exists)
    existing = await db["aws_accounts"].find_one({"user_id": user_id})
    if existing:
        await db["aws_accounts"].update_one(
            {"user_id": user_id},
            {"$set": account_doc},
        )
        account_id = str(existing["_id"])
    else:
        result = await db["aws_accounts"].insert_one(account_doc)
        account_id = str(result.inserted_id)

    return {
        "message": "AWS account connected successfully",
        "account_id": account_id,
        "connection_status": account_doc["connection_status"],
        "is_demo": payload.use_demo,
    }


# ── Get AWS Connection Status ─────────────────────────────────────────────────
@router.get("/status")
async def get_aws_status(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = str(current_user["_id"])

    account = await db["aws_accounts"].find_one({"user_id": user_id})
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No AWS account connected. Please connect an account first.",
        )

    return AWSStatusResponse(
        account_id=str(account["_id"]),
        account_name=account.get("account_name", ""),
        region=account.get("region", "us-east-1"),
        connection_status=account.get("connection_status", "unknown"),
        is_demo=account.get("is_demo", False),
        last_validated=account.get("last_validated", datetime.utcnow()).isoformat()
        if account.get("last_validated") else None,
    )
