from datetime import datetime
from uuid import uuid4
from typing import Dict, Any, List
from .database import cart_collection
from app.models.item import ItemInDB
from app.models.cart import Cart

# POST
async def add_item_to_cart(email: str, cart_id: str, item: dict) -> Dict[str, Any]:
    """Add an item with a unique ID to a specific cart and update the item count."""
    # Create ItemInDB from dict
    item["item_id"] = str(uuid4())  # Generate unique item_id
    item["added_at"] = datetime.utcnow().isoformat()
    item_in_db = ItemInDB.from_mongo(item)
    
    # Convert to dict for MongoDB
    item_dict = item_in_db.to_mongo_dict()

    result = await cart_collection.update_one(
        {"email": email, "carts.cart_id": cart_id},
        {
            "$push": {"carts.$.items": item_dict},
            "$inc": {"carts.$.item_count": 1}
        }
    )

    if result.matched_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Item added successfully!", "item_id": item_in_db.item_id}

#GET items from cart
async def retrieve_cart_items(email: str, cart_id: str) -> Cart:
    """
    Retrieve all items from a specific cart for a given user.
    Returns Cart model with ItemInDB objects.
    
    Raises:
        ValueError: If cart is not found
    """
    user_data = await cart_collection.find_one(
        {"email": email, "carts.cart_id": cart_id},
        {"carts.$": 1}  # Project only the matching cart
    )

    if not user_data or "carts" not in user_data or not user_data["carts"]:
        raise ValueError("Cart not found!")

    # Convert MongoDB document to Cart model
    cart_doc = user_data["carts"][0]
    return Cart.from_mongo(cart_doc)

# PUT (Edits notes for all apereances of saem item in every car per user)
async def update_item_note(email: str, item_id: str, new_note: str) -> ItemInDB:
    """
    Update the note for all occurrences of the item across all carts of a user.
    Returns the updated item details as ItemInDB model.
    """

    # Step 1: Update the note for all occurrences of the item
    result = await cart_collection.update_many(
        {
            "email": email,
            "carts.items.item_id": item_id  # Find any cart containing the item
        },
        {
            "$set": {"carts.$[].items.$[item].notes": new_note}  # Update notes for matching items
        },
        array_filters=[{"item.item_id": item_id}]  # Match items with the given item_id
    )

    if result.modified_count == 0:
        raise ValueError("No items were updated. Item not found or no changes made.")

    # Step 2: Retrieve the updated item from any cart
    updated_item_data = await cart_collection.find_one(
        {"email": email, "carts.items.item_id": item_id},
        {"carts.items.$": 1}  # Retrieve only the first occurrence
    )

    if not updated_item_data or "carts" not in updated_item_data or not updated_item_data["carts"]:
        raise ValueError("Item was updated but not found after update.")

    # Extract the updated item details and convert to ItemInDB
    updated_item_doc = next(
        (i for c in updated_item_data["carts"] for i in c["items"] if i["item_id"] == item_id),
        None
    )

    if not updated_item_doc:
        raise ValueError("Item successfully updated but not found.")
    
    return ItemInDB.from_mongo(updated_item_doc)


#DELETE
async def delete_item(email: str, cart_id: str, item_id: str) -> Dict[str, str]:
    """
    Delete a specific item from a cart and update its selected_cart_ids.
    If the item is in other carts, remove the cart from selected_cart_ids.
    If it’s the last cart, fully remove the item.
    """
    # Step 1: Remove the item from the specific cart
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_id": cart_id},
        {
            "$pull": {"carts.$.items": {"item_id": item_id}},
            "$inc": {"carts.$.item_count": -1}
        }
    )

    # Step 2: Check if the item exists in any other carts
    user_data = await cart_collection.find_one(
        {"email": email, "carts.items.item_id": item_id},
        {"carts.items.$": 1}
    )

    if user_data:
        # Item still exists in other carts, update `selected_cart_ids`
        await cart_collection.update_many(
            {"email": email, "carts.items.item_id": item_id},
            {"$pull": {"carts.$[].items.$[item].selected_cart_ids": cart_id}},
            array_filters=[{"item.item_id": item_id}]
        )
        return {"message": f"Item removed from cart {cart_id}, updated selected_cart_ids."}
    
    return {"message": "Item fully deleted from all carts."} if result.modified_count else {"message": "Cart or item not found!"}


# ADD NEW ITEM ACROSS SELECTED CARTS
async def add_new_item_across_carts(email: str, item_details: dict, selected_cart_ids: List[str]) -> Dict[str, Any]:
    """
    Add a new item with a unique item_id across selected carts.
    Prevents adding duplicate items (same URL) that already exist in any of the user's carts.
    Returns the details of the newly added item.
    """

    # Step 1: Check if the item (by URL) already exists in any of the user's carts
    existing_item = await cart_collection.find_one(
        {"email": email, "carts.items.url": item_details["url"]},
        {"carts.cart_id": 1, "carts.cart_name": 1, "carts.items.$": 1}
    )

    if existing_item and "carts" in existing_item:
        existing_cart = next(
            (cart for cart in existing_item["carts"] if any(i["url"] == item_details["url"] for i in cart["items"])),
            None
        )

        if existing_cart:
            existing_item_doc = next(i for i in existing_cart["items"] if i["url"] == item_details["url"])
            return {
                "message": f"Item already exists in '{existing_cart['cart_name']}'. Move it instead.",
                "existing_item": ItemInDB.from_mongo(existing_item_doc)
            }

    # Step 2: Generate a new unique item ID and create ItemInDB
    item_details["item_id"] = str(uuid4())  
    item_details["added_at"] = datetime.utcnow().isoformat()
    item_details["selected_cart_ids"] = selected_cart_ids  # Store selected carts in the item itself
    item_in_db = ItemInDB.from_mongo(item_details)

    # Step 3: Add the item to each selected cart
    item_dict = item_in_db.to_mongo_dict()
    for cart_id in selected_cart_ids:
        item_copy = item_dict.copy()
        await cart_collection.update_one(
            {"email": email, "carts.cart_id": cart_id},
            {
                "$push": {"carts.$.items": item_copy},
                "$inc": {"carts.$.item_count": 1}
            }
        )

    # Step 4: Return the newly added item details
    return {
        "message": "New item added successfully across selected carts.",
        "item": item_in_db
    }

# MODIFY EXISTING ITEM ACROSS CARTS
async def modify_existing_item_across_carts(email: str, item_id: str, selected_cart_ids: List[str]) -> ItemInDB:
    """
    Move an existing item across selected carts.
    - Ensures the item is **added** to selected carts if not already there.
    - Ensures the item is **removed** from deselected carts.
    - Updates the `selected_cart_ids` attribute correctly in all carts.
    - Returns the updated item as ItemInDB.
    """

    # Step 1: Retrieve all carts for this user
    user_data = await cart_collection.find_one(
        {"email": email},
        {"carts.cart_id": 1, "carts.items": 1}  # Fetch only cart IDs and items
    )

    if not user_data or "carts" not in user_data:
        raise ValueError("No carts found for this user.")

    # Step 2: Identify where the item currently exists & Extract item details
    current_cart_ids = set()
    item_doc = None  # Placeholder for item data

    for cart in user_data["carts"]:
        for cart_item in cart["items"]:
            if cart_item["item_id"] == item_id:
                current_cart_ids.add(cart["cart_id"])
                if item_doc is None:  # Store the first found instance of the item
                    item_doc = cart_item

    if not item_doc:
        raise ValueError("Item not found!")

    # Convert to ItemInDB for easier manipulation
    item_in_db = ItemInDB.from_mongo(item_doc)

    # Step 3: Identify which carts need removal and addition
    remove_from_cart_ids = list(current_cart_ids - set(selected_cart_ids))  # Carts where item needs to be removed
    add_to_cart_ids = list(set(selected_cart_ids) - current_cart_ids)  # Carts where item needs to be added

    # Step 4: Remove the item from deselected carts
    if remove_from_cart_ids:
        await cart_collection.update_many(
            {"email": email, "carts.cart_id": {"$in": remove_from_cart_ids}},
            {
                "$pull": {"carts.$.items": {"item_id": item_id}},  # Remove the item
                "$inc": {"carts.$.item_count": -1}  # Decrement the item count
            }
        )

    # Step 5: Add the item to selected carts **(even if they are not empty)**
    if add_to_cart_ids:
        item_dict = item_in_db.to_mongo_dict()
        for cart_id in add_to_cart_ids:
            item_copy = item_dict.copy()
            # Keep the original timestamp (don't update added_at)

            await cart_collection.update_one(
                {"email": email, "carts.cart_id": cart_id},
                {
                    "$push": {"carts.$.items": item_copy},  # Ensure item is added to all selected carts
                    "$inc": {"carts.$.item_count": 1}
                }
            )

    # Step 6: Ensure `selected_cart_ids` is correctly updated in **all occurrences** of the item
    updated_cart_ids = list(set(selected_cart_ids))  # Remove duplicates
    await cart_collection.update_many(
        {"email": email, "carts.items.item_id": item_id},
        {
            "$set": {"carts.$[].items.$[item].selected_cart_ids": updated_cart_ids}
        },
        array_filters=[{"item.item_id": item_id}]
    )

    # Step 7: Retrieve the updated item from any cart
    updated_item_data = await cart_collection.find_one(
        {"email": email, "carts.items.item_id": item_id},
        {"carts.items.$": 1}
    )

    if not updated_item_data or "carts" not in updated_item_data or not updated_item_data["carts"]:
        raise ValueError("Item was moved but not found after update.")

    updated_item_doc = next(
        (i for c in updated_item_data["carts"] for i in c["items"] if i["item_id"] == item_id),
        None
    )

    if not updated_item_doc:
        raise ValueError("Item successfully moved but not found.")
    
    return ItemInDB.from_mongo(updated_item_doc)

#Nuclear delete
async def nuke(email: str, item_id: str) -> Dict[str, str]:
    """
    Deletes an item from all carts for a given user.
    """
    # Use update_many to remove the item from all carts that contain it
    # We need to update each cart individually since we need to decrement item_count per cart
    user_data = await cart_collection.find_one(
        {"email": email, "carts.items.item_id": item_id}
    )
    
    if not user_data or "carts" not in user_data:
        return {"message": "Item not found in any cart!"}
    
    # Count how many carts will be affected
    carts_with_item = [
        cart for cart in user_data["carts"] 
        if any(item.get("item_id") == item_id for item in cart.get("items", []))
    ]
    
    if not carts_with_item:
        return {"message": "Item not found in any cart!"}
    
    # Remove item from each cart
    modified_count = 0
    for cart in carts_with_item:
        result = await cart_collection.update_one(
            {"email": email, "carts.cart_id": cart["cart_id"]},
            {
                "$pull": {"carts.$.items": {"item_id": item_id}},
                "$inc": {"carts.$.item_count": -1}
            }
        )
        if result.modified_count > 0:
            modified_count += 1
    
    return {"message": f"Item successfully deleted from {modified_count} cart(s)."}
