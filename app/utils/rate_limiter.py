"""
Rate limiting utilities for FastAPI routes.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings
from fastapi import Request

def get_rate_limit_key(request: Request):
    """Get rate limit key from request (IP address)."""
    return get_remote_address(request)

# Create limiter instance
limiter = Limiter(key_func=get_rate_limit_key) if settings.RATE_LIMIT_ENABLED else None

def rate_limit(limit: str):
    """
    Decorator for rate limiting that works even when limiter is None.
    
    Note: Functions using this decorator MUST have `request: Request` as a parameter.
    
    Usage:
        @rate_limit("10/minute")
        async def my_endpoint(request: Request, ...):
            ...
    """
    def decorator(func):
        if limiter:
            # Apply slowapi's limit decorator
            return limiter.limit(limit)(func)
        else:
            # If rate limiting is disabled, return function as-is
            return func
    return decorator

