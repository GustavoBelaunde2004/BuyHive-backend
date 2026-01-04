"""Item API schemas for request/response validation."""
from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, List
from app.utils.sanitize import sanitize_product_name, sanitize_notes


class AddNewItemRequest(BaseModel):
    """Request schema for adding a new item."""
    name: str
    price: str
    image: Optional[HttpUrl] = None
    url: Optional[HttpUrl] = None
    notes: Optional[str] = None
    selected_cart_ids: List[str]
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Item name cannot be empty")
        return sanitize_product_name(v.strip())
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Price cannot be empty")
        return v.strip()
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return sanitize_notes(v.strip()) if v.strip() else None
    
    @field_validator('selected_cart_ids')
    @classmethod
    def validate_cart_ids(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("At least one cart must be selected")
        return v


class EditNoteRequest(BaseModel):
    """Request schema for editing an item note."""
    new_note: str
    
    @field_validator('new_note')
    @classmethod
    def validate_new_note(cls, v: str) -> str:
        return sanitize_notes(v.strip()) if v.strip() else ""


class MoveItemRequest(BaseModel):
    """Request schema for moving an item between carts."""
    selected_cart_ids: List[str]


class ItemResponse(BaseModel):
    """Response schema for item data."""
    item_id: str
    name: str
    price: str
    image: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None
    added_at: str
    selected_cart_ids: Optional[List[str]] = None

