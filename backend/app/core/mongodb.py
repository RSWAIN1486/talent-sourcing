import motor.motor_asyncio
import asyncio
from typing import Optional
from app.core.config import settings
import logging
from pymongo.server_api import ServerApi

logger = logging.getLogger(__name__)

# ✅ Global MongoDB client and database instance
client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None

async def connect_to_mongo():
    """✅ Connect to MongoDB on startup without closing event loop."""
    global client, database
    if client is None:
        try:
            logger.info(f"🔌 Connecting to MongoDB at {settings.MONGODB_CLUSTER}")
            
            # ✅ Fix for event loop issues
            loop = asyncio.get_running_loop()
            client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.MONGODB_URL,
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=5000,  # 5 seconds
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                maxPoolSize=10,  # ✅ Increase connection pool for Vercel
                minPoolSize=1,
                waitQueueTimeoutMS=5000,
                retryWrites=True,
                retryReads=True,
                tls=True,
                tlsAllowInvalidCertificates=True,
                io_loop=loop  # ✅ Ensures proper async execution
            )
            database = client[settings.MONGODB_DB_NAME]

            # ✅ Test connection
            await client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB Atlas")

        except Exception as e:
            logger.error(f"🚨 MongoDB connection error: {str(e)}", exc_info=True)
            client = None
            database = None
            raise

def get_database():
    """✅ Get database instance (NOT async)"""
    global database
    if database is None:
        raise RuntimeError("MongoDB connection is not established. Call `connect_to_mongo()` first.")
    return database

async def get_gridfs():
    """✅ Get GridFS instance asynchronously"""
    try:
        db = get_database()
        return motor.motor_asyncio.AsyncIOMotorGridFSBucket(db)
    except Exception as e:
        logger.error(f"🚨 GridFS error: {str(e)}", exc_info=True)
        raise

async def close_mongo_connection():
    """✅ Prevent closing event loop on Vercel"""
    global client
    if client:
        logger.info("🔄 Skipping MongoDB connection shutdown to avoid event loop issues.")
