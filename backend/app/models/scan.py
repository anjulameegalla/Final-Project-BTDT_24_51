"""
CloudGuard AI – Scan and Finding database models.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.user import PyObjectId


class FindingModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    scan_id: str
    service: str                    # iam | s3 | ec2 | cloudtrail
    resource_id: str
    issue_title: str
    severity: str                   # Low | Medium | High | Critical
    description: str
    ai_explanation: Optional[str] = None
    recommendation: Optional[str] = None
    fix_steps: Optional[List[str]] = None
    status: str = "open"            # open | resolved | ignored
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ScanModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    aws_account_id: str
    scan_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = "running"         # running | completed | failed
    overall_score: int = 0
    risk_level: str = "Unknown"
    total_issues: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    findings: List[Dict[str, Any]] = []
    service_scores: Dict[str, int] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
