from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from app.auth.dependencies import get_current_user
from app.auth.password_reset import create_password_reset_token, update_password
from app.models.user import User

router = APIRouter()


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    token: str
    new_password: str


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


@router.post("/password-reset/request")
async def request_password_reset(request: PasswordResetRequest):
    """Request password reset token (sends email - to be implemented with SES)."""
    try:
        reset_token = await create_password_reset_token(request.email)
        
        # TODO: Send email with reset link using AWS SES (Phase 3)
        # For now, return token (in production, don't return token, send via email)
        return {
            "message": "Password reset token generated",
            "token": reset_token,  # Remove this in production, send via email
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/password-reset/confirm")
async def confirm_password_reset(request: PasswordResetConfirm):
    """Confirm password reset with token."""
    success = await update_password(
        request.email,
        request.new_password,
        request.token
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {"message": "Password updated successfully"}

