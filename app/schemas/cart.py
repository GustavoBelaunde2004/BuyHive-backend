"""Cart API schemas for request/response validation."""
from pydantic import BaseModel, field_validator
from typing import List
from app.utils.sanitize import sanitize_product_name


class AddCartRequest(BaseModel):
    """Request schema for creating a new cart."""
    cart_name: str
    
    @field_validator('cart_name')
    @classmethod
    def validate_cart_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Cart name cannot be empty")
        if len(v.strip()) > 100:
            raise ValueError("Cart name must be 100 characters or less")
        return sanitize_product_name(v.strip(), max_length=100)


class EditCartNameRequest(BaseModel):
    """Request schema for editing a cart name."""
    new_name: str
    
    @field_validator('new_name')
    @classmethod
    def validate_new_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Cart name cannot be empty")
        if len(v.strip()) > 100:
            raise ValueError("Cart name must be 100 characters or less")
        return sanitize_product_name(v.strip(), max_length=100)


class CartResponse(BaseModel):
    """Response schema for cart data."""
    cart_id: str
    cart_name: str
    item_count: int
    created_at: str
    item_ids: List[str]

