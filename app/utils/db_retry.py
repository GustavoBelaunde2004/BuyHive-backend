"""
Database retry utilities for MongoDB operations.
Provides retry logic with exponential backoff for failed operations.
"""
import asyncio
from typing import Callable, Any, TypeVar, Coroutine
from functools import wraps

T = TypeVar('T')

async def retry_operation(
    operation: Callable[[], Coroutine[Any, Any, T]],
    max_retries: int = 3,
    initial_delay: float = 0.1,
    max_delay: float = 2.0,
    backoff_factor: float = 2.0
) -> T:
    """
    Retry an async database operation with exponential backoff.
    
    Args:
        operation: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay between retries
        backoff_factor: Multiplier for delay after each retry
        
    Returns:
        Result of the operation
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    delay = initial_delay
    
    for attempt in range(max_retries + 1):
        try:
            return await operation()
        except Exception as e:
            last_exception = e
            
            # Don't retry on last attempt
            if attempt < max_retries:
                await asyncio.sleep(min(delay, max_delay))
                delay *= backoff_factor
            else:
                # Last attempt failed, raise the exception
                raise last_exception
    
    # Should never reach here, but just in case
    raise last_exception

def with_retry(
    max_retries: int = 3,
    initial_delay: float = 0.1,
    max_delay: float = 2.0,
    backoff_factor: float = 2.0
):
    """
    Decorator to add retry logic to async database functions.
    
    Usage:
        @with_retry(max_retries=3)
        async def my_db_function(...):
            ...
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            async def operation():
                return await func(*args, **kwargs)
            
            return await retry_operation(
                operation,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                backoff_factor=backoff_factor
            )
        return wrapper
    return decorator

