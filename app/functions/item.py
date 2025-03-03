from datetime import datetime
from uuid import uuid4
from .database import cart_collection

# POST
async def add_item_to_cart(email: str, cart_id: str, item: dict):
    """Add an item with a unique ID to a specific cart and update the item count."""
    item["item_id"] = str(uuid4())  # Generate unique item_id
    item["added_at"] = datetime.utcnow().isoformat()

    result = await cart_collection.update_one(
        {"email": email, "carts.cart_id": cart_id},
        {
            "$push": {"carts.$.items": item},
            "$inc": {"carts.$.item_count": 1}
        }
    )

    if result.matched_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Item added successfully!", "item_id": item["item_id"]}

#GET items from cart
async def retrieve_cart_items(email: str, cart_id: str):
    """
    Retrieve all items from a specific cart for a given user.
    """
    user_data = await cart_collection.find_one(
        {"email": email, "carts.cart_id": cart_id},
        {"carts.$": 1}  # Project only the matching cart
    )

    if not user_data or "carts" not in user_data or not user_data["carts"]:
        return {"message": "Cart not found!"}

    # Extract the cart items
    cart = user_data["carts"][0]
    return {"cart_id": cart["cart_id"], "cart_name": cart["cart_name"], "items": cart["items"]}

# PUT (Edits notes for all apereances of saem item in every car per user)
async def update_item_note(email: str, item_id: str, new_note: str):
    """
    Update the note for all occurrences of the item across all carts of a user.
    Returns the updated item details.
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
        return {"message": "No items were updated. Item not found or no changes made."}

    # Step 2: Retrieve the updated item from any cart
    updated_item_data = await cart_collection.find_one(
        {"email": email, "carts.items.item_id": item_id},
        {"carts.items.$": 1}  # Retrieve only the first occurrence
    )

    if not updated_item_data or "carts" not in updated_item_data or not updated_item_data["carts"]:
        return {"message": "Item was updated but not found after update."}

    # Extract the updated item details
    updated_item = next(
        (i for c in updated_item_data["carts"] for i in c["items"] if i["item_id"] == item_id),
        None
    )

    return updated_item if updated_item else {"message": "Item successfully updated but not found."}


#DELETE
async def delete_item(email: str, cart_id: str, item_id: str):
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
async def add_new_item_across_carts(email: str, item_details: dict, selected_cart_ids: list):
    """
    Add a new item with a unique item_id across selected carts.
    Prevents adding duplicate items (same URL) that already exist in any of the user's carts.
    """

    # Step 1: Check if the item (by URL) already exists in any of the user's carts
    existing_item = await cart_collection.find_one(
        {"email": email, "carts.items.url": item_details["url"]},
        {"carts.cart_id": 1, "carts.cart_name": 1, "carts.items.$": 1}
    )

    if existing_item and "carts" in existing_item:
        # Find the cart where the item already exists
        existing_cart = next(
            (cart for cart in existing_item["carts"] if any(i["url"] == item_details["url"] for i in cart["items"])),
            None
        )

        if existing_cart:
            return {
                "message": f"Item already exists in '{existing_cart['cart_name']}'. Move it instead."
            }

    # Step 2: Generate a new unique item ID
    item_details["item_id"] = str(uuid4())  
    item_details["added_at"] = datetime.utcnow().isoformat()

    # Step 3: Add the item to each selected cart
    for cart_id in selected_cart_ids:
        item_copy = item_details.copy()
        await cart_collection.update_one(
            {"email": email, "carts.cart_id": cart_id},
            {
                "$push": {"carts.$.items": item_copy},
                "$inc": {"carts.$.item_count": 1}
            }
        )

    return {"message": "New item added successfully across selected carts."}

# MODIFY EXISTING ITEM ACROSS CARTS
async def modify_existing_item_across_carts(email: str, item_id: str, selected_cart_ids: list):
    """
    Move an existing item across selected carts.
    - Ensures the item is **added** to selected carts if not already there.
    - Ensures the item is **removed** from deselected carts.
    - Updates the `selected_cart_ids` attribute correctly in all carts.
    - Returns the updated item.
    """

    # Step 1: Retrieve all carts for this user
    user_data = await cart_collection.find_one(
        {"email": email},
        {"carts.cart_id": 1, "carts.items": 1}  # Fetch only cart IDs and items
    )

    if not user_data or "carts" not in user_data:
        return {"message": "No carts found for this user."}

    # Step 2: Identify where the item currently exists & Extract item details
    current_cart_ids = set()
    item = None  # Placeholder for item data

    for cart in user_data["carts"]:
        for cart_item in cart["items"]:
            if cart_item["item_id"] == item_id:
                current_cart_ids.add(cart["cart_id"])
                if item is None:  # Store the first found instance of the item
                    item = cart_item

    if not item:
        return {"message": "Item not found!"}

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
        for cart_id in add_to_cart_ids:
            item_copy = item.copy()
            item_copy.pop("added_at", None)  # Keep the original timestamp

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
        return {"message": "Item was moved but not found after update."}

    updated_item = next(
        (i for c in updated_item_data["carts"] for i in c["items"] if i["item_id"] == item_id),
        None
    )

    return updated_item if updated_item else {"message": "Item successfully moved but not found."}