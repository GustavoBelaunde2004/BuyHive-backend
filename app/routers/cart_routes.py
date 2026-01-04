from fastapi import APIRouter, HTTPException, Depends, Request
from app.schemas.cart import AddCartRequest, EditCartNameRequest, CartResponse
from app.services.cart_service import CartService
from app.core.dependencies import get_current_user, get_cart_service
from app.models.user import User
from app.utils.rate_limiter import rate_limit

router = APIRouter()

@router.post("", response_model=CartResponse)
@rate_limit("60/minute")
async def add_cart(
    request: Request,
    payload: AddCartRequest,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    """Add a new cart for a user."""
    try:
        response = await cart_service.create_cart(current_user.user_id, payload.cart_name)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:  
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{cart_id}/edit-name", response_model=dict)
async def edit_cart_name(
    cart_id: str,
    payload: EditCartNameRequest,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    """Edit the name of a specific cart."""
    try:
        response = await cart_service.update_cart_name(
            current_user.user_id, 
            cart_id, 
            payload.new_name
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=dict)
async def retrieve_carts(
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
) -> dict:
    """Get all carts for a user."""
    try:
        carts = await cart_service.get_user_carts(current_user.user_id)
        return {"carts": carts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{cart_id}", response_model=dict)
async def remove_cart(
    cart_id: str,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    """Delete a specific cart for a user."""
    try:
        response = await cart_service.delete_cart(current_user.user_id, cart_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
