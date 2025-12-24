from datetime import datetime
from uuid import uuid4
from typing import Dict, Any, List
from .database import carts_collection, items_collection
from app.models.item import ItemInDB

# GET items from cart
async def retrieve_cart_items(user_id: str, cart_id: str) -> List[ItemInDB]:
    """
    Retrieve all items from a specific cart for a given user.
    Returns list of ItemInDB objects.
    
    Raises:
        ValueError: If cart is not found
    """
    cart_doc = await carts_collection.find_one({"user_id": user_id, "cart_id": cart_id})
    if not cart_doc:
        raise ValueError("Cart not found!")

    item_ids = cart_doc.get("item_ids", [])
    items: List[ItemInDB] = []
    if item_ids:
        item_docs = await items_collection.find(
            {"user_id": user_id, "item_id": {"$in": item_ids}}
        ).to_list(length=None)
        doc_by_id = {d.get("item_id"): d for d in item_docs}
        for iid in item_ids:
            if iid in doc_by_id:
                items.append(ItemInDB.from_mongo(doc_by_id[iid]))

    return items

# PUT (Edits notes for all appearances of same item in every cart per user)
async def update_item_note(user_id: str, item_id: str, new_note: str) -> ItemInDB:
    """
    Update the note for all occurrences of the item across all carts of a user.
    Returns the updated item details as ItemInDB model.
    """
    result = await items_collection.update_one(
        {"user_id": user_id, "item_id": item_id},
        {"$set": {"notes": new_note}},
    )
    if result.matched_count == 0:
        raise ValueError("Item not found!")

    updated_item_doc = await items_collection.find_one({"user_id": user_id, "item_id": item_id})
    if not updated_item_doc:
        raise ValueError("Item was updated but not found after update.")
    return ItemInDB.from_mongo(updated_item_doc)


# DELETE item from cart
async def delete_item(user_id: str, cart_id: str, item_id: str) -> Dict[str, str]:
    """
    Delete a specific item from a cart and update its selected_cart_ids.
    If the item is in other carts, remove the cart from selected_cart_ids.
    If it’s the last cart, fully remove the item.
    """
    # Remove from cart
    cart = await carts_collection.find_one({"user_id": user_id, "cart_id": cart_id})
    if not cart:
        return {"message": "Cart or item not found!"}

    if item_id not in (cart.get("item_ids") or []):
        return {"message": "Cart or item not found!"}

    await carts_collection.update_one(
        {"user_id": user_id, "cart_id": cart_id},
        {"$pull": {"item_ids": item_id}, "$inc": {"item_count": -1}},
    )

    # Remove cart_id from item.selected_cart_ids
    item_doc = await items_collection.find_one({"user_id": user_id, "item_id": item_id})
    if not item_doc:
        return {"message": "Cart or item not found!"}

    await items_collection.update_one(
        {"user_id": user_id, "item_id": item_id},
        {"$pull": {"selected_cart_ids": cart_id}},
    )
    updated_item = await items_collection.find_one({"user_id": user_id, "item_id": item_id})
    selected_cart_ids = (updated_item or {}).get("selected_cart_ids") or []

    if not selected_cart_ids:
        await items_collection.delete_one({"user_id": user_id, "item_id": item_id})
        return {"message": "Item fully deleted from all carts."}

    return {"message": f"Item removed from cart {cart_id}, updated selected_cart_ids."}


# ADD NEW ITEM ACROSS SELECTED CARTS
async def add_new_item_across_carts(user_id: str, item_details: dict, selected_cart_ids: List[str]) -> Dict[str, Any]:
    """
    Add a new item with a unique item_id across selected carts.
    Prevents adding duplicate items (same URL) that already exist in any of the user's carts.
    Returns the details of the newly added item.
    """
    url = item_details.get("url")
    if url:
        existing = await items_collection.find_one({"user_id": user_id, "url": str(url)})
        if existing:
            # Fetch a cart name for messaging if possible
            cart_name = None
            cart_ids = existing.get("selected_cart_ids") or []
            if cart_ids:
                cart_doc = await carts_collection.find_one({"user_id": user_id, "cart_id": cart_ids[0]})
                if cart_doc:
                    cart_name = cart_doc.get("cart_name")
            msg_cart = f"'{cart_name}'" if cart_name else "an existing cart"
            return {
                "message": f"Item already exists in {msg_cart}. Move it instead.",
                "existing_item": ItemInDB.from_mongo(existing),
            }

    # Validate carts exist for this user
    for cart_id in selected_cart_ids:
        cart_doc = await carts_collection.find_one({"user_id": user_id, "cart_id": cart_id})
        if not cart_doc:
            raise ValueError(f"Cart not found: {cart_id}")

    # Create item document once
    item_details["item_id"] = str(uuid4())
    item_details["added_at"] = datetime.utcnow().isoformat()
    item_details["selected_cart_ids"] = list(dict.fromkeys(selected_cart_ids))
    item_in_db = ItemInDB.from_mongo(item_details)
    await items_collection.insert_one(item_in_db.to_mongo_dict() | {"user_id": user_id})

    # Add item_id to each selected cart
    for cart_id in selected_cart_ids:
        await carts_collection.update_one(
            {"user_id": user_id, "cart_id": cart_id},
            {"$addToSet": {"item_ids": item_in_db.item_id}, "$inc": {"item_count": 1}},
        )

    return {"message": "New item added successfully across selected carts.", "item": item_in_db}

# MODIFY EXISTING ITEM ACROSS CARTS
async def modify_existing_item_across_carts(user_id: str, item_id: str, selected_cart_ids: List[str]) -> ItemInDB:
    """
    Move an existing item across selected carts.
    - Ensures the item is **added** to selected carts if not already there.
    - Ensures the item is **removed** from deselected carts.
    - Updates the `selected_cart_ids` attribute correctly in all carts.
    - Returns the updated item as ItemInDB.
    """
    item_doc = await items_collection.find_one({"user_id": user_id, "item_id": item_id})
    if not item_doc:
        raise ValueError("Item not found!")

    current_cart_ids = set(item_doc.get("selected_cart_ids") or [])
    target_cart_ids = set(selected_cart_ids or [])

    remove_from_cart_ids = list(current_cart_ids - target_cart_ids)
    add_to_cart_ids = list(target_cart_ids - current_cart_ids)

    # Validate target carts exist
    for cart_id in target_cart_ids:
        cart_doc = await carts_collection.find_one({"user_id": user_id, "cart_id": cart_id})
        if not cart_doc:
            raise ValueError(f"Cart not found: {cart_id}")

    for cart_id in remove_from_cart_ids:
        await carts_collection.update_one(
            {"user_id": user_id, "cart_id": cart_id},
            {"$pull": {"item_ids": item_id}, "$inc": {"item_count": -1}},
        )

    for cart_id in add_to_cart_ids:
        await carts_collection.update_one(
            {"user_id": user_id, "cart_id": cart_id},
            {"$addToSet": {"item_ids": item_id}, "$inc": {"item_count": 1}},
        )

    updated_cart_ids = list(dict.fromkeys(selected_cart_ids))
    await items_collection.update_one(
        {"user_id": user_id, "item_id": item_id},
        {"$set": {"selected_cart_ids": updated_cart_ids}},
    )

    updated_item_doc = await items_collection.find_one({"user_id": user_id, "item_id": item_id})
    if not updated_item_doc:
        raise ValueError("Item was moved but not found after update.")
    return ItemInDB.from_mongo(updated_item_doc)

# Nuclear delete - removes item from all carts
async def nuke(user_id: str, item_id: str) -> Dict[str, str]:
    """
    Deletes an item from all carts for a given user.
    """
    item_doc = await items_collection.find_one({"user_id": user_id, "item_id": item_id})
    if not item_doc:
        return {"message": "Item not found in any cart!"}

    cart_ids = item_doc.get("selected_cart_ids") or []
    modified_count = 0
    for cart_id in cart_ids:
        cart = await carts_collection.find_one({"user_id": user_id, "cart_id": cart_id})
        if not cart:
            continue
        if item_id not in (cart.get("item_ids") or []):
            continue
        result = await carts_collection.update_one(
            {"user_id": user_id, "cart_id": cart_id},
            {"$pull": {"item_ids": item_id}, "$inc": {"item_count": -1}},
        )
        if getattr(result, "modified_count", 0) > 0:
            modified_count += 1

    await items_collection.delete_one({"user_id": user_id, "item_id": item_id})
    return {"message": f"Item successfully deleted from {modified_count} cart(s)."}
