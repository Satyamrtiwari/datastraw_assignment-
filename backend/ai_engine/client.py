import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "groq/compound-mini").strip()


def get_groq_client():
    """
    Returns an authenticated Groq client if API key is configured,
    or None if key is absent.
    """
    if not GROQ_API_KEY or GROQ_API_KEY.startswith("your_"):
        return None
    try:
        from groq import Groq
        return Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"Warning: Failed to initialize Groq client: {e}")
        return None
