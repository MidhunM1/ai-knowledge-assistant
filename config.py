import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

GEMINI_CHAT_MODEL = "gemini-3.8-flash"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
GEMINI_503_MAX_ATTEMPTS = 3
GEMINI_REQUEST_TIMEOUT_SECONDS = 45

# Get Gemini API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Check whether the API key exists
if not GOOGLE_API_KEY:
    raise ValueError("Google API key not found. Check your .env file.")
