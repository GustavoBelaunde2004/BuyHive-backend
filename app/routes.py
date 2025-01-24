from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from app.models import (
    save_cart,
    get_carts,
    update_cart,
    delete_cart,
    add_item_to_cart,
    delete_item,
    add_user_by_email,
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

router = APIRouter()


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


@router.post("/carts/{email}")
async def add_cart(email: str, payload: AddCartRequest):
    """Add a new cart for a user."""
    try:
        response = await save_cart(email, payload.cart_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/carts/{email}")
async def retrieve_carts(email: str):
    """Get all carts for a user."""
    try:
        carts = await get_carts(email)
        return {"carts": carts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/carts/{email}/{cart_name}")
async def modify_cart(email: str, cart_name: str, payload: ModifyCartRequest):
    """Update items in an existing cart."""
    try:
        # Convert Pydantic models to dictionaries
        items_as_dict = [item.dict() for item in payload.items]

        response = await update_cart(email, cart_name, items_as_dict)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/carts/{email}/{cart_name}")
async def remove_cart(email: str, cart_name: str):
    """Delete a specific cart for a user."""
    try:
        response = await delete_cart(email, cart_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/carts/{email}/{cart_name}/items")
async def add_item(email: str, cart_name: str, payload: Item):
    """Add an item to a specific cart."""
    try:
        # Convert the Pydantic model to a dictionary
        item_as_dict = payload.dict()

        response = await add_item_to_cart(email, cart_name, item_as_dict)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/carts/{email}/{cart_name}/items/{item_name}")
async def remove_item(email: str, cart_name: str, item_name: str):
    """Delete a specific item from a cart."""
    try:
        response = await delete_item(email, cart_name, item_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
