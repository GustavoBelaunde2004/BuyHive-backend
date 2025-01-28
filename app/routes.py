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
    move_item,
    duplicate_item_to_cart
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

router = APIRouter()

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
@router.put("/carts/{email}/{cart_id}/items/{item_id}/edit-note")
async def edit_item_note(email: str, cart_id: str, item_id: str, payload: EditNoteRequest):
    """Edit the note of a specific item in a cart."""
    try:
        # Call the model function to update the note
        response = await update_item_note(email, cart_id, item_id, payload.new_note)
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




@router.put("/carts/{email}/move-item")
async def move_item_between_carts(email: str, source_cart: str, destination_cart: str, item_name: str):
    """Move an item from one cart to another."""
    try:
        response = await move_item(email, source_cart, destination_cart, item_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.put("/carts/{email}/duplicate-item")
async def duplicate_item(email: str, source_cart: str, destination_cart: str, item_name: str):
    """Duplicate an item from one cart to another."""
    try:
        response = await duplicate_item_to_cart(email, source_cart, destination_cart, item_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


""""
@router.post("/carts/{email}/add-item-to-multiple")
async def add_item_to_multiple_carts(email: str, cart_names: List[str], payload: Item):
    """ """Add an item to multiple carts.""" """
    try:
        response = await add_item_to_carts(email, cart_names, payload)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""