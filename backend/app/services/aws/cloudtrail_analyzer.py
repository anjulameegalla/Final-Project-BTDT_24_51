"""
CloudGuard AI – CloudTrail Log Analyzer
Detects: failed logins, root usage, IAM changes, key creation, suspicious API calls.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import boto3
from botocore.exceptions import ClientError


DEMO_FINDINGS = [
    {
        "service": "cloudtrail",
        "resource_id": "root",
        "issue_title": "Root Account Login Detected",
        "severity": "Critical",
        "description": "Root account was used to log into the AWS console. Root usage should be avoided.",
    },
    {
        "service": "cloudtrail",
        "resource_id": "arn:aws:iam::123456789012:user/dev-user",
        "issue_title": "Multiple Failed Console Login Attempts",
        "severity": "High",
        "description": "User 'dev-user' had 7 failed console login attempts in the last 24 hours.",
    },
    {
        "service": "cloudtrail",
        "resource_id": "arn:aws:iam::123456789012:user/admin-user",
        "issue_title": "IAM Policy Modified",
        "severity": "High",
        "description": "IAM policy was modified by 'admin-user'. Unauthorized policy changes can escalate privileges.",
    },
    {
        "service": "cloudtrail",
        "resource_id": "arn:aws:iam::123456789012:user/ci-user",
        "issue_title": "New Access Key Created",
        "severity": "Medium",
        "description": "A new access key was created for user 'ci-user'. Verify this was intentional.",
    },
    {
        "service": "cloudtrail",
        "resource_id": "203.0.113.42",
        "issue_title": "API Activity From Unknown IP Address",
        "severity": "High",
        "description": "AWS API calls were made from IP 203.0.113.42 which is not in the known IP whitelist.",
    },
]

# Events that indicate suspicious activity
SUSPICIOUS_EVENTS = {
    "ConsoleLogin": "Console Login",
    "CreateAccessKey": "Access Key Created",
    "DeleteAccessKey": "Access Key Deleted",
    "AttachUserPolicy": "IAM Policy Attached",
    "DetachUserPolicy": "IAM Policy Detached",
    "PutUserPolicy": "Inline Policy Added",
    "DeleteUserPolicy": "Inline Policy Deleted",
    "CreateUser": "IAM User Created",
    "DeleteUser": "IAM User Deleted",
    "UpdateLoginProfile": "Login Profile Updated",
    "CreateLoginProfile": "Login Profile Created",
}


class CloudTrailAnalyzer:
    def __init__(self, session: boto3.Session):
        self.ct = session.client("cloudtrail")
        self.lookback_hours = 24

    def scan(self) -> List[Dict[str, Any]]:
        findings = []
        events = self._fetch_events()
        findings.extend(self._check_root_usage(events))
        findings.extend(self._check_failed_logins(events))
        findings.extend(self._check_iam_changes(events))
        findings.extend(self._check_key_creation(events))
        return findings

    # ── Fetch Events ─────────────────────────────────────────────────────────
    def _fetch_events(self) -> List[Dict]:
        events = []
        try:
            start_time = datetime.now(timezone.utc) - timedelta(hours=self.lookback_hours)
            paginator = self.ct.get_paginator("lookup_events")
            for page in paginator.paginate(
                StartTime=start_time,
                EndTime=datetime.now(timezone.utc),
            ):
                events.extend(page.get("Events", []))
        except ClientError as e:
            print(f"[CloudTrail] Fetch error: {e}")
        return events

    # ── Root Account Usage ───────────────────────────────────────────────────
    def _check_root_usage(self, events: List[Dict]) -> List[Dict[str, Any]]:
        findings = []
        for event in events:
            username = event.get("Username", "")
            if username.lower() in ("root", "aws:root"):
                findings.append({
                    "service": "cloudtrail",
                    "resource_id": "root",
                    "issue_title": "Root Account Activity Detected",
                    "severity": "Critical",
                    "description": f"Root account performed action '{event.get('EventName')}' "
                                   f"at {event.get('EventTime')}. Root usage is strongly discouraged.",
                })
        return findings

    # ── Failed Console Logins ────────────────────────────────────────────────
    def _check_failed_logins(self, events: List[Dict]) -> List[Dict[str, Any]]:
        findings = []
        failed: Dict[str, int] = {}
        for event in events:
            if event.get("EventName") == "ConsoleLogin":
                import json
                try:
                    detail = json.loads(event.get("CloudTrailEvent", "{}"))
                    if detail.get("responseElements", {}).get("ConsoleLogin") == "Failure":
                        user = event.get("Username", "unknown")
                        failed[user] = failed.get(user, 0) + 1
                except Exception:
                    pass
        for user, count in failed.items():
            if count >= 3:
                findings.append({
                    "service": "cloudtrail",
                    "resource_id": f"arn:aws:iam::user/{user}",
                    "issue_title": "Multiple Failed Console Login Attempts",
                    "severity": "High" if count >= 5 else "Medium",
                    "description": f"User '{user}' had {count} failed console login attempts in the last "
                                   f"{self.lookback_hours} hours. Possible brute-force attack.",
                })
        return findings

    # ── IAM Policy Changes ───────────────────────────────────────────────────
    def _check_iam_changes(self, events: List[Dict]) -> List[Dict[str, Any]]:
        findings = []
        iam_change_events = {
            "AttachUserPolicy", "DetachUserPolicy", "PutUserPolicy",
            "DeleteUserPolicy", "CreateUser", "DeleteUser",
            "AttachRolePolicy", "DetachRolePolicy", "PutRolePolicy",
        }
        for event in events:
            if event.get("EventName") in iam_change_events:
                findings.append({
                    "service": "cloudtrail",
                    "resource_id": event.get("Username", "unknown"),
                    "issue_title": "IAM Configuration Changed",
                    "severity": "High",
                    "description": f"IAM action '{event.get('EventName')}' was performed by "
                                   f"'{event.get('Username')}' at {event.get('EventTime')}.",
                })
        return findings

    # ── Access Key Creation ──────────────────────────────────────────────────
    def _check_key_creation(self, events: List[Dict]) -> List[Dict[str, Any]]:
        findings = []
        for event in events:
            if event.get("EventName") == "CreateAccessKey":
                findings.append({
                    "service": "cloudtrail",
                    "resource_id": event.get("Username", "unknown"),
                    "issue_title": "New Access Key Created",
                    "severity": "Medium",
                    "description": f"A new access key was created by '{event.get('Username')}' "
                                   f"at {event.get('EventTime')}. Verify this was intentional.",
                })
        return findings


def run_cloudtrail_scan(session: boto3.Session, demo: bool = False) -> List[Dict[str, Any]]:
    """Entry point: run CloudTrail analysis or return demo data."""
    if demo:
        return DEMO_FINDINGS
    analyzer = CloudTrailAnalyzer(session)
    return analyzer.scan()
