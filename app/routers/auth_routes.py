from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    Useful for frontend to check if user is logged in and get user details.
    """
    return {
        "email": current_user.email,
        "name": current_user.name,
        "auth0_id": getattr(current_user, "auth0_id", None),
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout endpoint.
    Note: With Auth0, token invalidation is typically handled on the frontend.
    This endpoint is kept for consistency and can be used for server-side cleanup if needed.
    """
    # Auth0 handles token invalidation on their side
    # This endpoint can be used for any server-side cleanup if needed
    return {"message": "Logged out successfully"}

