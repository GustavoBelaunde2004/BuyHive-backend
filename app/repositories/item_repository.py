"""Item repository for database operations."""
from typing import Optional, Dict, Any, List
from app.repositories.base import BaseRepository
from app.core.database import items_collection


class ItemRepository(BaseRepository):
    """Repository for item database operations."""
    
    def __init__(self):
        super().__init__(items_collection)
    
    async def find_by_id(self, user_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Find item by user_id and item_id.
        
        Args:
            user_id: User ID
            item_id: Item ID
            
        Returns:
            Item document or None if not found
        """
        return await self.find_one({"user_id": user_id, "item_id": item_id})
    
    async def find_by_ids(self, user_id: str, item_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Find multiple items by their IDs.
        
        Args:
            user_id: User ID
            item_ids: List of item IDs
            
        Returns:
            List of item documents
        """
        return await self.find_many({"user_id": user_id, "item_id": {"$in": item_ids}})
    
    async def find_by_url(self, user_id: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Find item by user_id and URL.
        
        Args:
            user_id: User ID
            url: Item URL
            
        Returns:
            Item document or None if not found
        """
        return await self.find_one({"user_id": user_id, "url": str(url)})
    
    async def create(self, item_data: Dict[str, Any]) -> None:
        """
        Create a new item.
        
        Args:
            item_data: Item document dictionary (must include user_id)
        """
        await self.insert_one(item_data)
    
    async def update(self, user_id: str, item_id: str, update_data: Dict[str, Any]) -> int:
        """
        Update item data.
        
        Args:
            user_id: User ID
            item_id: Item ID
            update_data: Update dictionary
            
        Returns:
            Number of matched documents
        """
        return await self.update_one(
            {"user_id": user_id, "item_id": item_id},
            {"$set": update_data}
        )
    
    async def delete(self, user_id: str, item_id: str) -> bool:
        """
        Delete an item.
        
        Args:
            user_id: User ID
            item_id: Item ID
            
        Returns:
            True if deleted, False otherwise
        """
        return await self.delete_one({"user_id": user_id, "item_id": item_id})
    
    async def update_selected_carts(self, user_id: str, item_id: str, cart_ids: List[str]) -> int:
        """
        Update item's selected_cart_ids array.
        
        Args:
            user_id: User ID
            item_id: Item ID
            cart_ids: List of cart IDs
            
        Returns:
            Number of matched documents
        """
        return await self.update_one(
            {"user_id": user_id, "item_id": item_id},
            {"$set": {"selected_cart_ids": list(dict.fromkeys(cart_ids))}}
        )
    
    async def remove_cart_from_selected(self, user_id: str, item_id: str, cart_id: str) -> int:
        """
        Remove cart_id from item's selected_cart_ids array.
        
        Args:
            user_id: User ID
            item_id: Item ID
            cart_id: Cart ID to remove
            
        Returns:
            Number of matched documents
        """
        return await self.update_one(
            {"user_id": user_id, "item_id": item_id},
            {"$pull": {"selected_cart_ids": cart_id}}
        )

