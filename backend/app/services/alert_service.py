"""
CloudGuard AI – Alert Service
Sends email alerts via AWS SES for critical/high findings.
"""

from datetime import datetime
from typing import List, Dict, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from app.config import settings
from app.database import get_database


async def send_alerts_for_scan(
    scan_id: str,
    user_id: str,
    findings: List[Dict[str, Any]],
  demo: bool = False,
) -> List[Dict[str, Any]]:
    """
    Send email alerts for Critical and High severity findings.
    Stores alert records in the database.
    Returns list of created alert records.
    """
    db = get_database()
    alerts_created = []

    critical_high = [f for f in findings if f.get("severity") in ("Critical", "High")]

    if not critical_high:
        return alerts_created

    # Build summary email
    email_body = _build_email_body(scan_id, critical_high)
    sent = await _send_email(
        subject=f"[CloudGuard AI] {len(critical_high)} Critical/High Security Issues Detected",
        body=email_body,
      demo=demo,
    )

    # Store alert record
    alert_doc = {
        "user_id": user_id,
        "scan_id": scan_id,
        "severity": "Critical" if any(f["severity"] == "Critical" for f in critical_high) else "High",
        "message": f"{len(critical_high)} critical/high severity issues detected in your AWS environment.",
        "affected_service": "multiple",
        "sent_status": "sent" if sent else "failed",
        "channel": "email",
        "created_at": datetime.utcnow(),
    }
    result = await db["alerts"].insert_one(alert_doc)
    alert_doc["_id"] = str(result.inserted_id)
    alerts_created.append(alert_doc)

    return alerts_created


def _build_email_body(scan_id: str, findings: List[Dict[str, Any]]) -> str:
    """Build HTML email body for alert."""
    rows = ""
    for f in findings:
        color = "#dc2626" if f["severity"] == "Critical" else "#ea580c"
        rows += f"""
        <tr>
          <td style="padding:8px;border:1px solid #e5e7eb">{f.get('service','').upper()}</td>
          <td style="padding:8px;border:1px solid #e5e7eb">{f.get('issue_title','')}</td>
          <td style="padding:8px;border:1px solid #e5e7eb;color:{color};font-weight:bold">{f.get('severity','')}</td>
          <td style="padding:8px;border:1px solid #e5e7eb">{f.get('resource_id','')}</td>
        </tr>"""

    return f"""
    <html><body style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto">
      <div style="background:#1e293b;color:white;padding:20px;border-radius:8px 8px 0 0">
        <h1 style="margin:0">🛡️ CloudGuard AI Security Alert</h1>
        <p style="margin:5px 0 0">Scan ID: {scan_id}</p>
      </div>
      <div style="padding:20px;background:#f8fafc;border:1px solid #e2e8f0">
        <p>The following <strong>Critical/High</strong> security issues were detected in your AWS environment:</p>
        <table style="width:100%;border-collapse:collapse;margin-top:16px">
          <thead>
            <tr style="background:#1e293b;color:white">
              <th style="padding:10px;text-align:left">Service</th>
              <th style="padding:10px;text-align:left">Issue</th>
              <th style="padding:10px;text-align:left">Severity</th>
              <th style="padding:10px;text-align:left">Resource</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
        <p style="margin-top:20px">
          <strong>Action Required:</strong> Log in to CloudGuard AI to view detailed findings and remediation steps.
        </p>
      </div>
      <div style="padding:12px;background:#1e293b;color:#94a3b8;text-align:center;border-radius:0 0 8px 8px;font-size:12px">
        CloudGuard AI – AWS Cloud Security Monitoring
      </div>
    </body></html>
    """


async def _send_email(subject: str, body: str, demo: bool = False) -> bool:
    """Send email via AWS SES. Returns True on success."""
    if not settings.ALERT_EMAIL_FROM or settings.DEMO_MODE or demo:
        print(f"[Alert] Demo mode – email not sent: {subject}")
        return True  # Simulate success in demo mode

    try:
        ses = boto3.client("ses", region_name=settings.SES_REGION)
        ses.send_email(
            Source=settings.ALERT_EMAIL_FROM,
            Destination={"ToAddresses": [settings.ALERT_EMAIL_TO]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Html": {"Data": body, "Charset": "UTF-8"}},
            },
        )
        print(f"[Alert] Email sent: {subject}")
        return True
    except (ClientError, NoCredentialsError) as e:
        print(f"[Alert] SES error: {e}")
        return False


async def get_user_alerts(user_id: str, limit: int = 50) -> List[Dict]:
    """Fetch alert history for a user."""
    db = get_database()
    cursor = db["alerts"].find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    alerts = []
    async for alert in cursor:
        alert["_id"] = str(alert["_id"])
        alerts.append(alert)
    return alerts
