"""
CloudGuard AI – Utility helpers.
"""

from datetime import datetime
import base64
import hashlib
from bson import ObjectId
from cryptography.fernet import Fernet
from app.config import settings


def serialize_doc(doc: dict) -> dict:
    """Recursively convert ObjectId and datetime to JSON-serializable types."""
    if doc is None:
        return {}
    result = {}
    for k, v in doc.items():
        if k == "_id":
            result["id"] = str(v)
        elif isinstance(v, ObjectId):
            result[k] = str(v)
        elif isinstance(v, datetime):
            result[k] = v.isoformat()
        elif isinstance(v, dict):
            result[k] = serialize_doc(v)
        elif isinstance(v, list):
            result[k] = [serialize_doc(i) if isinstance(i, dict) else i for i in v]
        else:
            result[k] = v
    return result


def paginate(cursor, page: int = 1, page_size: int = 20):
    """Apply skip/limit pagination to a Motor cursor."""
    skip = (page - 1) * page_size
    return cursor.skip(skip).limit(page_size)


def _credential_cipher() -> Fernet:
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
    return Fernet(key)


def encrypt_credential(value: str) -> str:
    return _credential_cipher().encrypt(value.encode()).decode()


def decrypt_credential(value: str) -> str:
    return _credential_cipher().decrypt(value.encode()).decode()
