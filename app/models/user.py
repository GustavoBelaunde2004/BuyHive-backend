from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime


class User(BaseModel):
    """User model matching database structure."""
    email: EmailStr
    name: str
    auth0_id: Optional[str] = None  # Auth0 user ID (sub claim)
    password_hash: Optional[str] = None  # For future email/password auth
    cart_count: int = 0
    carts: List[dict] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserInDB(User):
    """User model as stored in database (includes MongoDB _id)."""
    id: Optional[str] = None  # MongoDB _id

