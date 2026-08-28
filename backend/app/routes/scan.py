"""
CloudGuard AI – Scan Routes
POST   /api/scan/start
GET    /api/scan/latest
GET    /api/scan/history
GET    /api/scan/{scan_id}
DELETE /api/scan/{scan_id}
"""

import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks, Query
from bson import ObjectId

from app.database import get_database
from app.schemas.scan import ScanStartRequest
from app.auth.dependencies import get_current_user
from app.services.scan_service import run_full_scan_safely

router = APIRouter(prefix="/api/scan", tags=["Scanning"])


def _serialize_scan(scan: dict) -> dict:
    scan["id"] = str(scan.pop("_id"))
    if isinstance(scan.get("scan_date"), datetime):
        scan["scan_date"] = scan["scan_date"].isoformat()
    if isinstance(scan.get("created_at"), datetime):
        scan["created_at"] = scan["created_at"].isoformat()
    return scan


# ── Start Scan ────────────────────────────────────────────────────────────────
@router.post("/start", status_code=status.HTTP_202_ACCEPTED)
async def start_scan(
    payload: ScanStartRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    db = get_database()
    user_id = str(current_user["_id"])

    # Verify AWS account belongs to user
    try:
        account = await db["aws_accounts"].find_one({
            "_id": ObjectId(payload.aws_account_id),
            "user_id": user_id,
        })
    except Exception:
        account = None

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AWS account not found. Please connect an account first.",
        )

    # Create scan record
    scan_doc = {
        "user_id": user_id,
        "aws_account_id": payload.aws_account_id,
        "scan_date": datetime.utcnow(),
        "status": "running",
        "overall_score": 0,
        "risk_level": "Unknown",
        "total_issues": 0,
        "critical_count": 0,
        "high_count": 0,
        "medium_count": 0,
        "low_count": 0,
        "findings": [],
        "service_scores": {},
        "created_at": datetime.utcnow(),
    }
    result = await db["scans"].insert_one(scan_doc)
    scan_id = str(result.inserted_id)

    # Run scan in background
    background_tasks.add_task(
        run_full_scan_safely,
        scan_id=scan_id,
        user_id=user_id,
        aws_account=dict(account),
        services=payload.services or ["iam", "s3", "ec2", "cloudtrail"],
    )

    return {
        "message": "Scan started successfully",
        "scan_id": scan_id,
        "status": "running",
    }


# ── Get Latest Scan ───────────────────────────────────────────────────────────
@router.get("/latest")
async def get_latest_scan(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = str(current_user["_id"])

    scan = await db["scans"].find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)],
    )
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No scans found. Run your first scan to get started.",
        )
    return _serialize_scan(scan)


# ── Scan History ──────────────────────────────────────────────────────────────
@router.get("/history")
async def get_scan_history(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    db = get_database()
    user_id = str(current_user["_id"])

    cursor = db["scans"].find(
        {"user_id": user_id},
        sort=[("created_at", -1)],
    ).limit(limit)

    scans = []
    async for scan in cursor:
        # Return summary only (no full findings list for performance)
        scan.pop("findings", None)
        scans.append(_serialize_scan(scan))

    return {"scans": scans, "total": len(scans)}


# ── Get Single Scan ───────────────────────────────────────────────────────────
@router.get("/{scan_id}")
async def get_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user),
):
    db = get_database()
    user_id = str(current_user["_id"])

    try:
        scan = await db["scans"].find_one({
            "_id": ObjectId(scan_id),
            "user_id": user_id,
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid scan ID")

    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")

    return _serialize_scan(scan)


# ── Delete Scan ───────────────────────────────────────────────────────────────
@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user),
):
    db = get_database()
    user_id = str(current_user["_id"])

    try:
        result = await db["scans"].delete_one({
            "_id": ObjectId(scan_id),
            "user_id": user_id,
        })
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid scan ID")

    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
