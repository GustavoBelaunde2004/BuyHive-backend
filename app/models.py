from .database import cart_collection

async def add_user_by_email(email: str, name: str = "Unknown"):
    """Add a new user to the database or ensure they already exist."""
    # Check if the user already exists
    existing_user = await cart_collection.find_one({"email": email})
    if existing_user:
        return {"message": "User already exists!"}

    # Add a new user if not found
    new_user = {
        "email": email,
        "name": name,
    }
    await cart_collection.insert_one(new_user)
    return {"message": "User added successfully!"}


async def save_cart(email: str, cart_name: str, items: list):
    """Save a new cart for a user, avoiding duplicate cart names."""
    # Check if the cart already exists
    existing_cart = await cart_collection.find_one(
        {"email": email, "carts.cart_name": cart_name}
    )
    if existing_cart:
        return {"message": "Cart already exists!"}

    # Add the new cart
    result = await cart_collection.update_one(
        {"email": email},
        {"$push": {"carts": {"cart_name": cart_name, "items": items}}},
        upsert=True
    )

    # Return a JSON-friendly response
    if result.upserted_id:
        return {"message": "Cart created successfully!", "upserted_id": str(result.upserted_id)}
    elif result.modified_count > 0:
        return {"message": "Cart updated successfully!"}
    else:
        return {"message": "No changes made to the cart."}


async def get_carts(email: str):
    """Retrieve all carts for a user."""
    user_data = await cart_collection.find_one({"email": email})
    return user_data.get("carts", []) if user_data else []


async def update_cart(email: str, cart_name: str, items: list):
    """Update items in an existing cart."""
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_name": cart_name},
        {"$set": {"carts.$.items": items}}
    )
    if result.matched_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Cart updated successfully!"}


async def delete_cart(email: str, cart_name: str):
    """Delete a specific cart for a user."""
    result = await cart_collection.update_one(
        {"email": email},
        {"$pull": {"carts": {"cart_name": cart_name}}}
    )
    if result.modified_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Cart deleted successfully!"}


async def add_item_to_cart(email: str, cart_name: str, item: dict):
    """Add an item to a specific cart."""
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_name": cart_name},
        {"$push": {"carts.$.items": item}}
    )
    if result.matched_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Item added successfully!"}


async def delete_item(email: str, cart_name: str, item_name: str):
    """Delete a specific item from a cart."""
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_name": cart_name},
        {"$pull": {"carts.$.items": {"name": item_name}}}
    )
    if result.modified_count == 0:
        return {"message": "Cart or item not found!"}
    return {"message": "Item deleted successfully!"}
