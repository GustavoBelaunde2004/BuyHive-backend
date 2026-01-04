"""Extraction API schemas for request/response validation."""
from pydantic import BaseModel, HttpUrl, field_validator
from app.utils.sanitize import sanitize_product_name


class ImageRequest(BaseModel):
    """Request schema for image analysis."""
    page_url: HttpUrl
    image_urls: str
    
    @field_validator('image_urls')
    @classmethod
    def validate_image_urls(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("image_urls cannot be empty")
        return v.strip()


class ProductVerificationRequest(BaseModel):
    """Request schema for product image verification."""
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


class URLRequest(BaseModel):
    """Request schema for URL classification."""
    url: HttpUrl

