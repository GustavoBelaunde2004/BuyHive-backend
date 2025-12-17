from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from app.functions.base import AddCartRequest, EditCartNameRequest
from app.functions.cart import save_cart, get_carts, delete_cart, update_cart_name
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.cart import Cart
from app.utils.rate_limiter import rate_limit

router = APIRouter()

@router.post("")
@rate_limit("60/minute")
async def add_cart(
    request: Request,
    payload: AddCartRequest,
    current_user: User = Depends(get_current_user)
):
    """Add a new cart for a user."""
    try:
        response = await save_cart(current_user.user_id, payload.cart_name)
        return response
    except Exception as e:  
        raise HTTPException(status_code=500, detail=str(e))

# EDIT CART NAME ROUTE
@router.put("/{cart_id}/edit-name")
async def edit_cart_name(
    cart_id: str,
    payload: EditCartNameRequest,
    current_user: User = Depends(get_current_user)
):
    """Edit the name of a specific cart."""
    try:
        response = await update_cart_name(current_user.user_id, cart_id, payload.new_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# RETRIEVE CART NAMES
@router.get("")
async def retrieve_carts(current_user: User = Depends(get_current_user)) -> dict:
    """Get all carts for a user."""
    try:
        carts = await get_carts(current_user.user_id)
        return {"carts": carts}  # FastAPI will auto-serialize List[Cart] to JSON
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE
@router.delete("/{cart_id}")
async def remove_cart(
    cart_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a specific cart for a user."""
    try:
        response = await delete_cart(current_user.user_id, cart_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
