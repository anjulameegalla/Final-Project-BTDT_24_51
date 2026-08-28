"""
CloudGuard AI – Admin Routes
GET    /api/admin/users
GET    /api/admin/scans
GET    /api/admin/reports
DELETE /api/admin/user/{user_id}
GET    /api/admin/stats
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, Query
from bson import ObjectId

from app.database import get_database
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    for k, v in doc.items():
        if isinstance(v, datetime):
            doc[k] = v.isoformat()
    return doc


# ── List All Users ────────────────────────────────────────────────────────────
@router.get("/users")
async def list_users(admin: dict = Depends(require_admin)):
    db = get_database()
    users = []
    async for user in db["users"].find({}, {"password_hash": 0}):
        users.append(_serialize(user))
    return {"users": users, "total": len(users)}


# ── List All Scans ────────────────────────────────────────────────────────────
@router.get("/scans")
async def list_all_scans(
    limit: int = Query(default=50, ge=1, le=100),
    admin: dict = Depends(require_admin),
):
    db = get_database()
    scans = []
    cursor = db["scans"].find({}, {"findings": 0}).sort("created_at", -1).limit(limit)
    async for scan in cursor:
        scans.append(_serialize(scan))
    return {"scans": scans, "total": len(scans)}


# ── List All Reports ──────────────────────────────────────────────────────────
@router.get("/reports")
async def list_all_reports(admin: dict = Depends(require_admin)):
    db = get_database()
    reports = []
    async for report in db["reports"].find({}).sort("created_at", -1):
        reports.append(_serialize(report))
    return {"reports": reports, "total": len(reports)}


# ── System Stats ──────────────────────────────────────────────────────────────
@router.get("/stats")
async def get_system_stats(admin: dict = Depends(require_admin)):
    db = get_database()
    total_users = await db["users"].count_documents({})
    total_scans = await db["scans"].count_documents({})
    total_reports = await db["reports"].count_documents({})
    total_alerts = await db["alerts"].count_documents({})
    critical_scans = await db["scans"].count_documents({"risk_level": "Critical"})

    return {
        "total_users": total_users,
        "total_scans": total_scans,
        "total_reports": total_reports,
        "total_alerts": total_alerts,
        "critical_scans": critical_scans,
    }


# ── Delete User ───────────────────────────────────────────────────────────────
@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    admin: dict = Depends(require_admin),
):
    db = get_database()

    # Prevent self-deletion
    if user_id == str(admin["_id"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    try:
        result = await db["users"].delete_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # Cascade delete user data
    await db["scans"].delete_many({"user_id": user_id})
    await db["reports"].delete_many({"user_id": user_id})
    await db["alerts"].delete_many({"user_id": user_id})
    await db["aws_accounts"].delete_many({"user_id": user_id})


# ── Delete Report ─────────────────────────────────────────────────────────────
@router.delete("/report/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str,
    admin: dict = Depends(require_admin),
):
    db = get_database()
    try:
        result = await db["reports"].delete_one({"_id": ObjectId(report_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid report ID")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Report not found")
