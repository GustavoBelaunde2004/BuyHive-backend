"""Failed Extraction API schemas for request/response validation."""
from pydantic import BaseModel, HttpUrl


class FailedExtractionRequest(BaseModel):
    """Request schema for failed extraction submissions."""
    url: HttpUrl

