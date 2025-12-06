from datetime import datetime, timedelta
from secrets import token_urlsafe
from typing import Optional
from app.functions.database import cart_collection
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_reset_token() -> str:
    """Generate a secure password reset token."""
    return token_urlsafe(32)


async def create_password_reset_token(email: str) -> str:
    """
    Create and store a password reset token for a user.
    
    Args:
        email: User's email address
    
    Returns:
        Reset token string
    
    Raises:
        ValueError: If user not found
    """
    user = await cart_collection.find_one({"email": email})
    if not user:
        raise ValueError("User not found")
    
    reset_token = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    
    # Store reset token in user document
    await cart_collection.update_one(
        {"email": email},
        {
            "$set": {
                "password_reset_token": reset_token,
                "password_reset_expires": expires_at.isoformat(),
            }
        }
    )
    
    return reset_token


async def verify_reset_token(email: str, token: str) -> bool:
    """
    Verify a password reset token.
    
    Args:
        email: User's email address
        token: Reset token to verify
    
    Returns:
        True if token is valid, False otherwise
    """
    user = await cart_collection.find_one({"email": email})
    
    if not user:
        return False
    
    stored_token = user.get("password_reset_token")
    expires_at_str = user.get("password_reset_expires")
    
    if not stored_token or not expires_at_str:
        return False
    
    # Check if token matches
    if stored_token != token:
        return False
    
    # Check if token has expired
    expires_at = datetime.fromisoformat(expires_at_str)
    if datetime.utcnow() > expires_at:
        return False
    
    return True


async def update_password(email: str, new_password: str, reset_token: str) -> bool:
    """
    Update user password using reset token.
    
    Args:
        email: User's email address
        new_password: New password (plain text)
        reset_token: Valid reset token
    
    Returns:
        True if password updated successfully, False otherwise
    """
    # Verify token
    if not await verify_reset_token(email, reset_token):
        return False
    
    # Hash password
    password_hash = pwd_context.hash(new_password)
    
    # Update password and clear reset token
    await cart_collection.update_one(
        {"email": email},
        {
            "$set": {
                "password_hash": password_hash,
                "updated_at": datetime.utcnow().isoformat(),
            },
            "$unset": {
                "password_reset_token": "",
                "password_reset_expires": "",
            }
        }
    )
    
    return True


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

