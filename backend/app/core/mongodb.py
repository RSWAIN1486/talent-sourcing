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
    """✅ Connect to MongoDB on startup and keep it alive."""
    global client, database
    if client is None:
        try:
            logger.info(f"🔌 Connecting to MongoDB at {settings.MONGODB_CLUSTER}")

            # ✅ Ensure the event loop is running
            loop = asyncio.get_running_loop()
            client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.MONGODB_URL,
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=5000,  # 5 seconds
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                maxPoolSize=10,  # ✅ Keep persistent connections
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


async def ensure_mongo_connection():
    """✅ Ensure MongoDB is connected before returning database."""
    global database
    if database is None:
        logger.warning("⚠️ Database is not connected. Reconnecting...")
        await connect_to_mongo()
    return database  # ✅ Return actual database instance


async def get_database():
    """✅ Always ensure MongoDB is connected before returning the database."""
    return await ensure_mongo_connection()


async def get_gridfs():
    """✅ Get GridFS instance asynchronously"""
    try:
        db = await ensure_mongo_connection()  # ✅ Ensure connection is active
        return motor.motor_asyncio.AsyncIOMotorGridFSBucket(db)
    except Exception as e:
        logger.error(f"🚨 GridFS error: {str(e)}", exc_info=True)
        raise


async def close_mongo_connection():
    """✅ Prevent closing MongoDB connection in Vercel"""
    global client
    if client:
        logger.info("🔄 Skipping MongoDB connection shutdown to avoid event loop issues.")
