from pydantic import BaseModel, HttpUrl, EmailStr, field_validator
from typing import List, Optional
from app.utils.sanitize import sanitize_product_name, sanitize_notes

class ImageRequest(BaseModel):
    page_url: HttpUrl
    image_urls: str
    
    @field_validator('image_urls')
    @classmethod
    def validate_image_urls(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("image_urls cannot be empty")
        return v.strip()

class ProductVerificationRequest(BaseModel):
    product_name: str
    price: str
    image_url: HttpUrl
    
    @field_validator('product_name')
    @classmethod
    def validate_product_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("product_name cannot be empty")
        return sanitize_product_name(v.strip())
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("price cannot be empty")
        return v.strip()

class Item(BaseModel):
    name: str
    price: str
    image: Optional[HttpUrl]  # Optional URL for the product image
    url: Optional[HttpUrl]    # Optional URL for the product
    notes: Optional[str]      # Optional notes about the item
    
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

class AddCartRequest(BaseModel):
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
    new_name: str
    
    @field_validator('new_name')
    @classmethod
    def validate_new_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Cart name cannot be empty")
        if len(v.strip()) > 100:
            raise ValueError("Cart name must be 100 characters or less")
        return sanitize_product_name(v.strip(), max_length=100)

class ModifyCartRequest(BaseModel):
    items: List[Item]

class EditNoteRequest(BaseModel):
    new_note: str
    
    @field_validator('new_note')
    @classmethod
    def validate_new_note(cls, v: str) -> str:
        return sanitize_notes(v.strip()) if v.strip() else ""

# Request body for adding a new item
class AddNewItemRequest(BaseModel):
    name: str
    price: str
    image: Optional[HttpUrl]  # Optional URL for the product image
    url: Optional[HttpUrl]    # Optional URL for the product
    notes: Optional[str]      # Optional notes about the item
    selected_cart_ids: List[str]  # Carts to add the new item to
    
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

# Request body for modifying an existing item
class ModifyItemAcrossCartsRequest(BaseModel):
    add_to_cart_ids: List[str]
    remove_from_cart_ids: List[str]

class ShareCartRequest(BaseModel):
    recipient_email: EmailStr
    cart_id: str
    
    @field_validator('cart_id')
    @classmethod
    def validate_cart_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Cart ID cannot be empty")
        return v.strip()

# Request model for incoming URLs
class URLRequest(BaseModel):
    url: HttpUrl
