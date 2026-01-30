import re
from html import unescape


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from text."""
    if not text:
        return ""
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    return clean.strip()


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input text by:
    - Decoding any existing HTML entities (to prevent double-encoding)
    - Stripping HTML tags
    - Limiting length
    Note: We don't escape characters here since we're storing in DB, not rendering HTML.
    """
    if not text:
        return ""
    
    # First, decode any existing HTML entities (in case data is already encoded)
    text = unescape(text)
    
    # Strip HTML tags
    text = strip_html_tags(text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()


def sanitize_product_name(name: str, max_length: int = 200) -> str:
    """Sanitize product name."""
    return sanitize_text(name, max_length)


def sanitize_notes(notes: str, max_length: int = 500) -> str:
    """Sanitize item notes."""
    return sanitize_text(notes, max_length)

