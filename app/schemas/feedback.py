"""Feedback API schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, field_validator


class FeedbackFormRequest(BaseModel):
    """Request schema for feedback form submissions (bug reports or feature requests)."""
    type: str
    description: str
    firstName: str
    lastName: str
    email: EmailStr
    timestamp: str  # ISO format timestamp
    
    @field_validator('type', 'description', 'firstName', 'lastName')
    @classmethod
    def validate_required_fields(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return v.strip()

