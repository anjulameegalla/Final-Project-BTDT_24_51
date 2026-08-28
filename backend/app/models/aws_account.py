"""
CloudGuard AI – AWS Account database model.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.user import PyObjectId


class AWSAccountModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    account_name: str
    region: str = "us-east-1"
    # Either role_arn (production) or demo mode
    role_arn: Optional[str] = None
    access_key_id: Optional[str] = None        # stored encrypted / masked
    secret_access_key_encrypted: Optional[str] = None
    is_demo: bool = False
    connection_status: str = "pending"          # pending | connected | failed
    last_validated: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
