"""Cart service for business logic."""
from datetime import datetime
from uuid import uuid4
from typing import List, Dict, Any
from app.repositories.cart_repository import CartRepository
from app.repositories.user_repository import UserRepository
from app.repositories.item_repository import ItemRepository
from app.models.cart import Cart


class CartService:
    """Service for cart business logic."""
    
    def __init__(
        self,
        cart_repo: CartRepository,
        user_repo: UserRepository,
        item_repo: ItemRepository
    ):
        """
        Initialize cart service with repositories.
        
        Args:
            cart_repo: Cart repository instance
            user_repo: User repository instance
            item_repo: Item repository instance
        """
        self.cart_repo = cart_repo
        self.user_repo = user_repo
        self.item_repo = item_repo
    
    async def create_cart(self, user_id: str, cart_name: str) -> Dict[str, str]:
        """
        Create a new cart for a user.
        
        Args:
            user_id: User ID
            cart_name: Cart name
            
        Returns:
            Dictionary with success message and cart_id
            
        Raises:
            ValueError: If user not found
        """
        # Validate user exists
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError("User not found!")
        
        # Generate cart ID
        cart_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        
        # Create cart document
        cart_doc = {
            "cart_id": cart_id,
            "user_id": user_id,
            "cart_name": cart_name,
            "item_count": 0,
            "created_at": now,
            "item_ids": [],
        }
        
        # Save cart and update user
        await self.cart_repo.create(cart_doc)
        await self.user_repo.add_cart_id(user_id, cart_id, now)
        
        return {"message": "Cart created successfully!", "cart_id": cart_id}
    
    async def get_user_carts(self, user_id: str) -> List[Cart]:
        """
        Get all carts for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Cart models
        """
        cart_docs = await self.cart_repo.find_by_user(user_id)
        carts: List[Cart] = []
        
        for cart_doc in cart_docs:
            carts.append(
                Cart(
                    cart_id=cart_doc["cart_id"],
                    cart_name=cart_doc["cart_name"],
                    item_count=cart_doc.get("item_count", 0),
                    created_at=cart_doc.get("created_at", datetime.utcnow().isoformat()),
                    item_ids=cart_doc.get("item_ids", []),
                )
            )
        
        return carts
    
    async def update_cart_name(self, user_id: str, cart_id: str, new_name: str) -> Dict[str, str]:
        """
        Update cart name.
        
        Args:
            user_id: User ID
            cart_id: Cart ID
            new_name: New cart name
            
        Returns:
            Dictionary with success message
        """
        result = await self.cart_repo.update(user_id, cart_id, {"cart_name": new_name})
        
        if result == 0:
            return {"message": "Cart not found!"}
        return {"message": "Cart name updated successfully!"}
    
    async def delete_cart(self, user_id: str, cart_id: str) -> Dict[str, str]:
        """
        Delete a cart and clean up relationships.
        
        Args:
            user_id: User ID
            cart_id: Cart ID
            
        Returns:
            Dictionary with success message
        """
        cart_doc = await self.cart_repo.find_by_id(user_id, cart_id)
        if not cart_doc:
            return {"message": "Cart not found!"}
        
        item_ids = cart_doc.get("item_ids", [])
        now = datetime.utcnow().isoformat()
        
        # Delete cart
        await self.cart_repo.delete(user_id, cart_id)
        
        # Remove cart from user
        await self.user_repo.remove_cart_id(user_id, cart_id, now)
        
        # Remove cart_id from items.selected_cart_ids, and delete orphan items
        if item_ids:
            for item_id in item_ids:
                await self.item_repo.remove_cart_from_selected(user_id, item_id, cart_id)
                updated_item = await self.item_repo.find_by_id(user_id, item_id)
                if updated_item and not (updated_item.get("selected_cart_ids") or []):
                    await self.item_repo.delete(user_id, item_id)
        
        return {"message": "Cart deleted successfully!"}

