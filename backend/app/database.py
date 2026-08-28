"""
CloudGuard AI – MongoDB async database connection.
Uses real MongoDB if available, otherwise falls back to mongomock for local dev/demo.
"""

import os
from app.config import settings

client = None
_use_mock = False


async def connect_db():
    """Open the MongoDB connection pool."""
    global client, _use_mock

    # Try real MongoDB first
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        test_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=3000,
        )
        # Ping to verify connection
        await test_client.admin.command("ping")
        client = test_client
        _use_mock = False
        print(f"[DB] Connected to MongoDB at {settings.MONGODB_URL}")
    except Exception as e:
        print(f"[DB] Real MongoDB unavailable ({e}), using in-memory mock database.")
        try:
            from mongomock_motor import AsyncMongoMockClient
            client = AsyncMongoMockClient()
            _use_mock = True
            print("[DB] mongomock_motor in-memory database active (demo mode)")
        except ImportError:
            raise RuntimeError(
                "Neither MongoDB nor mongomock_motor is available. "
                "Run: pip install mongomock-motor"
            )


async def close_db():
    """Close the MongoDB connection pool."""
    global client
    if client and not _use_mock:
        client.close()
        print("[DB] MongoDB connection closed")


def get_database():
    """Return the application database handle."""
    if client is None:
        raise RuntimeError("Database not initialised. Call connect_db() first.")
    return client[settings.DATABASE_NAME]
