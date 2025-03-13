# This file is deprecated, use app.core.mongodb instead
from app.core.mongodb import get_database, get_gridfs, connect_to_mongo, close_mongo_connection

# Re-export the functions for backward compatibility
__all__ = ['get_database', 'get_gridfs', 'connect_to_mongo', 'close_mongo_connection'] 