from fastapi import APIRouter, HTTPException
from app.functions.user import add_user_by_email,send_email_gmail
from app.functions.cart import get_carts

router = APIRouter()

@router.post("/users/add")
async def add_user(payload: dict):
    """
    Add a new user to the database or update their info.
    Expects a JSON payload with 'email' (required) and optional 'name'.
    """
    email = payload.get("email")
    name = payload.get("name", "Unknown")

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    try:
        response = await add_user_by_email(email, name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/carts/{email}/share")
async def share_cart(email: str, cart_id: str, recipient_email: str):
    """Share a cart by sending its details via email."""
    try:
        # Retrieve the user's carts
        user_carts = await get_carts(email)
        cart_to_share = next((cart for cart in user_carts if cart["cart_id"] == cart_id), None)

        if not cart_to_share:
            raise HTTPException(status_code=404, detail="Cart not found")

        cart_name = cart_to_share["cart_name"]
        cart_items = cart_to_share["items"]

        # Send email using Gmail SMTP
        result = send_email_gmail(recipient_email, cart_name, cart_items)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))