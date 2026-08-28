"""
CloudGuard AI – Scan Orchestration Service
Coordinates all scanner modules, scoring, AI enrichment, and alerts.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from app.config import settings
from app.database import get_database
from app.services.aws.iam_scanner import run_iam_scan
from app.services.aws.s3_scanner import run_s3_scan
from app.services.aws.ec2_scanner import run_ec2_scan
from app.services.aws.cloudtrail_analyzer import run_cloudtrail_scan
from app.services.scoring_service import (
    calculate_score, calculate_service_scores, count_by_severity
)
from app.services.ai_service import generate_ai_explanation
from app.services.alert_service import send_alerts_for_scan
from bson import ObjectId
from app.utils.helpers import decrypt_credential


async def run_full_scan(
    scan_id: str,
    user_id: str,
    aws_account: Dict[str, Any],
    services: List[str],
) -> Dict[str, Any]:
    """
    Run a full security scan across selected AWS services.
    Updates the scan document in MongoDB as it progresses.
    """
    db = get_database()
    is_demo = aws_account.get("is_demo", True) or settings.DEMO_MODE

    # Build boto3 session
    session = _build_session(aws_account, is_demo)

    all_findings = []

    # ── Run scanners ──────────────────────────────────────────────────────────
    if "iam" in services:
        iam_findings = run_iam_scan(session, demo=is_demo)
        all_findings.extend(iam_findings)

    if "s3" in services:
        s3_findings = run_s3_scan(session, demo=is_demo)
        all_findings.extend(s3_findings)

    if "ec2" in services:
        ec2_findings = run_ec2_scan(session, demo=is_demo)
        all_findings.extend(ec2_findings)

    if "cloudtrail" in services:
        ct_findings = run_cloudtrail_scan(session, demo=is_demo)
        all_findings.extend(ct_findings)

    # ── Enrich with AI explanations ───────────────────────────────────────────
    enriched_findings = []
    for finding in all_findings:
        ai_data = await generate_ai_explanation(finding)
        finding["ai_explanation"] = ai_data.get("explanation", "")
        finding["recommendation"] = ai_data.get("best_practice", "")
        finding["fix_steps"] = ai_data.get("fix_steps", [])
        finding["why_dangerous"] = ai_data.get("why_dangerous", "")
        finding["business_impact"] = ai_data.get("business_impact", "")
        finding["cli_command"] = ai_data.get("cli_command", "")
        finding["id"] = str(ObjectId())
        finding["scan_id"] = scan_id
        finding["status"] = "open"
        finding["created_at"] = datetime.utcnow().isoformat()
        enriched_findings.append(finding)

    # ── Calculate scores ──────────────────────────────────────────────────────
    overall_score, risk_level = calculate_score(enriched_findings)
    service_scores = calculate_service_scores(enriched_findings)
    severity_counts = count_by_severity(enriched_findings)

    # ── Update scan document ──────────────────────────────────────────────────
    update_data = {
        "status": "completed",
        "overall_score": overall_score,
        "risk_level": risk_level,
        "total_issues": len(enriched_findings),
        "critical_count": severity_counts["Critical"],
        "high_count": severity_counts["High"],
        "medium_count": severity_counts["Medium"],
        "low_count": severity_counts["Low"],
        "findings": enriched_findings,
        "service_scores": service_scores,
    }

    await db["scans"].update_one(
        {"_id": ObjectId(scan_id)},
        {"$set": update_data},
    )

    # ── Send alerts ───────────────────────────────────────────────────────────
    await send_alerts_for_scan(scan_id, user_id, enriched_findings, demo=is_demo)

    return {**update_data, "id": scan_id}


async def run_full_scan_safely(
    scan_id: str,
    user_id: str,
    aws_account: Dict[str, Any],
    services: List[str],
) -> None:
    """Run a scan and record unexpected failures for the polling client."""
    try:
        await run_full_scan(scan_id, user_id, aws_account, services)
    except Exception as exc:
        db = get_database()
        await db["scans"].update_one(
            {"_id": ObjectId(scan_id)},
            {"$set": {"status": "failed", "error": str(exc)}},
        )
        print(f"[Scan] Scan {scan_id} failed: {exc}")


def _build_session(aws_account: Dict[str, Any], is_demo: bool) -> Optional[boto3.Session]:
    """Build a boto3 session from account config."""
    if is_demo:
        # Return a dummy session – scanners will use demo data
        return boto3.Session(region_name="us-east-1")

    region = aws_account.get("region", "us-east-1")

    # Role ARN (assume role)
    if aws_account.get("role_arn"):
        try:
            sts = boto3.client("sts")
            assumed = sts.assume_role(
                RoleArn=aws_account["role_arn"],
                RoleSessionName="CloudGuardAIScan",
            )
            creds = assumed["Credentials"]
            return boto3.Session(
                aws_access_key_id=creds["AccessKeyId"],
                aws_secret_access_key=creds["SecretAccessKey"],
                aws_session_token=creds["SessionToken"],
                region_name=region,
            )
        except ClientError as e:
            print(f"[Scan] AssumeRole failed: {e}")
            raise

    # Direct keys
    secret_access_key = aws_account.get("secret_access_key")
    encrypted_secret = aws_account.get("secret_access_key_encrypted")
    if encrypted_secret:
        secret_access_key = decrypt_credential(encrypted_secret)

    if aws_account.get("access_key_id") and secret_access_key:
        return boto3.Session(
            aws_access_key_id=aws_account["access_key_id"],
            aws_secret_access_key=secret_access_key,
            region_name=region,
        )

    # Fall back to environment / instance profile
    return boto3.Session(region_name=region)


async def validate_aws_connection(aws_account: Dict[str, Any]) -> bool:
    """Validate AWS credentials by calling STS GetCallerIdentity."""
    try:
        session = _build_session(aws_account, is_demo=False)
        sts = session.client("sts")
        await asyncio.to_thread(sts.get_caller_identity)
        return True
    except (ClientError, NoCredentialsError) as e:
        print(f"[Scan] AWS validation failed: {e}")
        return False
