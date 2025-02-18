import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import logging

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Local MongoDB settings
LOCAL_MONGODB_URL = "mongodb://localhost:27017"
LOCAL_DB_NAME = "recruitment_ai"

async def migrate_collection(source_db, dest_db, collection_name):
    """Migrate a single collection from source to destination"""
    try:
        logger.info(f"Migrating collection: {collection_name}")
        
        # Get all documents from source
        documents = await source_db[collection_name].find().to_list(None)
        logger.info(f"Found {len(documents)} documents in {collection_name}")
        
        if documents:
            # Insert documents into destination
            result = await dest_db[collection_name].insert_many(documents)
            logger.info(f"Inserted {len(result.inserted_ids)} documents into {collection_name}")
        
        return len(documents)
    except Exception as e:
        logger.error(f"Error migrating collection {collection_name}: {str(e)}")
        return 0

async def migrate_data():
    """Migrate all data from local MongoDB to Atlas"""
    try:
        # Connect to local MongoDB
        logger.info("Connecting to local MongoDB...")
        local_client = AsyncIOMotorClient(LOCAL_MONGODB_URL)
        local_db = local_client[LOCAL_DB_NAME]
        
        # Test local connection
        await local_client.admin.command('ping')
        logger.info("Successfully connected to local MongoDB")
        
        # Connect to Atlas
        logger.info("Connecting to MongoDB Atlas...")
        atlas_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            server_api=ServerApi('1')
        )
        atlas_db = atlas_client[settings.MONGODB_DB_NAME]
        
        # Test Atlas connection
        await atlas_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas")
        
        # Collections to migrate
        collections = ['users', 'jobs', 'candidates']
        
        # Migrate each collection
        total_documents = 0
        for collection in collections:
            count = await migrate_collection(local_db, atlas_db, collection)
            total_documents += count
        
        logger.info(f"Migration completed. Total documents migrated: {total_documents}")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise
    finally:
        # Close connections
        if 'local_client' in locals():
            local_client.close()
        if 'atlas_client' in locals():
            atlas_client.close()

if __name__ == "__main__":
    asyncio.run(migrate_data()) 