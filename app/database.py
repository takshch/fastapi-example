"""
Database connection and management.

This module handles MongoDB connections with proper error handling,
connection pooling, and lifecycle management.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from typing import Optional
import asyncio

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import DatabaseError

logger = get_logger(__name__)


class DatabaseManager:
    """Manages MongoDB database connections and operations."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._connection_lock = asyncio.Lock()
    
    async def connect(self) -> None:
        """
        Establish connection to MongoDB.
        
        Raises:
            DatabaseError: If connection fails
        """
        async with self._connection_lock:
            if self.client is not None:
                logger.warning("Database connection already exists")
                return
            
            try:
                logger.info(f"Connecting to MongoDB at {settings.mongodb_url}")
                
                self.client = AsyncIOMotorClient(
                    settings.mongodb_url,
                    serverSelectionTimeoutMS=5000,
                    maxPoolSize=settings.mongodb_max_pool_size,
                    minPoolSize=settings.mongodb_min_pool_size,
                    retryWrites=True,
                    retryReads=True
                )
                
                # Test connection
                await self.client.admin.command('ping')
                
                # Get database
                self.database = self.client[settings.database_name]
                
                logger.info("Successfully connected to MongoDB")
                
            except (ServerSelectionTimeoutError, ConnectionFailure) as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise DatabaseError(f"Failed to connect to MongoDB: {e}")
            except Exception as e:
                logger.error(f"Unexpected error connecting to MongoDB: {e}")
                raise DatabaseError(f"Unexpected error connecting to MongoDB: {e}")
    
    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        async with self._connection_lock:
            if self.client is not None:
                logger.info("Disconnecting from MongoDB")
                self.client.close()
                self.client = None
                self.database = None
                logger.info("Disconnected from MongoDB")
    
    async def get_database(self) -> AsyncIOMotorDatabase:
        """
        Get the database instance.
        
        Returns:
            AsyncIOMotorDatabase: Database instance
            
        Raises:
            DatabaseError: If not connected
        """
        if self.database is None:
            raise DatabaseError("Database not connected. Call connect() first.")
        return self.database
    
    async def health_check(self) -> bool:
        """
        Check database health.
        
        Returns:
            bool: True if database is healthy, False otherwise
        """
        try:
            if self.client is None:
                return False
            
            await self.client.admin.command('ping')
            return True
            
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False
    
    async def get_collection(self, collection_name: str):
        """
        Get a collection from the database.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection instance
            
        Raises:
            DatabaseError: If not connected
        """
        database = await self.get_database()
        return database[collection_name]


# Global database manager instance
db_manager = DatabaseManager()


async def connect_to_mongo() -> None:
    """Connect to MongoDB. Used by FastAPI lifespan."""
    await db_manager.connect()


async def close_mongo_connection() -> None:
    """Close MongoDB connection. Used by FastAPI lifespan."""
    await db_manager.disconnect()


async def get_database() -> AsyncIOMotorDatabase:
    """
    Get the database instance.
    
    Returns:
        AsyncIOMotorDatabase: Database instance
    """
    return await db_manager.get_database()


async def get_collection(collection_name: str):
    """
    Get a collection from the database.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Collection instance
    """
    return await db_manager.get_collection(collection_name)