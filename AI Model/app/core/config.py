import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Load root .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
logger = logging.getLogger(__name__)

def setup_services():
    """Configure external services (Gemini API). Logging is handled by logging_config.py."""
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("Gemini API configured successfully.")
    else:
        logger.warning("GEMINI_API_KEY not set in environment.")

