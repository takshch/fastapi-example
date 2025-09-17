"""
Base service class for common database operations.

This module provides a base service class that other services can inherit from
to get common database operations and logging functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError, OperationFailure

from app.database import get_collection
from app.core.logging import get_logger
from app.core.exceptions import DatabaseError, ConflictError, NotFoundError

T = TypeVar('T')


class BaseService(ABC, Generic[T]):
    """Base service class for database operations."""
    
    def __init__(self, collection_name: str):
        """
        Initialize the service.
        
        Args:
            collection_name: Name of the MongoDB collection
        """
        self.collection_name = collection_name
        self.logger = get_logger(f"services.{self.__class__.__name__}")
    
    async def get_collection(self) -> AsyncIOMotorCollection:
        """
        Get the MongoDB collection.
        
        Returns:
            AsyncIOMotorCollection: MongoDB collection instance
        """
        return await get_collection(self.collection_name)
    
    async def create_document(self, document: Dict[str, Any]) -> str:
        """
        Create a new document in the collection.
        
        Args:
            document: Document data to insert
            
        Returns:
            str: ID of the created document
            
        Raises:
            ConflictError: If document already exists
            DatabaseError: If database operation fails
        """
        try:
            collection = await self.get_collection()
            result = await collection.insert_one(document)
            
            self.logger.info(
                f"Created document in {self.collection_name}",
                extra={"document_id": str(result.inserted_id)}
            )
            
            return str(result.inserted_id)
            
        except DuplicateKeyError as e:
            self.logger.warning(f"Duplicate key error in {self.collection_name}: {e}")
            raise ConflictError(f"Document already exists: {e}")
        except OperationFailure as e:
            self.logger.error(f"Database operation failed in {self.collection_name}: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error creating document in {self.collection_name}: {e}")
            raise DatabaseError(f"Unexpected error creating document: {e}")
    
    async def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by its ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Optional[Dict[str, Any]]: Document data or None if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            from bson import ObjectId
            
            collection = await self.get_collection()
            document = await collection.find_one({"_id": ObjectId(document_id)})
            
            if document:
                self.logger.debug(f"Retrieved document from {self.collection_name}", extra={"document_id": document_id})
            else:
                self.logger.debug(f"Document not found in {self.collection_name}", extra={"document_id": document_id})
            
            return document
            
        except Exception as e:
            self.logger.error(f"Error retrieving document from {self.collection_name}: {e}")
            raise DatabaseError(f"Error retrieving document: {e}")
    
    async def update_document(self, document_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a document by its ID.
        
        Args:
            document_id: Document ID
            update_data: Data to update
            
        Returns:
            bool: True if document was updated, False if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            from bson import ObjectId
            
            collection = await self.get_collection()
            result = await collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                self.logger.info(f"Updated document in {self.collection_name}", extra={"document_id": document_id})
                return True
            else:
                self.logger.warning(f"Document not found for update in {self.collection_name}", extra={"document_id": document_id})
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating document in {self.collection_name}: {e}")
            raise DatabaseError(f"Error updating document: {e}")
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document by its ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            bool: True if document was deleted, False if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            from bson import ObjectId
            
            collection = await self.get_collection()
            result = await collection.delete_one({"_id": ObjectId(document_id)})
            
            if result.deleted_count > 0:
                self.logger.info(f"Deleted document from {self.collection_name}", extra={"document_id": document_id})
                return True
            else:
                self.logger.warning(f"Document not found for deletion in {self.collection_name}", extra={"document_id": document_id})
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting document from {self.collection_name}: {e}")
            raise DatabaseError(f"Error deleting document: {e}")
    
    async def count_documents(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents in the collection.
        
        Args:
            filter_dict: Optional filter criteria
            
        Returns:
            int: Number of documents matching the filter
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            collection = await self.get_collection()
            count = await collection.count_documents(filter_dict or {})
            
            self.logger.debug(f"Counted {count} documents in {self.collection_name}")
            return count
            
        except Exception as e:
            self.logger.error(f"Error counting documents in {self.collection_name}: {e}")
            raise DatabaseError(f"Error counting documents: {e}")
    
    async def find_documents(
        self,
        filter_dict: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 0,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find documents in the collection.
        
        Args:
            filter_dict: Optional filter criteria
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            sort: Sort criteria as list of tuples
            
        Returns:
            List[Dict[str, Any]]: List of documents
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            collection = await self.get_collection()
            cursor = collection.find(filter_dict or {})
            
            if sort:
                cursor = cursor.sort(sort)
            if skip > 0:
                cursor = cursor.skip(skip)
            if limit > 0:
                cursor = cursor.limit(limit)
            
            documents = await cursor.to_list(length=None)
            
            self.logger.debug(f"Found {len(documents)} documents in {self.collection_name}")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error finding documents in {self.collection_name}: {e}")
            raise DatabaseError(f"Error finding documents: {e}")
    
    @abstractmethod
    async def validate_document(self, document: Dict[str, Any]) -> None:
        """
        Validate document data before operations.
        
        Args:
            document: Document data to validate
            
        Raises:
            ValidationError: If validation fails
        """
        pass
