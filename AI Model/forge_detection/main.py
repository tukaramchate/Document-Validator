# filename: app.py
import base64
import json
import re
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import google.generativeai as genai

# ---------- CORS Setup ----------
# Development: allow all origins
# Production: restrict to trusted domains only
allow_origins = ["*"]  # ✅ allows all origins during development
# Example for production:
# allow_origins = [
#     "http://localhost:3000",    # Local frontend
#     "https://your-frontend-domain.com"  # Deployed frontend
# ]

# ---------- Load environment variables ----------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in .env")

genai.configure(api_key=GEMINI_API_KEY)

# ---------- FastAPI App ----------
app = FastAPI(
    title="Forge Detection API",
    description="Analyze document images for visual manipulation and forgery",
    version="1.0"
)

# ---------- Add CORS Middleware ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # Must be False if origins is *
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ---------- Core Function ----------
import sys
import pathlib
_BASE_DIR = pathlib.Path(__file__).parent.parent
sys.path.append(str(_BASE_DIR))
from model import DocumentValidator

# Initialize model once
validator = DocumentValidator()
validator.load_model()

# ---------- API Endpoint ----------
@app.get("/health")
async def health():
    return {"status": "ok", "service": "Forge Detection API v1.0"}

@app.post("/detect/")
async def detect_forgery(file: UploadFile = File(...)):
    if not file.content_type or not (file.content_type.startswith("image/") or file.content_type == "application/pdf"):
        raise HTTPException(status_code=400, detail=f"Only image and PDF files are supported. Received: {file.content_type}")
        
    # Save file temporarily to pass to the model
    import tempfile
    suffix = pathlib.Path(file.filename).suffix if file.filename else ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
        
    try:
        # We only need the CNN result for pure forge detection
        # But we'll use the full validator to ensure the image is loaded correctly
        result = validator.validate(temp_path)
        cnn_result = result.get("cnn_result", {})
    finally:
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    return JSONResponse(content=cnn_result)
