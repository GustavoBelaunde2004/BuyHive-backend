from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime


class User(BaseModel):
    """User model matching database structure."""
    user_id: str  # Auth0 sub (stable)
    email: EmailStr
    name: str
    auth0_id: Optional[str] = None  # kept for compatibility (same as user_id)
    password_hash: Optional[str] = None  # For future email/password auth
    cart_count: int = 0
    cart_ids: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserInDB(User):
    """User model as stored in database (includes MongoDB _id)."""
    id: Optional[str] = None  # MongoDB _id

