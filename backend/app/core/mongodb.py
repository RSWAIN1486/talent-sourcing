import motor.motor_asyncio
from typing import Optional
from app.core.config import settings
import logging
from pymongo.server_api import ServerApi

logger = logging.getLogger(__name__)

# Global MongoDB client and database instance
client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None

async def connect_to_mongo():
    """Connect to MongoDB on startup"""
    global client, database
    if client is None:
        try:
            logger.info(f"🔌 Connecting to MongoDB at {settings.MONGODB_CLUSTER}")
            client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.MONGODB_URL,
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=5000,  # 5 seconds
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                maxPoolSize=5,  # Allow up to 5 connections
                minPoolSize=1,
                waitQueueTimeoutMS=5000,
                retryWrites=True,
                retryReads=True,
                tls=True,
                tlsAllowInvalidCertificates=True
            )
            database = client[settings.MONGODB_DB_NAME]

            # Test connection
            await client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB Atlas")

        except Exception as e:
            logger.error(f"🚨 MongoDB connection error: {str(e)}", exc_info=True)
            client = None
            database = None
            raise

async def get_database():
    """Get database instance"""
    global database
    if database is None:
        await connect_to_mongo()
    return database

async def get_gridfs():
    """Get GridFS instance"""
    try:
        db = await get_database()
        return motor.motor_asyncio.AsyncIOMotorGridFSBucket(db)
    except Exception as e:
        logger.error(f"🚨 GridFS error: {str(e)}", exc_info=True)
        raise

async def close_mongo_connection():
    """Close MongoDB connection on shutdown"""
    global client
    if client:
        client.close()
        client = None
        logger.info("🔌 Closed MongoDB connection")
