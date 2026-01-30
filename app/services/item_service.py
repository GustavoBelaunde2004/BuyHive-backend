"""Item service for business logic."""
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any, List
from app.repositories.cart_repository import CartRepository
from app.repositories.item_repository import ItemRepository
from app.models.item import ItemInDB


class DuplicateItemError(ValueError):
    """Raised when trying to create an item that already exists."""
    def __init__(self, message: str, existing_item: ItemInDB):
        super().__init__(message)
        self.existing_item = existing_item


class ItemService:
    """Service for item business logic."""
    
    def __init__(
        self,
        item_repo: ItemRepository,
        cart_repo: CartRepository
    ):
        """
        Initialize item service with repositories.
        
        Args:
            item_repo: Item repository instance
            cart_repo: Cart repository instance
        """
        self.item_repo = item_repo
        self.cart_repo = cart_repo
    
    async def get_cart_items(self, user_id: str, cart_id: str) -> List[ItemInDB]:
        """
        Retrieve all items from a specific cart.
        
        Args:
            user_id: User ID
            cart_id: Cart ID
            
        Returns:
            List of ItemInDB models
            
        Raises:
            ValueError: If cart not found
        """
        cart_doc = await self.cart_repo.find_by_id(user_id, cart_id)
        if not cart_doc:
            raise ValueError("Cart not found!")
        
        item_ids = cart_doc.get("item_ids", [])
        items: List[ItemInDB] = []
        
        if item_ids:
            item_docs = await self.item_repo.find_by_ids(user_id, item_ids)
            doc_by_id = {d.get("item_id"): d for d in item_docs}
            for iid in item_ids:
                if iid in doc_by_id:
                    items.append(ItemInDB.from_mongo(doc_by_id[iid]))
        
        return items
    

    async def create_item(
        self,
        user_id: str,
        item_details: Dict[str, Any],
        selected_cart_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Create a new item across selected carts.
        
        Args:
            user_id: User ID
            item_details: Item details dictionary
            selected_cart_ids: List of cart IDs to add item to
            
        Returns:
            Dictionary with message and item
            
        Raises:
            ValueError: If cart not found
            DuplicateItemError: If item with same URL already exists
        """
        url = item_details.get("url")
        
        # Check for duplicate URL
        if url:
            existing = await self.item_repo.find_by_url(user_id, str(url))
            if existing:
                # Fetch a cart name for messaging if possible
                cart_name = None
                cart_ids = existing.get("selected_cart_ids") or []
                if cart_ids:
                    cart_doc = await self.cart_repo.find_by_id(user_id, cart_ids[0])
                    if cart_doc:
                        cart_name = cart_doc.get("cart_name")
                msg_cart = f"'{cart_name}'" if cart_name else "an existing cart"
                existing_item = ItemInDB.from_mongo(existing)
                raise DuplicateItemError(
                    f"Item already exists in {msg_cart}. Move it instead.",
                    existing_item
                )
        
        # Validate carts exist
        for cart_id in selected_cart_ids:
            cart_doc = await self.cart_repo.find_by_id(user_id, cart_id)
            if not cart_doc:
                raise ValueError(f"Cart not found: {cart_id}")
        
        # Create item document
        item_details["item_id"] = str(uuid4())
        item_details["added_at"] = datetime.utcnow().isoformat()
        item_details["selected_cart_ids"] = list(dict.fromkeys(selected_cart_ids))
        item_in_db = ItemInDB.from_mongo(item_details)
        
        # Save item with user_id
        await self.item_repo.create(item_in_db.to_mongo_dict() | {"user_id": user_id})
        
        # Add item_id to each selected cart
        for cart_id in selected_cart_ids:
            await self.cart_repo.add_item_id(user_id, cart_id, item_in_db.item_id)
        
        return {"message": "New item added successfully across selected carts.", "item": item_in_db}
    
    async def update_item_note(self, user_id: str, item_id: str, new_note: str) -> ItemInDB:
        """
        Update the note for an item across all carts.
        
        Args:
            user_id: User ID
            item_id: Item ID
            new_note: New note text
            
        Returns:
            Updated ItemInDB model
            
        Raises:
            ValueError: If item not found
        """
        result = await self.item_repo.update(user_id, item_id, {"notes": new_note})
        if result == 0:
            raise ValueError("Item not found!")
        
        updated_item_doc = await self.item_repo.find_by_id(user_id, item_id)
        if not updated_item_doc:
            raise ValueError("Item was updated but not found after update.")
        
        return ItemInDB.from_mongo(updated_item_doc)
    
    async def move_item(
        self,
        user_id: str,
        item_id: str,
        selected_cart_ids: List[str]
    ) -> ItemInDB:
        """
        Move an existing item across selected carts.
        
        Args:
            user_id: User ID
            item_id: Item ID
            selected_cart_ids: List of cart IDs to move item to
            
        Returns:
            Updated ItemInDB model
            
        Raises:
            ValueError: If item or cart not found
        """
        item_doc = await self.item_repo.find_by_id(user_id, item_id)
        if not item_doc:
            raise ValueError("Item not found!")
        
        current_cart_ids = set(item_doc.get("selected_cart_ids") or [])
        target_cart_ids = set(selected_cart_ids or [])
        
        remove_from_cart_ids = list(current_cart_ids - target_cart_ids)
        add_to_cart_ids = list(target_cart_ids - current_cart_ids)
        
        # Validate target carts exist
        for cart_id in target_cart_ids:
            cart_doc = await self.cart_repo.find_by_id(user_id, cart_id)
            if not cart_doc:
                raise ValueError(f"Cart not found: {cart_id}")
        
        # Remove from deselected carts
        for cart_id in remove_from_cart_ids:
            await self.cart_repo.remove_item_id(user_id, cart_id, item_id)
        
        # Add to newly selected carts
        for cart_id in add_to_cart_ids:
            await self.cart_repo.add_item_id(user_id, cart_id, item_id)
        
        # Update item's selected_cart_ids
        updated_cart_ids = list(dict.fromkeys(selected_cart_ids))
        await self.item_repo.update_selected_carts(user_id, item_id, updated_cart_ids)
        
        updated_item_doc = await self.item_repo.find_by_id(user_id, item_id)
        if not updated_item_doc:
            raise ValueError("Item was moved but not found after update.")
        
        return ItemInDB.from_mongo(updated_item_doc)
    
    async def delete_item(
        self,
        user_id: str,
        cart_id: str,
        item_id: str
    ) -> Dict[str, str]:
        """
        Delete an item from a cart.
        
        Args:
            user_id: User ID
            cart_id: Cart ID
            item_id: Item ID
            
        Returns:
            Dictionary with success message
        """
        cart = await self.cart_repo.find_by_id(user_id, cart_id)
        if not cart:
            return {"message": "Cart or item not found!"}
        
        if item_id not in (cart.get("item_ids") or []):
            return {"message": "Cart or item not found!"}
        
        # Remove from cart
        await self.cart_repo.remove_item_id(user_id, cart_id, item_id)
        
        # Remove cart_id from item's selected_cart_ids
        item_doc = await self.item_repo.find_by_id(user_id, item_id)
        if not item_doc:
            return {"message": "Cart or item not found!"}
        
        await self.item_repo.remove_cart_from_selected(user_id, item_id, cart_id)
        
        # Check if item is orphaned and delete if so
        updated_item = await self.item_repo.find_by_id(user_id, item_id)
        selected_cart_ids = (updated_item or {}).get("selected_cart_ids") or []
        
        if not selected_cart_ids:
            await self.item_repo.delete(user_id, item_id)
            return {"message": "Item fully deleted from all carts."}
        
        return {"message": f"Item removed from cart {cart_id}, updated selected_cart_ids."}
    
    async def delete_item_from_all_carts(self, user_id: str, item_id: str) -> Dict[str, str]:
        """
        Delete an item from all carts (nuke).
        
        Args:
            user_id: User ID
            item_id: Item ID
            
        Returns:
            Dictionary with success message
        """
        item_doc = await self.item_repo.find_by_id(user_id, item_id)
        if not item_doc:
            return {"message": "Item not found in any cart!"}
        
        cart_ids = item_doc.get("selected_cart_ids") or []
        modified_count = 0
        
        for cart_id in cart_ids:
            cart = await self.cart_repo.find_by_id(user_id, cart_id)
            if not cart:
                continue
            if item_id not in (cart.get("item_ids") or []):
                continue
            
            result = await self.cart_repo.remove_item_id(user_id, cart_id, item_id)
            if result > 0:
                modified_count += 1
        
        await self.item_repo.delete(user_id, item_id)
        return {"message": f"Item successfully deleted from {modified_count} cart(s)."}

