"""
Image preprocessing utilities for the document validation pipeline.

Provides deskew, denoise, contrast enhancement, and PDF-to-image conversion.
All functions accept / return PIL Images for pipeline compatibility.
"""
from __future__ import annotations


import logging
import os
from typing import Sequence

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from src.exceptions import ImageProcessingError

logger = logging.getLogger(__name__)

# ─── Poppler path from environment ───────────────────────────
_DEFAULT_POPPLER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "poppler", "Library", "bin",
)
POPPLER_PATH = os.getenv("POPPLER_PATH", _DEFAULT_POPPLER)


def load_image(image_path: str) -> Image.Image:
    """
    Load an image from disk, handling PDFs via pdf2image.

    Args:
        image_path: Absolute path to image or PDF file.

    Returns:
        PIL Image in RGB mode.

    Raises:
        ImageProcessingError: If the file cannot be loaded.
    """
    try:
        if image_path.lower().endswith(".pdf"):
            try:
                from pdf2image import convert_from_path

                pages = convert_from_path(image_path, poppler_path=POPPLER_PATH, dpi=300)
                if not pages:
                    raise ImageProcessingError("No pages found in PDF", path=image_path)
                return pages[0].convert("RGB")
            except ImportError:
                raise ImageProcessingError(
                    "pdf2image package is required for PDF processing",
                    path=image_path,
                )
        else:
            img = Image.open(image_path)
            return img.convert("RGB")
    except ImageProcessingError:
        raise
    except Exception as exc:
        raise ImageProcessingError(
            f"Cannot load image: {exc}",
            path=image_path,
            details={"original_error": type(exc).__name__},
        )



def enhance_for_ocr(image: Image.Image) -> Image.Image:
    """
    Apply preprocessing optimizations for OCR accuracy.

    Steps:
      1. Convert to grayscale for text detection.
      2. Increase contrast.
      3. Apply mild sharpening.
      4. Denoise.
      5. Return as RGB (Gemini expects RGB).

    Args:
        image: Input PIL Image (RGB).

    Returns:
        Enhanced PIL Image (RGB), optimized for OCR.
    """
    try:
        # Increase contrast
        enhancer = ImageEnhance.Contrast(image)
        enhanced = enhancer.enhance(1.5)

        # Sharpen
        enhanced = enhanced.filter(ImageFilter.SHARPEN)

        # Denoise via OpenCV (mild bilateral filter preserves edges)
        cv_img = np.array(enhanced)
        denoised = cv2.bilateralFilter(cv_img, d=9, sigmaColor=75, sigmaSpace=75)

        return Image.fromarray(denoised)
    except Exception as exc:
        logger.warning(f"Image enhancement failed, using original: {exc}")
        return image


def deskew_image(image: Image.Image, max_angle: float = 15.0) -> Image.Image:
    """
    Correct image skew using Hough line detection.

    Args:
        image: Input PIL Image.
        max_angle: Maximum skew angle to correct (degrees).

    Returns:
        Deskewed PIL Image.
    """
    try:
        cv_img = np.array(image)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(
            edges, 1, np.pi / 180, threshold=100,
            minLineLength=100, maxLineGap=10,
        )

        if lines is None or len(lines) == 0:
            return image

        # Calculate median angle from detected lines
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            if abs(angle) < max_angle:
                angles.append(angle)

        if not angles:
            return image

        median_angle = float(np.median(angles))

        if abs(median_angle) < 0.5:
            # Negligible skew — skip rotation
            return image

        logger.info(f"Deskewing image by {median_angle:.1f} degrees")

        # Rotate using PIL for clean output
        return image.rotate(-median_angle, resample=Image.BICUBIC, expand=True, fillcolor=(255, 255, 255))

    except Exception as exc:
        logger.warning(f"Deskew failed, using original: {exc}")
        return image


def preprocess_document(image: Image.Image, do_deskew: bool = True, do_enhance: bool = True) -> Image.Image:
    """
    Full preprocessing pipeline for document images.

    Args:
        image: Input PIL Image (RGB).
        do_deskew: Whether to apply deskewing.
        do_enhance: Whether to apply OCR enhancement.

    Returns:
        Preprocessed PIL Image.
    """
    result = image

    if do_deskew:
        result = deskew_image(result)

    if do_enhance:
        result = enhance_for_ocr(result)

    return result


def detect_qr_codes(image: Image.Image) -> list[dict]:
    """
    Detect and decode QR codes in a document image.

    Args:
        image: PIL Image to scan.

    Returns:
        List of dicts with 'data' and 'position' keys.
    """
    try:
        cv_img = np.array(image)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)

        detector = cv2.QRCodeDetector()
        retval, decoded_info, points, straight_qrcode = detector.detectAndDecodeMulti(gray)

        if not retval or decoded_info is None:
            return []

        results = []
        for i, data in enumerate(decoded_info):
            if data:
                result: dict = {"data": data}
                if points is not None and i < len(points):
                    bbox = points[i].tolist()
                    result["position"] = bbox
                results.append(result)

        return results
    except Exception as exc:
        logger.warning(f"QR code detection failed: {exc}")
        return []


def detect_watermark(image: Image.Image) -> dict:
    """
    Detect watermark presence using frequency domain analysis.

    Uses DFT to check for repeating patterns typical of watermarks.

    Args:
        image: PIL Image to analyze.

    Returns:
        Dict with 'detected' (bool) and 'confidence' (float).
    """
    try:
        cv_img = np.array(image)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)

        # Resize for consistent analysis
        h, w = gray.shape
        target_size = 512
        scale = target_size / max(h, w)
        resized = cv2.resize(gray, None, fx=scale, fy=scale)

        # Apply DFT
        f_transform = np.fft.fft2(resized.astype(np.float32))
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.log1p(np.abs(f_shift))

        # Analyze frequency spectrum — watermarks create distinctive peaks
        # in the mid-frequency range
        rows, cols = magnitude.shape
        center_r, center_c = rows // 2, cols // 2
        inner_radius = min(rows, cols) // 8
        outer_radius = min(rows, cols) // 3

        # Create annular mask for mid-frequency region
        y, x = np.ogrid[:rows, :cols]
        dist = np.sqrt((x - center_c) ** 2 + (y - center_r) ** 2)
        mask = (dist > inner_radius) & (dist < outer_radius)

        mid_freq_energy = float(np.mean(magnitude[mask]))
        total_energy = float(np.mean(magnitude))

        ratio = mid_freq_energy / (total_energy + 1e-8)

        # Heuristic: watermarks tend to have higher mid-frequency energy
        detected = ratio > 0.85
        confidence = min(ratio / 1.2, 1.0)

        return {"detected": detected, "confidence": round(confidence, 4)}

    except Exception as exc:
        logger.warning(f"Watermark detection failed: {exc}")
        return {"detected": False, "confidence": 0.0}


def detect_seal_stamp(image: Image.Image) -> dict:
    """
    Detect circular seals/stamps using Hough circle detection.

    Args:
        image: PIL Image to scan.

    Returns:
        Dict with 'detected' (bool), 'count' (int), and 'confidence' (float).
    """
    try:
        cv_img = np.array(image)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
        blurred = cv2.medianBlur(gray, 5)

        # Detect circles
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=50,
            param1=100,
            param2=50,
            minRadius=30,
            maxRadius=200,
        )

        if circles is None:
            return {"detected": False, "count": 0, "confidence": 0.0}

        count = len(circles[0])
        # Confidence: 1 circle = 0.7, 2+ circles = 0.9
        confidence = min(0.5 + count * 0.2, 1.0)

        return {
            "detected": True,
            "count": count,
            "confidence": round(confidence, 4),
        }

    except Exception as exc:
        logger.warning(f"Seal/stamp detection failed: {exc}")
        return {"detected": False, "count": 0, "confidence": 0.0}
