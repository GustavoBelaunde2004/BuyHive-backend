from datetime import datetime
from .database import cart_collection


#USER FUNCTIOS--------------------------------------------------------------------------------------------------------------
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

#CART FUNCTIOS--------------------------------------------------------------------------------------------------------------
#POST
async def save_cart(email: str, cart_name: str):
    """Add a new cart for a user and update the cart count."""
    existing_cart = await cart_collection.find_one({"email": email, "carts.cart_name": cart_name})
    if existing_cart:
        return {"message": "Cart already exists!"}

    # Add a new cart with a timestamp
    result = await cart_collection.update_one(
        {"email": email},
        {
            "$push": {
                "carts": {
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
        return {"message": "Cart created successfully!", "upserted_id": str(result.upserted_id)}
    elif result.modified_count > 0:
        return {"message": "Cart added successfully!"}
    else:
        return {"message": "No changes made."}
#PUT
async def update_cart_name(email: str, cart_name: str, new_name: str):
    """Update the name of a specific cart."""
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_name": cart_name},
        {"$set": {"carts.$.cart_name": new_name}}
    )

    if result.matched_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Cart name updated successfully!"}
#GET
async def get_carts(email: str):
    """Retrieve all carts for a user."""
    user_data = await cart_collection.find_one({"email": email})
    return user_data.get("carts", []) if user_data else []
#DELETE
async def delete_cart(email: str, cart_name: str):
    """Delete a specific cart and update the cart count."""
    result = await cart_collection.update_one(
        {"email": email},
        {
            "$pull": {"carts": {"cart_name": cart_name}},
            "$inc": {"cart_count": -1}
        }
    )
    if result.modified_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Cart deleted successfully!"}

#ITEM FUNCTIOS--------------------------------------------------------------------------------------------------------------
#POST
async def add_item_to_cart(email: str, cart_name: str, item: dict):
    """Add an item to a specific cart and update the item count."""
    # Add a timestamp to the item
    item["added_at"] = datetime.utcnow().isoformat()

    result = await cart_collection.update_one(
        {"email": email, "carts.cart_name": cart_name},
        {
            "$push": {"carts.$.items": item},
            "$inc": {"carts.$.item_count": 1}
        }
    )

    if result.matched_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Item added successfully!"}
#PUT/NAME
async def update_cart_items(email: str, cart_name: str, items: list):
    """Update items in a specific cart."""
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_name": cart_name},
        {"$set": {"carts.$.items": items}}
    )

    if result.matched_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Cart items updated successfully!"}
#PUT/NOTES
async def update_item_note(email: str, cart_name: str, item_name: str, new_note: str):
    """Update the note of a specific item in a cart."""
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_name": cart_name, "carts.items.name": item_name},
        {"$set": {"carts.$.items.$[item].notes": new_note}},
        array_filters=[{"item.name": item_name}]
    )

    if result.matched_count == 0:
        return {"message": "Item not found!"}
    return {"message": "Item note updated successfully!"}
#DELETE
async def delete_item(email: str, cart_name: str, item_name: str):
    """Delete a specific item from a cart and update the item count."""
    result = await cart_collection.update_one(
        {"email": email, "carts.cart_name": cart_name},
        {
            "$pull": {"carts.$.items": {"name": item_name}},
            "$inc": {"carts.$.item_count": -1}
        }
    )
    if result.modified_count == 0:
        return {"message": "Cart or item not found!"}
    return {"message": "Item deleted successfully!"}
