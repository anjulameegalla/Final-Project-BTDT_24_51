"""
CloudGuard AI – Alert Routes
GET  /api/alerts
POST /api/alerts/test
"""

from fastapi import APIRouter, Depends, Query
from app.auth.dependencies import get_current_user
from app.services.alert_service import get_user_alerts, _send_email

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("")
async def list_alerts(
    limit: int = Query(default=50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    user_id = str(current_user["_id"])
    alerts = await get_user_alerts(user_id, limit=limit)
    return {"alerts": alerts, "total": len(alerts)}


@router.post("/test")
async def test_alert(current_user: dict = Depends(get_current_user)):
    """Send a test alert email to verify SES configuration."""
    sent = await _send_email(
        subject="[CloudGuard AI] Test Alert",
        body="<h2>Test Alert</h2><p>Your CloudGuard AI alert system is working correctly.</p>",
    )
    return {
        "message": "Test alert sent" if sent else "Test alert failed",
        "success": sent,
    }
