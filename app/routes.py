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
    update_item_note
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

router = APIRouter()

#USER ROUTES--------------------------------------------------------------------------------------------------------------
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

#CART ROUTES--------------------------------------------------------------------------------------------------------------
@router.post("/carts/{email}")
async def add_cart(email: str, payload: AddCartRequest):
    """Add a new cart for a user."""
    try:
        response = await save_cart(email, payload.cart_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#EDIT CART NAME ROUTE
@router.put("/carts/{email}/{cart_name}/edit-name")
async def edit_cart_name(email: str, cart_name: str, payload: EditCartNameRequest):
    """Edit the name of a specific cart."""
    try:
        response = await update_cart_name(email, cart_name, payload.new_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#RETRIEVE CART NAMES
@router.get("/carts/{email}")
async def retrieve_carts(email: str):
    """Get all carts for a user."""
    try:
        carts = await get_carts(email)
        return {"carts": carts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#DELETE
@router.delete("/carts/{email}/{cart_name}")
async def remove_cart(email: str, cart_name: str):
    """Delete a specific cart for a user."""
    try:
        response = await delete_cart(email, cart_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#ITEMS FUNCTIOS--------------------------------------------------------------------------------------------------------------
@router.post("/carts/{email}/{cart_name}/items")
async def add_item(email: str, cart_name: str, payload: Item):
    """Add an item to a specific cart."""
    try:
        # Convert Pydantic model to a plain dictionary and ensure HttpUrl is serialized to string
        item_as_dict = payload.model_dump()
        if item_as_dict.get("image"):
            item_as_dict["image"] = str(item_as_dict["image"])
        if item_as_dict.get("url"):
            item_as_dict["url"] = str(item_as_dict["url"])

        # Pass the converted dictionary to the model function
        response = await add_item_to_cart(email, cart_name, item_as_dict)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#EDITS ITEMS NAME
@router.put("/carts/{email}/{cart_name}/edit-items")
async def edit_cart_items(email: str, cart_name: str, payload: ModifyCartRequest):
    """Edit the items of a specific cart."""
    try:
        # Convert Pydantic models to dictionaries
        items_as_dict = [item.dict() for item in payload.items]

        response = await update_cart_items(email, cart_name, items_as_dict)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#EDITS ITEMS NOTES
@router.put("/carts/{email}/{cart_name}/items/{item_name}/edit-note")
async def edit_item_note(email: str, cart_name: str, item_name: str, payload: EditNoteRequest):
    """Edit the note of a specific item in a cart."""
    try:
        # Call the model function to update the note
        response = await update_item_note(email, cart_name, item_name, payload.new_note)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#DELETE
@router.delete("/carts/{email}/{cart_name}/items/{item_name}")
async def remove_item(email: str, cart_name: str, item_name: str):
    """Delete a specific item from a cart."""
    try:
        response = await delete_item(email, cart_name, item_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
