"""User repository for database operations."""
from typing import Optional, Dict, Any
from app.repositories.base import BaseRepository
from app.core.database import users_collection
from datetime import datetime


class UserRepository(BaseRepository):
    """Repository for user database operations."""
    
    def __init__(self):
        super().__init__(users_collection)
    
    async def find_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Find user by user_id.
        
        Args:
            user_id: User ID (Auth0 sub)
            
        Returns:
            User document or None if not found
        """
        return await self.find_one({"user_id": user_id})
    
    async def create(self, user_data: Dict[str, Any]) -> str:
        """
        Create a new user.
        
        Args:
            user_data: User document dictionary
            
        Returns:
            User ID
        """
        await self.collection.insert_one(user_data)
        return user_data.get("user_id")
    
    async def update(self, user_id: str, update_data: Dict[str, Any]) -> int:
        """
        Update user data.
        
        Args:
            user_id: User ID
            update_data: Update dictionary
            
        Returns:
            Number of matched documents
        """
        return await self.update_one({"user_id": user_id}, {"$set": update_data})
    
    async def add_cart_id(self, user_id: str, cart_id: str, now: str) -> int:
        """
        Add cart_id to user's cart_ids array and increment cart_count.
        
        Args:
            user_id: User ID
            cart_id: Cart ID to add
            now: ISO datetime string for updated_at
            
        Returns:
            Number of matched documents
        """
        return await self.update_one(
            {"user_id": user_id},
            {
                "$push": {"cart_ids": cart_id},
                "$inc": {"cart_count": 1},
                "$set": {"updated_at": now},
            }
        )
    
    async def remove_cart_id(self, user_id: str, cart_id: str, now: str) -> int:
        """
        Remove cart_id from user's cart_ids array and decrement cart_count.
        
        Args:
            user_id: User ID
            cart_id: Cart ID to remove
            now: ISO datetime string for updated_at
            
        Returns:
            Number of matched documents
        """
        return await self.update_one(
            {"user_id": user_id},
            {
                "$pull": {"cart_ids": cart_id},
                "$inc": {"cart_count": -1},
                "$set": {"updated_at": now},
            }
        )

