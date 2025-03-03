from datetime import datetime
from uuid import uuid4
from .database import cart_collection

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
        return {"message": "Cart created successfully!", "cart_id": cart_id}
    elif result.modified_count > 0:
        return {"message": "Cart added successfully!", "cart_id": cart_id}
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

