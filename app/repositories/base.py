"""Base repository with common MongoDB operations."""
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from motor.motor_asyncio import AsyncIOMotorCollection


class BaseRepository(ABC):
    """Abstract base repository providing common MongoDB operations."""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        """
        Initialize repository with a MongoDB collection.
        
        Args:
            collection: Motor async collection instance
        """
        self.collection = collection
    
    async def find_one(self, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document.
        
        Args:
            filter: MongoDB filter dictionary
            
        Returns:
            Document dictionary or None if not found
        """
        return await self.collection.find_one(filter)
    
    async def find_many(self, filter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find multiple documents.
        
        Args:
            filter: MongoDB filter dictionary
            
        Returns:
            List of document dictionaries
        """
        cursor = self.collection.find(filter)
        return await cursor.to_list(length=None)
    
    async def insert_one(self, document: Dict[str, Any]) -> str:
        """
        Insert a single document.
        
        Args:
            document: Document dictionary to insert
            
        Returns:
            Inserted document ID as string
        """
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)
    
    async def update_one(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any]
    ) -> int:
        """
        Update a single document.
        
        Args:
            filter: MongoDB filter dictionary
            update: MongoDB update dictionary
            
        Returns:
            Number of matched documents
        """
        result = await self.collection.update_one(filter, update)
        return result.matched_count
    
    async def delete_one(self, filter: Dict[str, Any]) -> bool:
        """
        Delete a single document.
        
        Args:
            filter: MongoDB filter dictionary
            
        Returns:
            True if document was deleted, False otherwise
        """
        result = await self.collection.delete_one(filter)
        return result.deleted_count > 0
    
    async def count_documents(self, filter: Dict[str, Any]) -> int:
        """
        Count documents matching filter.
        
        Args:
            filter: MongoDB filter dictionary
            
        Returns:
            Number of matching documents
        """
        return await self.collection.count_documents(filter)

