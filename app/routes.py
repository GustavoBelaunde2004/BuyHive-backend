from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from app.models import (
    save_cart,
    get_carts,
    delete_cart,
    add_item_to_cart,
    delete_item,
    add_user_by_email,
    update_cart_name,
    update_cart_items,
    update_item_note,
    send_cart_email,
    add_new_item_across_carts,
    modify_existing_item_across_carts
)

# Define the expected structure of the request body
class Item(BaseModel):
    name: str
    price: float
    image: Optional[HttpUrl]  # Optional URL for the product image
    url: Optional[HttpUrl]    # Optional URL for the product
    notes: Optional[str]      # Optional notes about the item

class AddCartRequest(BaseModel):
    cart_name: str  # The name of the new cart

class ModifyCartRequest(BaseModel):
    items: List[Item]  # List of items for modifying a cart

class EditCartNameRequest(BaseModel):
    new_name: str

class EditNoteRequest(BaseModel):
    new_note: str

#TEST
class CreateCartWithItemRequest(BaseModel):
    cart_name: str
    item: Item


# Request body for adding a new item
class AddNewItemRequest(BaseModel):
    name: str
    price: float
    image: Optional[HttpUrl]  # Optional URL for the product image
    url: Optional[HttpUrl]    # Optional URL for the product
    notes: Optional[str]      # Optional notes about the item
    selected_cart_ids: List[str]  # Carts to add the new item to

# Request body for modifying an existing item
class ModifyItemAcrossCartsRequest(BaseModel):
    add_to_cart_ids: List[str]
    remove_from_cart_ids: List[str]

router = APIRouter()

@router.post("/carts/{email}/share")
async def share_cart(email: str, cart_id: str, recipient_email: str):
    """Share a cart by sending its details to the recipient via email."""
    try:
        # Retrieve user's carts
        user_carts = await get_carts(email)

        # Find the cart to share
        cart_to_share = next((cart for cart in user_carts if cart["cart_id"] == cart_id), None)
        if not cart_to_share:
            raise HTTPException(status_code=404, detail="Cart not found")

        cart_name = cart_to_share["cart_name"]
        cart_items = cart_to_share["items"]

        # Call the email utility
        sender_email = "your_verified_ses_email@example.com"
        result = await send_cart_email(sender_email, recipient_email, cart_name, cart_items)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# USER ROUTES--------------------------------------------------------------------------------------------------------------
@router.post("/users/add")
async def add_user(payload: dict):
    """
    Add a new user to the database or update their info.
    Expects a JSON payload with 'email' (required) and optional 'name'.
    """
    email = payload.get("email")
    name = payload.get("name", "Unknown")  # Default name if not provided

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    try:
        response = await add_user_by_email(email, name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# CART ROUTES--------------------------------------------------------------------------------------------------------------
@router.post("/carts/{email}")
async def add_cart(email: str, payload: AddCartRequest):
    """Add a new cart for a user."""
    try:
        response = await save_cart(email, payload.cart_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# EDIT CART NAME ROUTE
@router.put("/carts/{email}/{cart_id}/edit-name")
async def edit_cart_name(email: str, cart_id: str, payload: EditCartNameRequest):
    """Edit the name of a specific cart."""
    try:
        response = await update_cart_name(email, cart_id, payload.new_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# RETRIEVE CART NAMES
@router.get("/carts/{email}")
async def retrieve_carts(email: str):
    """Get all carts for a user."""
    try:
        carts = await get_carts(email)
        return {"carts": carts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE
@router.delete("/carts/{email}/{cart_id}")
async def remove_cart(email: str, cart_id: str):
    """Delete a specific cart for a user."""
    try:
        response = await delete_cart(email, cart_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ITEMS FUNCTIONS--------------------------------------------------------------------------------------------------------------
@router.post("/carts/{email}/{cart_id}/items")
async def add_item(email: str, cart_id: str, payload: Item):
    """Add an item to a specific cart."""
    try:
        # Convert Pydantic model to a plain dictionary and ensure HttpUrl is serialized to string
        item_as_dict = payload.model_dump()
        if item_as_dict.get("image"):
            item_as_dict["image"] = str(item_as_dict["image"])
        if item_as_dict.get("url"):
            item_as_dict["url"] = str(item_as_dict["url"])

        # Pass the converted dictionary to the model function
        response = await add_item_to_cart(email, cart_id, item_as_dict)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# EDIT ITEMS
@router.put("/carts/{email}/{cart_id}/edit-items")
async def edit_cart_items(email: str, cart_id: str, payload: ModifyCartRequest):
    """Edit the items of a specific cart."""
    try:
        # Convert Pydantic models to dictionaries
        items_as_dict = [item.dict() for item in payload.items]

        response = await update_cart_items(email, cart_id, items_as_dict)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# EDIT ITEMS NOTES
@router.put("/carts/{email}/items/{item_id}/edit-note")
async def edit_item_note(email: str, item_id: str, payload: EditNoteRequest):
    """
    Edit the note for all occurrences of the item across all carts.
    """
    try:
        response = await update_item_note(email, item_id, payload.new_note)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE
@router.delete("/carts/{email}/{cart_id}/items/{item_id}")
async def remove_item(email: str, cart_id: str, item_id: str):
    """Delete a specific item from a cart."""
    try:
        response = await delete_item(email, cart_id, item_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#TEST---------------------------------------------------------------------------------------------------------------------------------------------

@router.post("/carts/{email}/create-with-item")
async def create_cart_with_item(email: str, payload: CreateCartWithItemRequest):
    """Create a new cart and add an item to it."""
    try:
        # Convert item to dictionary
        item_as_dict = payload.item.model_dump()
        # Add timestamp to the item
        item_as_dict["added_at"] = datetime.utcnow().isoformat()

        # Create the cart and add the item
        response = await save_cart(email, payload.cart_name, [item_as_dict])
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# ROUTE: Add new item across selected carts
@router.post("/carts/{email}/items/add-new")
async def add_new_item(email: str, payload: AddNewItemRequest):
    """
    Add a new item across selected carts with a unique item_id.
    """
    try:
        # Convert Pydantic object to a plain dictionary with URLs converted to strings
        item_details = payload.dict()
        if item_details.get("image"):
            item_details["image"] = str(item_details["image"])
        if item_details.get("url"):
            item_details["url"] = str(item_details["url"])

        response = await add_new_item_across_carts(email, item_details, payload.selected_cart_ids)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ROUTE: Modify existing item across selected carts
@router.put("/carts/{email}/items/{item_id}/modify")
async def modify_existing_item(email: str, item_id: str, payload: ModifyItemAcrossCartsRequest):
    """
    Modify an existing item's presence across selected/deselected carts.
    """
    try:
        response = await modify_existing_item_across_carts(
            email,
            item_id,
            payload.add_to_cart_ids,
            payload.remove_from_cart_ids
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))