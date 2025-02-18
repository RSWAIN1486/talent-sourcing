import motor.motor_asyncio
from typing import Optional, AsyncGenerator
from fastapi import Depends
from app.core.config import settings
import logging
from pymongo.server_api import ServerApi
from pymongo import MongoClient

logger = logging.getLogger(__name__)

# Global MongoDB client instance
client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None

async def get_database() -> AsyncGenerator[motor.motor_asyncio.AsyncIOMotorDatabase, None]:
    """Get database instance as a dependency"""
    global client  # Single global declaration at the start
    
    try:
        if client is None:
            logger.info(f"Connecting to MongoDB at {settings.MONGODB_CLUSTER}")
            logger.info(f"Using database: {settings.MONGODB_DB_NAME}")
            logger.info(f"Username: {settings.MONGODB_USERNAME}")
            
            # Create MongoDB client with optimized settings for serverless
            client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.MONGODB_URL,
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                maxPoolSize=1,  # Minimize connections for serverless
                minPoolSize=0,
                waitQueueTimeoutMS=5000,
                retryWrites=True,
                retryReads=True,
                tls=True,
                tlsAllowInvalidCertificates=True
            )
            
            # Test connection
            await client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas")
            
            # Initialize collections if needed
            db = client[settings.MONGODB_DB_NAME]
            collections = await db.list_collection_names()
            required_collections = ["users", "jobs", "candidates"]
            
            for collection in required_collections:
                if collection not in collections:
                    logger.info(f"Creating {collection} collection")
                    await db.create_collection(collection)
        
        yield client[settings.MONGODB_DB_NAME]
    except Exception as e:
        logger.error(f"MongoDB connection error: {str(e)}", exc_info=True)
        if client:
            client.close()
            client = None
        raise

async def get_gridfs() -> AsyncGenerator[motor.motor_asyncio.AsyncIOMotorGridFSBucket, None]:
    """Get GridFS instance as a dependency"""
    try:
        async for db in get_database():
            fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(db)
            yield fs
    except Exception as e:
        logger.error(f"GridFS error: {str(e)}", exc_info=True)
        raise

async def connect_to_mongo():
    """Connect to MongoDB on startup"""
    try:
        async for _ in get_database():
            pass  # Just test the connection
        logger.info("Initial MongoDB connection successful")
    except Exception as e:
        logger.error(f"Failed to establish initial MongoDB connection: {str(e)}", exc_info=True)
        raise

async def close_mongo_connection():
    """Close MongoDB connection on shutdown"""
    global client
    if client:
        client.close()
        client = None
        logger.info("Closed MongoDB connection") 