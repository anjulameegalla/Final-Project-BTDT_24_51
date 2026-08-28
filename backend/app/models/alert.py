"""
CloudGuard AI – Alert database model.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.user import PyObjectId


class AlertModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    scan_id: str
    finding_id: Optional[str] = None
    severity: str
    message: str
    affected_service: str
    sent_status: str = "pending"    # pending | sent | failed
    channel: str = "email"          # email | sns
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
