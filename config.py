
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_secret(name):
    # First check local .env
    value = os.getenv(name)

    if value:
        return value

    # Otherwise check Streamlit Cloud Secrets
    try:
        return st.secrets.get(name)
    except Exception:
        return None


# API keys
GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")
GROQ_API_KEY = get_secret("GROQ_API_KEY")
SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")

# Models
GROQ_CHAT_MODEL = "openai/gpt-oss-120b"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"

# Gemini settings
GEMINI_503_MAX_ATTEMPTS = 3
GEMINI_REQUEST_TIMEOUT_SECONDS = 45


# Validate API keys
if not GOOGLE_API_KEY:
    raise ValueError(
        "Google API key not found. "
        "Configure GOOGLE_API_KEY in .env or Streamlit Secrets."
    )

if not GROQ_API_KEY:
    raise ValueError(
        "Groq API key not found. "
        "Configure GROQ_API_KEY in .env or Streamlit Secrets."
    )
