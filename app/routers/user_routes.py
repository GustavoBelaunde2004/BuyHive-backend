from fastapi import APIRouter, HTTPException, Depends
from app.functions.user import send_email_gmail
from app.functions.item import retrieve_cart_items
from app.functions.database import carts_collection
from app.functions.base import ShareCartRequest
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

# Note: /users/add endpoint removed - users are now created via OAuth

@router.post("/carts/share")
# Route will be at /users/carts/share with prefix
async def share_cart(
    payload: ShareCartRequest,
    current_user: User = Depends(get_current_user)
):
    """Share a cart by sending its details via email."""
    try:
        # Extract data from request body
        recipient_email = payload.recipient_email
        cart_id = payload.cart_id

        # Get cart document first to get cart name and verify it exists
        cart_doc = await carts_collection.find_one({"user_id": current_user.user_id, "cart_id": cart_id})
        if not cart_doc:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        cart_name = cart_doc.get("cart_name", "Cart")

        # Retrieve cart items (cart already verified to exist)
        try:
            cart_items = await retrieve_cart_items(current_user.user_id, cart_id)
        except ValueError as e:
            # retrieve_cart_items raises ValueError if cart not found
            # This can happen in edge cases or test environments
            if "not found" in str(e).lower():
                raise HTTPException(status_code=404, detail="Cart not found")
            # Re-raise other ValueErrors as 500
            raise HTTPException(status_code=500, detail=str(e))

        # Send email using AWS SES (migrated from Gmail SMTP in Phase 3)
        result = await send_email_gmail(
            recipient_email, 
            cart_name, 
            cart_items,
            sender_name=current_user.name,
            sender_email=current_user.email
        )
        
        # Check if email sending failed
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result

    except HTTPException:
        # Re-raise HTTPException (like 404) as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))