from datetime import datetime
from uuid import uuid4
from typing import List
from .database import users_collection, carts_collection, items_collection
from app.models.cart import Cart

# POST
async def save_cart(user_id: str, cart_name: str) -> dict:
    """Add a new cart with a unique ID for a user and update the cart count."""
    cart_id = str(uuid4())  # Generate unique cart_id
    now = datetime.utcnow().isoformat()

    # Ensure user exists
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        raise ValueError("User not found!")

    # Create cart document (items stored as item_ids)
    cart_doc = {
        "cart_id": cart_id,
        "user_id": user_id,
        "cart_name": cart_name,
        "item_count": 0,
        "created_at": now,
        "item_ids": [],
    }
    await carts_collection.insert_one(cart_doc)

    # Add cart_id to user
    await users_collection.update_one(
        {"user_id": user_id},
        {
            "$push": {"cart_ids": cart_id},
            "$inc": {"cart_count": 1},
            "$set": {"updated_at": now},
        },
    )

    return {"message": "Cart created successfully!", "cart_id": cart_id}

# PUT
async def update_cart_name(user_id: str, cart_id: str, new_name: str) -> dict:
    """Update the name of a specific cart."""
    result = await carts_collection.update_one(
        {"user_id": user_id, "cart_id": cart_id},
        {"$set": {"cart_name": new_name}}
    )

    if result.matched_count == 0:
        return {"message": "Cart not found!"}
    return {"message": "Cart name updated successfully!"}

# GET
async def get_carts(user_id: str) -> List[Cart]:
    """Retrieve all carts for a user."""
    cart_docs = await carts_collection.find({"user_id": user_id}).to_list(length=None)
    carts: List[Cart] = []

    for cart_doc in cart_docs:
        item_ids = cart_doc.get("item_ids", [])
        items = []
        if item_ids:
            item_docs = await items_collection.find(
                {"user_id": user_id, "item_id": {"$in": item_ids}}
            ).to_list(length=None)
            # Preserve cart order if possible
            doc_by_id = {d.get("item_id"): d for d in item_docs}
            for iid in item_ids:
                if iid in doc_by_id:
                    items.append(doc_by_id[iid])

        carts.append(
            Cart(
                cart_id=cart_doc["cart_id"],
                cart_name=cart_doc["cart_name"],
                item_count=cart_doc.get("item_count", 0),
                created_at=cart_doc.get("created_at", datetime.utcnow().isoformat()),
                items=items,
            )
        )

    return carts

# DELETE
async def delete_cart(user_id: str, cart_id: str) -> dict:
    """Delete a specific cart and update the cart count."""
    now = datetime.utcnow().isoformat()

    cart_doc = await carts_collection.find_one({"user_id": user_id, "cart_id": cart_id})
    if not cart_doc:
        return {"message": "Cart not found!"}

    item_ids = cart_doc.get("item_ids", [])

    # Delete cart
    await carts_collection.delete_one({"user_id": user_id, "cart_id": cart_id})

    # Remove cart from user
    await users_collection.update_one(
        {"user_id": user_id},
        {
            "$pull": {"cart_ids": cart_id},
            "$inc": {"cart_count": -1},
            "$set": {"updated_at": now},
        },
    )

    # Remove cart_id from items.selected_cart_ids, and delete orphan items
    if item_ids:
        for item_id in item_ids:
            await items_collection.update_one(
                {"user_id": user_id, "item_id": item_id},
                {"$pull": {"selected_cart_ids": cart_id}},
            )
            updated_item = await items_collection.find_one({"user_id": user_id, "item_id": item_id})
            if updated_item and not (updated_item.get("selected_cart_ids") or []):
                await items_collection.delete_one({"user_id": user_id, "item_id": item_id})

    return {"message": "Cart deleted successfully!"}

