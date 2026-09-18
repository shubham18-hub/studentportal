from motor.motor_asyncio import AsyncClient, AsyncDatabase
from app.config import settings
import logging

logger = logging.getLogger(__name__)

client: AsyncClient = None
db: AsyncDatabase = None

async def connect_to_mongo():
    """Connect to MongoDB with pooling for 1k+ students."""
    global client, db
    try:
        # Connection pool settings optimized for 1k students
        client = AsyncClient(
            settings.mongodb_uri,
            maxPoolSize=settings.mongodb_pool_size,
            minPoolSize=10,
            maxIdleTimeMS=45000,
            waitQueueTimeoutMS=10000,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=5000,
            retryWrites=True,
        )
        db = client["ecell"]
        
        # Create indexes for performance
        await create_indexes()
        
        # Verify connection
        await db.command("ping")
        logger.info("Connected to MongoDB successfully with connection pooling")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def create_indexes():
    """Create database indexes for performance."""
    try:
        # Users indexes
        users_col = db["users"]
        await users_col.create_index("email", unique=True)
        await users_col.create_index("google_id", sparse=True)
        
        # Tasks indexes
        tasks_col = db["tasks"]
        await tasks_col.create_index("stage")
        await tasks_col.create_index("deadline")
        await tasks_col.create_index("created_by")
        
        # Submissions indexes
        submissions_col = db["submissions"]
        await submissions_col.create_index([("task_id", 1), ("user_id", 1)], unique=True)
        await submissions_col.create_index("task_id")
        await submissions_col.create_index("user_id")
        await submissions_col.create_index("status")
        await submissions_col.create_index("submitted_at")
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")

async def close_mongo():
    """Close MongoDB connection."""
    global client
    if client is not None:
        client.close()
        logger.info("Closed MongoDB connection")

def get_db() -> AsyncDatabase:
    """Get MongoDB database instance."""
    if db is None:
        raise RuntimeError("Database not connected")
    return db
