"""FastAPI dependencies for authentication and dependency injection."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from app.core.security import verify_auth0_token, get_or_create_user_from_token
from app.core.database import users_collection
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.failed_page_extraction_repository import FailedPageExtractionRepository
from app.repositories.failed_item_extraction_repository import FailedItemExtractionRepository
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


# Repository dependency injection functions
def get_user_repository() -> UserRepository:
    """Get UserRepository instance."""
    return UserRepository()


def get_cart_repository() -> CartRepository:
    """Get CartRepository instance."""
    return CartRepository()


def get_item_repository() -> ItemRepository:
    """Get ItemRepository instance."""
    return ItemRepository()


def get_feedback_repository() -> FeedbackRepository:
    """Get FeedbackRepository instance."""
    return FeedbackRepository()


def get_failed_page_extraction_repository() -> FailedPageExtractionRepository:
    """Get FailedPageExtractionRepository instance."""
    return FailedPageExtractionRepository()


def get_failed_item_extraction_repository() -> FailedItemExtractionRepository:
    """Get FailedItemExtractionRepository instance."""
    return FailedItemExtractionRepository()


# Service dependency injection functions
from app.services.cart_service import CartService
from app.services.item_service import ItemService
from app.services.user_service import UserService
from app.services.feedback_service import FeedbackService
from app.services.failed_extraction_service import FailedExtractionService


def get_cart_service(
    cart_repo: CartRepository = Depends(get_cart_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    item_repo: ItemRepository = Depends(get_item_repository)
) -> CartService:
    """Get CartService instance."""
    return CartService(cart_repo, user_repo, item_repo)


def get_item_service(
    item_repo: ItemRepository = Depends(get_item_repository),
    cart_repo: CartRepository = Depends(get_cart_repository)
) -> ItemService:
    """Get ItemService instance."""
    return ItemService(item_repo, cart_repo)


def get_user_service(
    item_service: ItemService = Depends(get_item_service),
    cart_repo: CartRepository = Depends(get_cart_repository)
) -> UserService:
    """Get UserService instance."""
    return UserService(item_service, cart_repo)


def get_feedback_service(
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository)
) -> FeedbackService:
    """Get FeedbackService instance."""
    return FeedbackService(feedback_repo)


def get_failed_extraction_service(
    page_extraction_repo: FailedPageExtractionRepository = Depends(get_failed_page_extraction_repository),
    item_extraction_repo: FailedItemExtractionRepository = Depends(get_failed_item_extraction_repository)
) -> FailedExtractionService:
    """Get FailedExtractionService instance."""
    return FailedExtractionService(page_extraction_repo, item_extraction_repo)

