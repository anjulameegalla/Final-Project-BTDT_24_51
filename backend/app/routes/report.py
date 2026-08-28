"""
CloudGuard AI – Report Routes
POST /api/report/generate/{scan_id}
GET  /api/report/download/{report_id}
GET  /api/report/list
"""

import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse
from bson import ObjectId

from app.database import get_database
from app.auth.dependencies import get_current_user
from app.services.report_service import (
    generate_pdf_report, save_report_to_disk, upload_report_to_s3
)

router = APIRouter(prefix="/api/report", tags=["Reports"])


# ── Generate Report ───────────────────────────────────────────────────────────
@router.post("/generate/{scan_id}", status_code=status.HTTP_201_CREATED)
async def generate_report(
    scan_id: str,
    current_user: dict = Depends(get_current_user),
):
    db = get_database()
    user_id = str(current_user["_id"])

    # Fetch scan
    try:
        scan = await db["scans"].find_one({
            "_id": ObjectId(scan_id),
            "user_id": user_id,
        })
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid scan ID")

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Scan is not yet completed")

    # Prepare scan data for report
    scan_data = dict(scan)
    scan_data["id"] = str(scan_data.pop("_id"))
    scan_data["account_name"] = current_user.get("name", "CloudGuard User")

    # Generate PDF
    pdf_bytes = generate_pdf_report(scan_data, user_name=current_user.get("name", "User"))

    # Save to disk
    file_path = await save_report_to_disk(pdf_bytes, scan_id)
    file_name = os.path.basename(file_path)

    # Try S3 upload
    s3_url = await upload_report_to_s3(pdf_bytes, file_name)

    # Store report record
    report_doc = {
        "user_id": user_id,
        "scan_id": scan_id,
        "file_name": file_name,
        "file_path": file_path,
        "s3_url": s3_url,
        "created_at": datetime.utcnow(),
    }
    result = await db["reports"].insert_one(report_doc)

    return {
        "message": "Report generated successfully",
        "report_id": str(result.inserted_id),
        "file_name": file_name,
        "s3_url": s3_url or None,
    }


# ── Download Report ───────────────────────────────────────────────────────────
@router.get("/download/{report_id}")
async def download_report(
    report_id: str,
    current_user: dict = Depends(get_current_user),
):
    db = get_database()
    user_id = str(current_user["_id"])

    try:
        report = await db["reports"].find_one({
            "_id": ObjectId(report_id),
            "user_id": user_id,
        })
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid report ID")

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    file_path = report.get("file_path", "")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found on disk")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=report.get("file_name", "cloudguard_report.pdf"),
    )


# ── List Reports ──────────────────────────────────────────────────────────────
@router.get("/list")
async def list_reports(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = str(current_user["_id"])

    cursor = db["reports"].find({"user_id": user_id}).sort("created_at", -1)
    reports = []
    async for r in cursor:
        r["id"] = str(r.pop("_id"))
        if isinstance(r.get("created_at"), datetime):
            r["created_at"] = r["created_at"].isoformat()
        reports.append(r)

    return {"reports": reports}
