from motor.motor_asyncio import AsyncClient, AsyncDatabase
from app.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

client: AsyncClient = None
db: AsyncDatabase = None
_mongo_connected: bool = False

async def connect_to_mongo():
    """Connect to MongoDB with pooling for 1k+ students.
    
    Can be called multiple times safely - will only connect once.
    Logs failures but doesn't crash the app (graceful degradation).
    """
    global client, db, _mongo_connected
    
    # If already connected, skip
    if _mongo_connected and client is not None and db is not None:
        logger.debug("MongoDB already connected, skipping reconnection")
        return
    
    try:
        logger.info("Attempting to connect to MongoDB...")
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
        
        # Verify connection with timeout
        try:
            await asyncio.wait_for(db.command("ping"), timeout=5.0)
            _mongo_connected = True
            logger.info("Connected to MongoDB successfully with connection pooling")
        except asyncio.TimeoutError:
            logger.warning("MongoDB ping timed out, but connection object created. Will retry on first request.")
            _mongo_connected = True
            
    except asyncio.TimeoutError as e:
        logger.warning(f"MongoDB connection timeout (this is normal during startup delays): {e}")
        logger.warning("App starting in DEGRADED MODE - MongoDB unavailable. Requests will fail with database errors.")
        _mongo_connected = False
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.warning("App starting in DEGRADED MODE - MongoDB unavailable. Requests will fail with database errors.")
        _mongo_connected = False

async def create_indexes():
    """Create database indexes for performance.
    
    Handles gracefully if indexes already exist or connection is degraded.
    """
    global db
    if db is None:
        logger.warning("Cannot create indexes - database not connected")
        return
        
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
        logger.warning(f"Failed to create indexes (will retry later): {e}")

async def close_mongo():
    """Close MongoDB connection safely.
    
    Can be called multiple times safely - checks if connection exists first.
    """
    global client, _mongo_connected
    if client is not None:
        try:
            client.close()
            _mongo_connected = False
            logger.info("Closed MongoDB connection")
        except Exception as e:
            logger.warning(f"Error closing MongoDB connection: {e}")

def get_db() -> AsyncDatabase:
    """Get MongoDB database instance.
    
    Raises RuntimeError if database is not connected.
    Returns the db connection if available (even in degraded mode).
    """
    global db
    if db is None:
        raise RuntimeError("Database not connected - service is in degraded mode")
    return db

def is_mongo_connected() -> bool:
    """Check if MongoDB is currently connected."""
    return _mongo_connected
