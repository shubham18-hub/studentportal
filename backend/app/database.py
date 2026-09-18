from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None
_mongo_connected: bool = False

async def connect_to_mongo():
    """Connect to MongoDB with pooling for 1k+ students.
    
    Idempotent - can be called multiple times safely.
    Only connects once. Subsequent calls are no-ops.
    Safe to call even if already connected or if connection is in progress.
    
    This is designed for lazy connection - called on first request, not at startup.
    """
    global client, db, _mongo_connected
    
    # If already connected, skip
    if _mongo_connected and client is not None and db is not None:
        logger.debug("MongoDB already connected, skipping reconnection")
        return
    
    # If client exists but not marked as connected, try to use it
    if client is not None and not _mongo_connected:
        logger.debug("MongoDB client exists but not marked as connected, attempting reconnection verification...")
        try:
            await asyncio.wait_for(db.command("ping"), timeout=2.0)
            _mongo_connected = True
            logger.info("MongoDB reconnection verified")
            return
        except Exception:
            logger.debug("MongoDB reconnection verification failed, will attempt fresh connection")
            client = None
            db = None
    
    try:
        logger.info("Attempting to connect to MongoDB...")
        # Connection pool settings optimized for 1k students
        client = AsyncIOMotorClient(
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
            logger.warning("MongoDB ping timed out, but connection object created. Will use connection anyway.")
            _mongo_connected = True
            
    except asyncio.TimeoutError as e:
        logger.warning(f"MongoDB connection timeout: {e}")
        logger.warning("Connection will be retried on next request.")
        _mongo_connected = False
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.warning("Connection will be retried on next request.")
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

async def get_db() -> AsyncIOMotorDatabase:
    """Get MongoDB database instance.
    
    Lazily attempts to connect if not already connected.
    On first call, will attempt to establish MongoDB connection.
    Subsequent calls will reuse the connection.
    
    Returns the db connection if available.
    Raises RuntimeError if database cannot be connected.
    """
    global db, _mongo_connected
    
    # If not connected, try to connect now (lazy connection)
    if not _mongo_connected:
        logger.info("First database request - attempting lazy MongoDB connection...")
        await connect_to_mongo()
    
    # If still not connected after attempt, raise error
    if db is None or not _mongo_connected:
        raise RuntimeError("Database not connected - MongoDB unavailable")
    
    return db

def is_mongo_connected() -> bool:
    """Check if MongoDB is currently connected."""
    return _mongo_connected
