import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get Gemini API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Check whether the API key exists
if not GOOGLE_API_KEY:
    raise ValueError("Google API key not found. Check your .env file.")
