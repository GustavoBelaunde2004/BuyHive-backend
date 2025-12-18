from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.functions.user import send_email_gmail
from app.functions.cart import get_carts
from app.functions.base import ShareCartRequest
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

# Note: /users/add endpoint removed - users are now created via OAuth

@router.post("/carts/share")
# Route will be at /users/carts/share with prefix
async def share_cart(
    payload: ShareCartRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Share a cart by sending its details via email."""
    try:
        # Extract data from request body
        recipient_email = payload.recipient_email
        cart_id = payload.cart_id

        # Retrieve the user's carts
        user_carts = await get_carts(current_user.user_id)
        cart_to_share = next((cart for cart in user_carts if cart.cart_id == cart_id), None)

        if not cart_to_share:
            raise HTTPException(status_code=404, detail="Cart not found")

        cart_name = cart_to_share.cart_name
        cart_items = cart_to_share.items

        # Send email asynchronously in background (non-blocking)
        background_tasks.add_task(
            send_email_gmail,
            recipient_email,
            cart_name,
            cart_items
        )
        
        # Return immediately without waiting for email delivery
        return {"message": "Cart shared successfully! Email is being sent."}

    except HTTPException:
        # Re-raise HTTPException (like 404) as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))