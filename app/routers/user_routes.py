from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user import ShareCartRequest
from app.services.user_service import UserService
from app.core.dependencies import get_current_user, get_user_service
from app.models.user import User

router = APIRouter()

@router.post("/carts/share", response_model=dict)
async def share_cart(
    payload: ShareCartRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Share a cart by sending its details via email."""
    try:
        result = await user_service.share_cart(
            current_user.user_id,
            payload.cart_id,
            payload.recipient_email,
            current_user.name,
            current_user.email
        )
        
        # Check if email sending failed
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
