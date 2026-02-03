from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.dependencies import get_current_user
from app.core.security import verify_auth0_token, get_or_create_user_from_token, create_access_token
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()
security = HTTPBearer()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/exchange", response_model=TokenResponse)
async def exchange_auth0_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Exchange Auth0 access token for internal JWT.
    
    This endpoint validates the Auth0 token and returns a shorter-lived
    internal JWT that can be used for subsequent API requests.
    """
    auth0_token = credentials.credentials
    
    try:
        # Verify Auth0 token
        payload = await verify_auth0_token(auth0_token)
        
        # Get or create user from token
        user_info = await get_or_create_user_from_token(payload)
        
        # Create internal JWT with user info
        jwt_data = {
            "sub": user_info["user_id"],
            "email": user_info["email"],
            "name": user_info["name"],
            "auth0_id": user_info["auth0_id"],
        }
        
        access_token = create_access_token(data=jwt_data)
        
        return TokenResponse(access_token=access_token)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Auth0 token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


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

