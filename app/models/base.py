from pydantic import BaseModel

class ImageRequest(BaseModel):
    page_url: str
    image_urls: str

class ProductVerificationRequest(BaseModel):
    product_name: str
    price: str
    image_url: str
