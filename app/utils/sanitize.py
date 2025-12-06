import re
from html import escape


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
    - Stripping HTML tags
    - Escaping special characters
    - Limiting length
    """
    if not text:
        return ""
    
    # Strip HTML
    text = strip_html_tags(text)
    
    # Escape special characters (but keep basic formatting)
    text = escape(text)
    
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

