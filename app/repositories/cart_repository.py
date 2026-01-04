"""Cart repository for database operations."""
from typing import Optional, Dict, Any, List
from app.repositories.base import BaseRepository
from app.core.database import carts_collection
from app.models.cart import Cart


class CartRepository(BaseRepository):
    """Repository for cart database operations."""
    
    def __init__(self):
        super().__init__(carts_collection)
    
    async def find_by_id(self, user_id: str, cart_id: str) -> Optional[Dict[str, Any]]:
        """
        Find cart by user_id and cart_id.
        
        Args:
            user_id: User ID
            cart_id: Cart ID
            
        Returns:
            Cart document or None if not found
        """
        return await self.find_one({"user_id": user_id, "cart_id": cart_id})
    
    async def find_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Find all carts for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of cart documents
        """
        return await self.find_many({"user_id": user_id})
    
    async def create(self, cart_data: Dict[str, Any]) -> None:
        """
        Create a new cart.
        
        Args:
            cart_data: Cart document dictionary
        """
        await self.insert_one(cart_data)
    
    async def update(self, user_id: str, cart_id: str, update_data: Dict[str, Any]) -> int:
        """
        Update cart data.
        
        Args:
            user_id: User ID
            cart_id: Cart ID
            update_data: Update dictionary
            
        Returns:
            Number of matched documents
        """
        return await self.update_one(
            {"user_id": user_id, "cart_id": cart_id},
            {"$set": update_data}
        )
    
    async def delete(self, user_id: str, cart_id: str) -> bool:
        """
        Delete a cart.
        
        Args:
            user_id: User ID
            cart_id: Cart ID
            
        Returns:
            True if deleted, False otherwise
        """
        return await self.delete_one({"user_id": user_id, "cart_id": cart_id})
    
    async def add_item_id(self, user_id: str, cart_id: str, item_id: str) -> int:
        """
        Add item_id to cart's item_ids array and increment item_count.
        
        Args:
            user_id: User ID
            cart_id: Cart ID
            item_id: Item ID to add
            
        Returns:
            Number of matched documents
        """
        return await self.update_one(
            {"user_id": user_id, "cart_id": cart_id},
            {"$addToSet": {"item_ids": item_id}, "$inc": {"item_count": 1}}
        )
    
    async def remove_item_id(self, user_id: str, cart_id: str, item_id: str) -> int:
        """
        Remove item_id from cart's item_ids array and decrement item_count.
        
        Args:
            user_id: User ID
            cart_id: Cart ID
            item_id: Item ID to remove
            
        Returns:
            Number of matched documents
        """
        return await self.update_one(
            {"user_id": user_id, "cart_id": cart_id},
            {"$pull": {"item_ids": item_id}, "$inc": {"item_count": -1}}
        )
    
    async def update_item_count(self, user_id: str, cart_id: str, increment: int) -> int:
        """
        Update item_count by increment.
        
        Args:
            user_id: User ID
            cart_id: Cart ID
            increment: Amount to increment (can be negative)
            
        Returns:
            Number of matched documents
        """
        return await self.update_one(
            {"user_id": user_id, "cart_id": cart_id},
            {"$inc": {"item_count": increment}}
        )

