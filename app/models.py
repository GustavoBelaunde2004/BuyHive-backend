from datetime import datetime
from uuid import uuid4  # For generating unique IDs
from .database import cart_collection

# USER FUNCTIONS --------------------------------------------------------------------------------------------------------------
async def add_user_by_email(email: str, name: str = "Unknown"):
    """Add a new user to the database or ensure they already exist."""
    existing_user = await cart_collection.find_one({"email": email})
    if existing_user:
        return {"message": "User already exists!"}

    new_user = {
        "email": email,
        "name": name,
        "cart_count": 0,
        "carts": []
    }
    await cart_collection.insert_one(new_user)
    return {"message": "User added successfully!"}

# CART FUNCTIONS --------------------------------------------------------------------------------------------------------------
# POST
async def save_cart(email: str, cart_name: str):
    """Add a new cart with a unique ID for a user and update the cart count."""
    existing_cart = await cart_collection.find_one({"email": email, "carts.cart_name": cart_name})
    if existing_cart:
        return {"message": "Cart already exists!"}

    cart_id = str(uuid4())  # Generate unique cart_id
    result = await cart_collection.update_one(
        {"email": email},
        {
            "$push": {
                "carts": {
                    "cart_id": cart_id,
                    "cart_name": cart_name,
                    "item_count": 0,
                    "created_at": datetime.utcnow().isoformat(),
                    "items": []
                }
            },
            "$inc": {"cart_count": 1}
        },
        upsert=True
    )

    if result.upserted_id:
        return {"message": "Cart created successfully!", "cart_id": cart_id, "cart_name": cart_name}
    elif result.modified_count > 0:
        return {"message": "Cart added successfully!", "cart_id": cart_id, "cart_name": cart_name}
    else:
        return {"message": "No changes made."}

# PUT
async def update_cart_name(email: str, cart_id: str, new_name: str):

    """Update the name of a specific cart."""
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_id": cart_id},
        {"$set": {"carts.$.cart_name": new_name}}
    )

    if result.matched_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Cart name updated successfully!"}

# GET
async def get_carts(email: str):
    """Retrieve all carts for a user."""
    user_data = await cart_collection.find_one({"email": email})
    return user_data.get("carts", []) if user_data else []

# DELETE
async def delete_cart(email: str, cart_id: str):
    """Delete a specific cart and update the cart count."""
    result = await cart_collection.update_one(
        {"email": email},
        {
            "$pull": {"carts": {"cart_id": cart_id}},
            "$inc": {"cart_count": -1}
        }
    )
    if result.modified_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Cart deleted successfully!"}

# ITEM FUNCTIONS --------------------------------------------------------------------------------------------------------------
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

# PUT (EDIT ALL ITEMS)
async def update_cart_items(email: str, cart_id: str, items: list):
    """Update all items in a specific cart."""
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_id": cart_id},
        {"$set": {"carts.$.items": items}}
    )

    if result.matched_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Cart items updated successfully!"}

# PUT (EDIT NOTE)
async def update_item_note(email: str, cart_id: str, item_id: str, new_note: str):
    """Update the note of a specific item in a cart."""
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_id": cart_id, "carts.items.item_id": item_id},
        {"$set": {"carts.$.items.$[item].notes": new_note}},
        array_filters=[{"item.item_id": item_id}]
    )

    if result.matched_count == 0:
        return {"message": "Item not found!"}
    return {"message": "Item note updated successfully!"}

# DELETE
async def delete_item(email: str, cart_id: str, item_id: str):
    """Delete a specific item from a cart and update the item count."""
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_id": cart_id},
        {
            "$pull": {"carts.$.items": {"item_id": item_id}},
            "$inc": {"carts.$.item_count": -1}
        }
    )
    if result.modified_count == 0:
        return {"message": "Cart or item not found!"}
    return {"message": "Item deleted successfully!"}


#TEST---------------------------------------------------------------------------------------------------------------------------------------------





async def move_item(email: str, source_cart: str, destination_cart: str, item_name: str):
    """Move an item from one cart to another."""
    # Step 1: Find the item in the source cart and remove it
    result = await cart_collection.find_one_and_update(
        {"email": email, "carts.cart_name": source_cart},
        {"$pull": {"carts.$.items": {"name": item_name}}},
        return_document=True
    )
    
    if not result:
        return {"message": "Source cart or item not found!"}

    # Extract the item that was removed
    item = next((i for c in result["carts"] if c["cart_name"] == source_cart for i in c["items"] if i["name"] == item_name), None)

    if not item:
        return {"message": "Item not found in source cart!"}

    # Step 2: Add the item to the destination cart
    await cart_collection.update_one(
        {"email": email, "carts.cart_name": destination_cart},
        {"$push": {"carts.$.items": item}}
    )

    return {"message": "Item moved successfully!"}



async def duplicate_item_to_cart(email: str, source_cart: str, destination_cart: str, item_name: str):
    """Duplicate an item from one cart to another."""
    # Find the source cart and the item
    user_data = await cart_collection.find_one({"email": email, "carts.cart_name": source_cart})
    if not user_data:
        return {"message": "Source cart not found!"}

    # Find the item in the source cart
    source_cart_data = next((c for c in user_data["carts"] if c["cart_name"] == source_cart), None)
    item = next((i for i in source_cart_data["items"] if i["name"] == item_name), None)

    if not item:
        return {"message": "Item not found in source cart!"}

    # Add the item to the destination cart
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_name": destination_cart},
        {"$push": {"carts.$.items": item}}
    )

    if result.matched_count == 0:
        return {"message": "Destination cart not found!"}

    return {"message": "Item duplicated successfully!"}




