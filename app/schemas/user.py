"""User API schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List


class ShareCartRequest(BaseModel):
    """Request schema for sharing a cart."""
    recipient_email: EmailStr
    cart_id: str
    
    @field_validator('cart_id')
    @classmethod
    def validate_cart_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Cart ID cannot be empty")
        return v.strip()


class UserResponse(BaseModel):
    """Response schema for user data (API-friendly, hides internal fields)."""
    email: str
    name: str
    auth0_id: Optional[str] = None

