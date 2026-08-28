"""
CloudGuard AI – Scan request/response schemas.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class ScanStartRequest(BaseModel):
    aws_account_id: str
    services: Optional[List[str]] = ["iam", "s3", "ec2", "cloudtrail"]


class FindingOut(BaseModel):
    id: str
    service: str
    resource_id: str
    issue_title: str
    severity: str
    description: str
    ai_explanation: Optional[str] = None
    recommendation: Optional[str] = None
    fix_steps: Optional[List[str]] = None
    status: str


class ScanOut(BaseModel):
    id: str
    user_id: str
    aws_account_id: str
    scan_date: datetime
    status: str
    overall_score: int
    risk_level: str
    total_issues: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    findings: List[Dict[str, Any]]
    service_scores: Dict[str, int]
    created_at: datetime
