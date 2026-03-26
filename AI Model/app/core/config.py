import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Load root .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def setup_services():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        logging.getLogger(__name__).info("Gemini API configured successfully.")
    else:
        logging.getLogger(__name__).warning("GEMINI_API_KEY not set in environment.")
