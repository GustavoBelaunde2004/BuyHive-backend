from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class ImageRequest(BaseModel):
    page_url: str
    image_urls: str

class ProductVerificationRequest(BaseModel):
    product_name: str
    price: str
    image_url: str

class Item(BaseModel):
    name: str
    price: str
    image: Optional[HttpUrl]
    url: Optional[HttpUrl]
    notes: Optional[str]

class AddCartRequest(BaseModel):
    cart_name: str

class EditCartNameRequest(BaseModel):
    new_name: str

class Item(BaseModel):
    name: str
    price: str
    image: Optional[HttpUrl]  # Optional URL for the product image
    url: Optional[HttpUrl]    # Optional URL for the product
    notes: Optional[str]      # Optional notes about the item

class ModifyCartRequest(BaseModel):
    items: List[Item]

class EditNoteRequest(BaseModel):
    new_note: str

# Request body for adding a new item
class AddNewItemRequest(BaseModel):
    name: str
    price: str
    image: Optional[HttpUrl]  # Optional URL for the product image
    url: Optional[HttpUrl]    # Optional URL for the product
    notes: Optional[str]      # Optional notes about the item
    selected_cart_ids: List[str]  # Carts to add the new item to

# Request body for modifying an existing item
class ModifyItemAcrossCartsRequest(BaseModel):
    add_to_cart_ids: List[str]
    remove_from_cart_ids: List[str]

class ShareCartRequest(BaseModel):
    recipient_email: str
    cart_id: str

# Request model for incoming URLs
class URLRequest(BaseModel):
    url: str
