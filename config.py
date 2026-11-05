
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_CHAT_MODEL = "gemini-3.8-flash"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
GEMINI_503_MAX_ATTEMPTS = 3
GEMINI_REQUEST_TIMEOUT_SECONDS = 45

# First, check the local .env file
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# If not found, check Streamlit Cloud Secrets
if not GOOGLE_API_KEY:
    try:
        import streamlit as st
        GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        GOOGLE_API_KEY = None

# Validate API key
if not GOOGLE_API_KEY:
    raise ValueError(
        "Google API key not found. "
        "Configure GOOGLE_API_KEY in .env or Streamlit Secrets."
    )
