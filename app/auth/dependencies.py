from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from app.auth.auth0 import verify_auth0_token, get_or_create_user_from_token
from app.functions.database import users_collection
from app.models.user import User
from typing import Optional

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    FastAPI dependency to get the current authenticated user.
    
    Validates Auth0 JWT token and returns user object.
    Creates user in database if doesn't exist.
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    try:
        # Verify Auth0 token
        payload = await verify_auth0_token(token)
        
        # Get or create user from token
        user_info = await get_or_create_user_from_token(payload)
        user_id = user_info["user_id"]
        
        # Get user from database
        user_data = await users_collection.find_one({"user_id": user_id})
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Convert to User model
        user = User(**user_data)
        return user
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        # Handle case where token doesn't have valid email
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    FastAPI dependency to get the current user if authenticated, None otherwise.
    
    Useful for routes that work with or without authentication.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

