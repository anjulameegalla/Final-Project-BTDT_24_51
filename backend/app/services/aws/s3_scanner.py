"""
CloudGuard AI – S3 Security Scanner
Detects: public buckets, public policies, encryption disabled, versioning off, logging off.
"""

import json
from typing import List, Dict, Any
import boto3
from botocore.exceptions import ClientError


DEMO_FINDINGS = [
    {
        "service": "s3",
        "resource_id": "arn:aws:s3:::my-public-bucket",
        "issue_title": "S3 Bucket Is Publicly Accessible",
        "severity": "Critical",
        "description": "Bucket 'my-public-bucket' has Block Public Access disabled and is accessible to the internet.",
    },
    {
        "service": "s3",
        "resource_id": "arn:aws:s3:::my-data-bucket",
        "issue_title": "S3 Bucket Policy Allows Public Access",
        "severity": "Critical",
        "description": "Bucket 'my-data-bucket' has a bucket policy that grants public read access (Principal: *).",
    },
    {
        "service": "s3",
        "resource_id": "arn:aws:s3:::backup-bucket",
        "issue_title": "S3 Bucket Encryption Disabled",
        "severity": "Medium",
        "description": "Bucket 'backup-bucket' does not have server-side encryption enabled.",
    },
    {
        "service": "s3",
        "resource_id": "arn:aws:s3:::logs-bucket",
        "issue_title": "S3 Bucket Versioning Disabled",
        "severity": "Low",
        "description": "Bucket 'logs-bucket' does not have versioning enabled, risking data loss.",
    },
    {
        "service": "s3",
        "resource_id": "arn:aws:s3:::assets-bucket",
        "issue_title": "S3 Bucket Access Logging Disabled",
        "severity": "Low",
        "description": "Bucket 'assets-bucket' does not have access logging enabled.",
    },
]


class S3Scanner:
    def __init__(self, session: boto3.Session):
        self.s3 = session.client("s3")

    def scan(self) -> List[Dict[str, Any]]:
        findings = []
        try:
            buckets = self.s3.list_buckets().get("Buckets", [])
        except ClientError as e:
            print(f"[S3] Cannot list buckets: {e}")
            return findings

        for bucket in buckets:
            name = bucket["Name"]
            arn = f"arn:aws:s3:::{name}"
            findings.extend(self._check_public_access(name, arn))
            findings.extend(self._check_bucket_policy(name, arn))
            findings.extend(self._check_encryption(name, arn))
            findings.extend(self._check_versioning(name, arn))
            findings.extend(self._check_logging(name, arn))
        return findings

    # ── Public Access Block ──────────────────────────────────────────────────
    def _check_public_access(self, name: str, arn: str) -> List[Dict[str, Any]]:
        findings = []
        try:
            config = self.s3.get_public_access_block(Bucket=name)
            block = config["PublicAccessBlockConfiguration"]
            if not all([
                block.get("BlockPublicAcls"),
                block.get("IgnorePublicAcls"),
                block.get("BlockPublicPolicy"),
                block.get("RestrictPublicBuckets"),
            ]):
                findings.append({
                    "service": "s3",
                    "resource_id": arn,
                    "issue_title": "S3 Bucket Is Publicly Accessible",
                    "severity": "Critical",
                    "description": f"Bucket '{name}' has Block Public Access settings disabled.",
                })
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
                findings.append({
                    "service": "s3",
                    "resource_id": arn,
                    "issue_title": "S3 Bucket Is Publicly Accessible",
                    "severity": "Critical",
                    "description": f"Bucket '{name}' has no Block Public Access configuration.",
                })
        return findings

    # ── Bucket Policy Public Access ──────────────────────────────────────────
    def _check_bucket_policy(self, name: str, arn: str) -> List[Dict[str, Any]]:
        findings = []
        try:
            policy_str = self.s3.get_bucket_policy(Bucket=name)["Policy"]
            policy = json.loads(policy_str)
            for stmt in policy.get("Statement", []):
                principal = stmt.get("Principal", "")
                effect = stmt.get("Effect", "")
                if effect == "Allow" and (principal == "*" or principal == {"AWS": "*"}):
                    findings.append({
                        "service": "s3",
                        "resource_id": arn,
                        "issue_title": "S3 Bucket Policy Allows Public Access",
                        "severity": "Critical",
                        "description": f"Bucket '{name}' policy grants public access (Principal: *).",
                    })
                    break
        except ClientError as e:
            if e.response["Error"]["Code"] != "NoSuchBucketPolicy":
                print(f"[S3] Policy check error for {name}: {e}")
        return findings

    # ── Encryption ───────────────────────────────────────────────────────────
    def _check_encryption(self, name: str, arn: str) -> List[Dict[str, Any]]:
        findings = []
        try:
            self.s3.get_bucket_encryption(Bucket=name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ServerSideEncryptionConfigurationNotFoundError":
                findings.append({
                    "service": "s3",
                    "resource_id": arn,
                    "issue_title": "S3 Bucket Encryption Disabled",
                    "severity": "Medium",
                    "description": f"Bucket '{name}' does not have server-side encryption enabled.",
                })
        return findings

    # ── Versioning ───────────────────────────────────────────────────────────
    def _check_versioning(self, name: str, arn: str) -> List[Dict[str, Any]]:
        findings = []
        try:
            resp = self.s3.get_bucket_versioning(Bucket=name)
            if resp.get("Status") != "Enabled":
                findings.append({
                    "service": "s3",
                    "resource_id": arn,
                    "issue_title": "S3 Bucket Versioning Disabled",
                    "severity": "Low",
                    "description": f"Bucket '{name}' does not have versioning enabled.",
                })
        except ClientError as e:
            print(f"[S3] Versioning check error for {name}: {e}")
        return findings

    # ── Logging ──────────────────────────────────────────────────────────────
    def _check_logging(self, name: str, arn: str) -> List[Dict[str, Any]]:
        findings = []
        try:
            resp = self.s3.get_bucket_logging(Bucket=name)
            if "LoggingEnabled" not in resp:
                findings.append({
                    "service": "s3",
                    "resource_id": arn,
                    "issue_title": "S3 Bucket Access Logging Disabled",
                    "severity": "Low",
                    "description": f"Bucket '{name}' does not have access logging enabled.",
                })
        except ClientError as e:
            print(f"[S3] Logging check error for {name}: {e}")
        return findings


def run_s3_scan(session: boto3.Session, demo: bool = False) -> List[Dict[str, Any]]:
    """Entry point: run S3 scan or return demo data."""
    if demo:
        return DEMO_FINDINGS
    scanner = S3Scanner(session)
    return scanner.scan()
