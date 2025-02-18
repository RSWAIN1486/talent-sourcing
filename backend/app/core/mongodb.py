import motor.motor_asyncio
from typing import Optional, AsyncGenerator
from fastapi import Depends
from app.core.config import settings
import logging
from pymongo.server_api import ServerApi

logger = logging.getLogger(__name__)

class MongoDB:
    client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
    db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
    fs: Optional[motor.motor_asyncio.AsyncIOMotorGridFSBucket] = None

    async def connect(self):
        """Connect to MongoDB"""
        if self.client is not None:
            logger.info("Already connected to MongoDB")
            return

        try:
            logger.info(f"Connecting to MongoDB at {settings.MONGODB_CLUSTER}")
            logger.info(f"Using database: {settings.MONGODB_DB_NAME}")
            logger.info(f"Username: {settings.MONGODB_USERNAME}")
            # Don't log the full password for security
            logger.info(f"Password length: {len(settings.MONGODB_PASSWORD)}")
            
            mongo_url = settings.MONGODB_URL
            logger.info(f"Generated MongoDB URL (without credentials): {mongo_url.replace(settings.MONGODB_USERNAME + ':' + settings.MONGODB_PASSWORD, 'username:password')}")
            
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                mongo_url,
                server_api=ServerApi('1'),
                maxPoolSize=10,
                minPoolSize=1
            )
            self.db = self.client[settings.MONGODB_DB_NAME]
            
            # Initialize GridFS
            self.fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(self.db)
            
            # Verify connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas")
            
            # Create collections if they don't exist
            collections = await self.db.list_collection_names()
            logger.info(f"Existing collections: {collections}")
            
            required_collections = ["users", "jobs", "candidates"]
            for collection in required_collections:
                if collection not in collections:
                    logger.info(f"Creating {collection} collection")
                    await self.db.create_collection(collection)
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}", exc_info=True)
            if self.client:
                self.client.close()
                self.client = None
            self.db = None
            self.fs = None
            raise

    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            logger.info("Closing MongoDB connection")
            self.client.close()
            self.client = None
            self.db = None
            self.fs = None

    def get_db(self) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        """Get database instance"""
        if self.db is None:
            raise Exception("Database not initialized. Call connect() first.")
        return self.db

    def get_gridfs(self) -> motor.motor_asyncio.AsyncIOMotorGridFSBucket:
        """Get GridFS instance"""
        if self.fs is None:
            raise Exception("GridFS not initialized. Call connect() first.")
        return self.fs

# Global MongoDB instance
mongodb = MongoDB()

async def connect_to_mongo():
    """Connect to MongoDB on startup"""
    await mongodb.connect()

async def close_mongo_connection():
    """Close MongoDB connection on shutdown"""
    await mongodb.disconnect()

async def get_database() -> AsyncGenerator[motor.motor_asyncio.AsyncIOMotorDatabase, None]:
    """Get database instance as a dependency"""
    if mongodb.db is None:
        await mongodb.connect()
    try:
        yield mongodb.get_db()
    except Exception as e:
        logger.error(f"Database error: {str(e)}", exc_info=True)
        raise

async def get_gridfs() -> AsyncGenerator[motor.motor_asyncio.AsyncIOMotorGridFSBucket, None]:
    """Get GridFS instance as a dependency"""
    if mongodb.fs is None:
        await mongodb.connect()
    try:
        yield mongodb.get_gridfs()
    except Exception as e:
        logger.error(f"GridFS error: {str(e)}", exc_info=True)
        raise 