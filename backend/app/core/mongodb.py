import motor.motor_asyncio
from typing import Optional
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
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGODB_URL,
            server_api=ServerApi('1'),
            maxPoolSize=10,
            minPoolSize=1
        )
        self.db = self.client[settings.MONGODB_DB_NAME]
        
        # Initialize GridFS
        self.fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(self.db)
        
        # Create collections if they don't exist
        collections = await self.db.list_collection_names()
        logger.info(f"Existing collections: {collections}")
        
        if "users" not in collections:
            logger.info("Creating users collection")
            await self.db.create_collection("users")
        if "jobs" not in collections:
            logger.info("Creating jobs collection")
            await self.db.create_collection("jobs")
        if "candidates" not in collections:
            logger.info("Creating candidates collection")
            await self.db.create_collection("candidates")
        
        # Verify connection
        try:
            # The ping command is cheap and does not require auth.
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}", exc_info=True)
            raise

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            logger.info("Closing MongoDB connection")
            self.client.close()

    def get_db(self) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        """Get database instance"""
        if self.db is None:
            raise Exception("Database not initialized")
        return self.db

    def get_gridfs(self) -> motor.motor_asyncio.AsyncIOMotorGridFSBucket:
        """Get GridFS instance"""
        if self.fs is None:
            raise Exception("GridFS not initialized")
        return self.fs

# Global MongoDB instance
mongodb = MongoDB()

async def connect_to_mongo():
    """Connect to MongoDB on startup"""
    await mongodb.connect()

async def close_mongo_connection():
    """Close MongoDB connection on shutdown"""
    if mongodb.client:
        mongodb.close()

def get_database() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """Get database instance"""
    return mongodb.get_db()

def get_gridfs() -> motor.motor_asyncio.AsyncIOMotorGridFSBucket:
    """Get GridFS instance"""
    return mongodb.get_gridfs() 