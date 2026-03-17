import cv2
import numpy as np
import os
from PIL import Image

def load_image(path):
    """Reads image using OpenCV and converts to RGB numpy array. 
    If a PDF is provided, extracts the first page as an image."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found at {path}")
    
    if path.lower().endswith('.pdf'):
        try:
            from pdf2image import convert_from_path
            pages = convert_from_path(path)
            if not pages:
                raise ValueError(f"No pages found in PDF {path}")
            img = pages[0].convert('RGB')
        except ImportError:
            raise ImportError("pdf2image package is required to process PDFs. Please install it with: pip install pdf2image")
    else:
        # Read using PIL to handle different formats safely, convert to RGB, then to NumPy
        img = Image.open(path).convert('RGB')
        
    return np.array(img)

def resize(image, size=(224, 224)):
    """Standardize dimensions for CNN. image shape: (H,W,3). Returns: (224,224,3)"""
    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)

def normalize(image):
    """Scale pixel values for neural network. Range: (0.0 - 1.0)"""
    return image.astype('float32') / 255.0

def to_grayscale(image):
    """Convert RGB to grayscale for OCR."""
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

def denoise(image):
    """Apply Gaussian blur to remove text noise for OCR."""
    return cv2.GaussianBlur(image, (5, 5), 0)

def preprocess_for_cnn(path, target_size=(224, 224)):
    """Full pipeline: load -> resize -> normalize -> batch dim. Returns: (1, 224, 224, 3)"""
    img = load_image(path)
    img_resized = resize(img, target_size)
    img_normalized = normalize(img_resized)
    # Add batch dimension (1, 224, 224, 3)
    return np.expand_dims(img_normalized, axis=0)

def preprocess_for_ocr(path):
    """Full pipeline: load -> grayscale -> denoise. Returns: 2D array"""
    img = load_image(path)
    img_gray = to_grayscale(img)
    img_denoised = denoise(img_gray)
    return img_denoised
