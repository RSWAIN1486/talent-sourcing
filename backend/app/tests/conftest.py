import pytest
import motor.motor_asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.core.mongodb import get_database
from app.core.config import settings

# Global variables for test MongoDB connection
class TestMongoDB:
    client = None
    db = None

# Create a test MongoDB instance
test_mongodb = TestMongoDB()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_db():
    """Create a test database and handle cleanup"""
    # Create test client
    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.MONGODB_URL,
        maxPoolSize=10,
        minPoolSize=1
    )
    db = client[settings.MONGODB_DB_NAME + "_test"]
    
    # Initialize collections
    collections = await db.list_collection_names()
    if "users" not in collections:
        await db.create_collection("users")
    if "jobs" not in collections:
        await db.create_collection("jobs")
    if "candidates" not in collections:
        await db.create_collection("candidates")
    
    # Override the get_database() function to return test database
    def get_test_database():
        return db
    
    # Replace the get_database function
    app.dependency_overrides[get_database] = get_test_database
    
    # Store the test database in the test MongoDB instance
    test_mongodb.client = client
    test_mongodb.db = db
    
    try:
        yield db
    finally:
        # Cleanup
        try:
            await client.drop_database(settings.MONGODB_DB_NAME + "_test")
        except Exception:
            pass
        
        try:
            await client.close()
        except Exception:
            pass
            
        app.dependency_overrides.clear()
        test_mongodb.client = None
        test_mongodb.db = None

@pytest.fixture
def client(test_db):
    """Create a test client with test database."""
    return TestClient(app) 