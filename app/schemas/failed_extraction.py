"""Failed Extraction API schemas for request/response validation."""
from pydantic import BaseModel, HttpUrl, Field


class FailedPageExtractionRequest(BaseModel):
    """Request schema for failed page extraction submissions."""
    url: HttpUrl
    failure_type: str = Field(..., description="Type of failure (e.g., 'unsupported', 'no_product', 'parsing_error')")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence that this is a failure (0.0-1.0)")


class FailedItemExtractionRequest(BaseModel):
    """Request schema for failed item extraction submissions."""
    url: HttpUrl
    type: str = Field(..., description="Type of failure (e.g., 'maybe', 'not_a_product')")
    image_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence for image extraction (0.0-1.0)")
    name_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence for name extraction (0.0-1.0)")
    price_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence for price extraction (0.0-1.0)")

