from fastapi import APIRouter, HTTPException
from app.functions.base import AddCartRequest,EditCartNameRequest
from app.functions.cart import save_cart, get_carts, delete_cart,update_cart_name

router = APIRouter()

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
