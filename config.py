from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access variables
MONGO_URL = os.getenv("MONGO_URL")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWROD")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

GOOGLE_SEARCH_API = os.getenv("GOOGLE_SEARCH_API")
CSE_ID = os.getenv("CSE_ID")

