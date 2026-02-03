"""Feedback API schemas for request/response validation."""
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


class FeedbackFormRequest(BaseModel):
    """Request schema for feedback form submissions (bug reports or feature requests)."""
    type: str
    description: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[EmailStr] = None
    
    @field_validator('type', 'description')
    @classmethod
    def validate_required_fields(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return v.strip()

