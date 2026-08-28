"""
CloudGuard AI – AWS connection request/response schemas.
"""

from typing import Optional
from pydantic import BaseModel


class AWSConnectRequest(BaseModel):
    account_name: str
    region: str = "us-east-1"
    # Production: provide role ARN
    role_arn: Optional[str] = None
    # Demo / direct key mode
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    use_demo: bool = False


class AWSStatusResponse(BaseModel):
    account_id: str
    account_name: str
    region: str
    connection_status: str
    is_demo: bool
    last_validated: Optional[str] = None
