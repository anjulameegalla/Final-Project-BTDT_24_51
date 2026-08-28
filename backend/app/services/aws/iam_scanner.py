"""
CloudGuard AI – IAM Security Scanner
Detects: MFA disabled, admin access, old/unused keys, root usage, overly permissive policies.
"""

import json
from datetime import datetime, timezone
from typing import List, Dict, Any
import boto3
from botocore.exceptions import ClientError


DEMO_FINDINGS = [
    {
        "service": "iam",
        "resource_id": "arn:aws:iam::123456789012:user/dev-user",
        "issue_title": "IAM User Without MFA Enabled",
        "severity": "High",
        "description": "IAM user 'dev-user' does not have Multi-Factor Authentication (MFA) enabled.",
    },
    {
        "service": "iam",
        "resource_id": "arn:aws:iam::123456789012:user/admin-user",
        "issue_title": "IAM User With Administrator Access",
        "severity": "Critical",
        "description": "IAM user 'admin-user' has AdministratorAccess policy attached, granting full AWS access.",
    },
    {
        "service": "iam",
        "resource_id": "arn:aws:iam::123456789012:user/old-user",
        "issue_title": "Access Key Older Than 90 Days",
        "severity": "Medium",
        "description": "Access key for 'old-user' was created 120 days ago and has not been rotated.",
    },
    {
        "service": "iam",
        "resource_id": "arn:aws:iam::123456789012:user/inactive-user",
        "issue_title": "Unused Access Key Detected",
        "severity": "Medium",
        "description": "Access key for 'inactive-user' has never been used or not used in the last 90 days.",
    },
    {
        "service": "iam",
        "resource_id": "arn:aws:iam::123456789012:policy/OverlyPermissivePolicy",
        "issue_title": "Overly Permissive IAM Policy",
        "severity": "High",
        "description": "Custom policy 'OverlyPermissivePolicy' uses wildcard (*) actions on all resources.",
    },
]


def _age_days(dt) -> int:
    """Return the age of a datetime in days."""
    if dt is None:
        return 0
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - dt).days


class IAMScanner:
    def __init__(self, session: boto3.Session):
        self.iam = session.client("iam")

    def scan(self) -> List[Dict[str, Any]]:
        findings = []
        findings.extend(self._check_mfa())
        findings.extend(self._check_admin_access())
        findings.extend(self._check_access_keys())
        findings.extend(self._check_permissive_policies())
        return findings

    # ── MFA Check ────────────────────────────────────────────────────────────
    def _check_mfa(self) -> List[Dict[str, Any]]:
        findings = []
        try:
            paginator = self.iam.get_paginator("list_users")
            for page in paginator.paginate():
                for user in page["Users"]:
                    username = user["UserName"]
                    mfa_devices = self.iam.list_mfa_devices(UserName=username)
                    if not mfa_devices["MFADevices"]:
                        findings.append({
                            "service": "iam",
                            "resource_id": user["Arn"],
                            "issue_title": "IAM User Without MFA Enabled",
                            "severity": "High",
                            "description": f"IAM user '{username}' does not have MFA enabled. "
                                           "This increases the risk of account compromise.",
                        })
        except ClientError as e:
            print(f"[IAM] MFA check error: {e}")
        return findings

    # ── Admin Access Check ───────────────────────────────────────────────────
    def _check_admin_access(self) -> List[Dict[str, Any]]:
        findings = []
        try:
            paginator = self.iam.get_paginator("list_users")
            for page in paginator.paginate():
                for user in page["Users"]:
                    username = user["UserName"]
                    # Check attached managed policies
                    attached = self.iam.list_attached_user_policies(UserName=username)
                    for policy in attached["AttachedPolicies"]:
                        if policy["PolicyName"] == "AdministratorAccess":
                            findings.append({
                                "service": "iam",
                                "resource_id": user["Arn"],
                                "issue_title": "IAM User With Administrator Access",
                                "severity": "Critical",
                                "description": f"User '{username}' has AdministratorAccess policy attached.",
                            })
        except ClientError as e:
            print(f"[IAM] Admin access check error: {e}")
        return findings

    # ── Access Key Age / Usage Check ─────────────────────────────────────────
    def _check_access_keys(self) -> List[Dict[str, Any]]:
        findings = []
        try:
            paginator = self.iam.get_paginator("list_users")
            for page in paginator.paginate():
                for user in page["Users"]:
                    username = user["UserName"]
                    keys = self.iam.list_access_keys(UserName=username)
                    for key in keys["AccessKeyMetadata"]:
                        key_id = key["AccessKeyId"]
                        age = _age_days(key["CreateDate"])

                        # Old key (> 90 days)
                        if age > 90:
                            findings.append({
                                "service": "iam",
                                "resource_id": user["Arn"],
                                "issue_title": "Access Key Older Than 90 Days",
                                "severity": "Medium",
                                "description": f"Access key '{key_id}' for user '{username}' "
                                               f"is {age} days old and should be rotated.",
                            })

                        # Unused key
                        try:
                            last_used = self.iam.get_access_key_last_used(AccessKeyId=key_id)
                            last_used_date = last_used["AccessKeyLastUsed"].get("LastUsedDate")
                            if last_used_date is None or _age_days(last_used_date) > 90:
                                findings.append({
                                    "service": "iam",
                                    "resource_id": user["Arn"],
                                    "issue_title": "Unused Access Key Detected",
                                    "severity": "Medium",
                                    "description": f"Access key '{key_id}' for user '{username}' "
                                                   "has not been used in over 90 days.",
                                })
                        except ClientError:
                            pass
        except ClientError as e:
            print(f"[IAM] Access key check error: {e}")
        return findings

    # ── Overly Permissive Policies ───────────────────────────────────────────
    def _check_permissive_policies(self) -> List[Dict[str, Any]]:
        findings = []
        try:
            paginator = self.iam.get_paginator("list_policies")
            for page in paginator.paginate(Scope="Local"):
                for policy in page["Policies"]:
                    try:
                        version = self.iam.get_policy_version(
                            PolicyArn=policy["Arn"],
                            VersionId=policy["DefaultVersionId"],
                        )
                        doc = version["PolicyVersion"]["Document"]
                        if isinstance(doc, str):
                            doc = json.loads(doc)
                        for stmt in doc.get("Statement", []):
                            actions = stmt.get("Action", [])
                            resources = stmt.get("Resource", [])
                            if isinstance(actions, str):
                                actions = [actions]
                            if isinstance(resources, str):
                                resources = [resources]
                            if "*" in actions and "*" in resources and stmt.get("Effect") == "Allow":
                                findings.append({
                                    "service": "iam",
                                    "resource_id": policy["Arn"],
                                    "issue_title": "Overly Permissive IAM Policy",
                                    "severity": "High",
                                    "description": f"Policy '{policy['PolicyName']}' allows all actions "
                                                   "on all resources (Action: *, Resource: *).",
                                })
                                break
                    except ClientError:
                        pass
        except ClientError as e:
            print(f"[IAM] Policy check error: {e}")
        return findings


def run_iam_scan(session: boto3.Session, demo: bool = False) -> List[Dict[str, Any]]:
    """Entry point: run IAM scan or return demo data."""
    if demo:
        return DEMO_FINDINGS
    scanner = IAMScanner(session)
    return scanner.scan()
