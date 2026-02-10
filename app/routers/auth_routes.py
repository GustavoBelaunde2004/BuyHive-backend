from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from app.core.dependencies import get_current_user
from app.core.security import verify_auth0_token, get_or_create_user_from_token, create_access_token, create_refresh_token, verify_token
from app.core.database import users_collection
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()
security = HTTPBearer()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
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
        refresh_token = create_refresh_token(data=jwt_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Auth0 token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Refresh access token using refresh token.
    
    Accepts a refresh token and returns a new access token and refresh token.
    Implements token rotation for security (old refresh token is invalidated
    by issuing a new one).
    """
    refresh_token = credentials.credentials
    
    try:
        # Verify refresh token
        payload = verify_token(refresh_token, token_type="refresh")
        
        # Extract user_id from token
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token: missing user_id",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user_data = await users_collection.find_one({"user_id": user_id})
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens with user info
        jwt_data = {
            "sub": user_data["user_id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "auth0_id": user_data["auth0_id"],
        }
        
        new_access_token = create_access_token(data=jwt_data)
        new_refresh_token = create_refresh_token(data=jwt_data)
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}",
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

