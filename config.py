"""
Legacy config file - kept for backward compatibility.
All new code should use app.core.config.settings instead.
"""
from app.core.config import settings

# Export settings for backward compatibility
MONGO_URL = settings.MONGO_URL
GROQ_API_KEY = settings.GROQ_API_KEY
GMAIL_USER = settings.GMAIL_USER
GMAIL_PASSWORD = settings.GMAIL_PASSWORD
OPENAI_API_KEY = settings.OPENAI_API_KEY
GOOGLE_SEARCH_API = settings.GOOGLE_SEARCH_API
CSE_ID = settings.CSE_ID

