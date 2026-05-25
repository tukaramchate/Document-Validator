"""
Dataset Preparation Script — Institution Format Classifier.

Scans the data/ directory, converts PDFs to images (for GHRCEM/digilocker),
and reorganises everything into a clean PyTorch ImageFolder structure:

    data/prepared/
        BNMIT/        <- images from B.N.M INSTITUTE OF TECHNOLOGY/train_* + valid_*
        GHRCEM/       <- images converted from GHRCEM/*.pdf
        SPPU/         <- images from SPPU/*.jpg + SPPU/*.webp
        digilocker/   <- images converted from digilocker/*.pdf

Usage:
    python scripts/prepare_dataset.py
"""

from __future__ import annotations

import io
import os
import shutil
import sys
import warnings

from PIL import Image

warnings.filterwarnings("ignore")

# ─── Paths ───────────────────────────────────────────────────
DATA_ROOT     = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_ROOT   = os.path.join(DATA_ROOT, "prepared")
POPPLER_PATH  = os.environ.get(
    "POPPLER_PATH",
    os.path.join(os.path.dirname(__file__), "..", "poppler", "Library", "bin"),
)

# Mapping: folder_name -> class_label (sanitised name used as directory)
CLASS_MAP = {
    "B.N.M INSTITUTE OF TECHNOLOGY": "BNMIT",
    "GHRCEM":                         "GHRCEM",
    "SPPU":                           "SPPU",
    "digilocker":                     "digilocker",
}

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
PDF_EXT  = ".pdf"


def pdf_to_images(pdf_path: str, dpi: int = 200) -> list[Image.Image]:
    """Convert a PDF file to a list of PIL Images (one per page)."""
    try:
        from pdf2image import convert_from_path
        pages = convert_from_path(pdf_path, dpi=dpi, poppler_path=POPPLER_PATH)
        return pages
    except ImportError:
        print("  [!] pdf2image not installed — skipping PDF conversion.")
        return []
    except Exception as e:
        print(f"  [!] Failed to convert {pdf_path}: {e}")
        return []


def save_image(img: Image.Image, out_path: str) -> None:
    """Save a PIL image as JPEG, ensuring RGB mode."""
    img.convert("RGB").save(out_path, "JPEG", quality=92)


def prepare_bnmit(src_dir: str, out_dir: str) -> int:
    """B.N.M — already has train_/valid_/test_ prefixed images. Copy all."""
    os.makedirs(out_dir, exist_ok=True)
    count = 0
    for fname in os.listdir(src_dir):
        ext = os.path.splitext(fname)[1].lower()
        if ext not in IMG_EXTS:
            continue
        src = os.path.join(src_dir, fname)
        # Normalise to .jpg
        dst = os.path.join(out_dir, f"{os.path.splitext(fname)[0]}.jpg")
        try:
            img = Image.open(src)
            save_image(img, dst)
            count += 1
        except Exception as e:
            print(f"  [!] Skipping {fname}: {e}")
    return count


def prepare_from_images(src_dir: str, out_dir: str, label: str) -> int:
    """Generic — copy/convert all images in a flat directory."""
    os.makedirs(out_dir, exist_ok=True)
    count = 0
    for fname in os.listdir(src_dir):
        fpath = os.path.join(src_dir, fname)
        if os.path.isdir(fpath):
            # Recurse one level (e.g. SPPU/degree/)
            count += prepare_from_images(fpath, out_dir, label)
            continue
        ext = os.path.splitext(fname)[1].lower()
        if ext not in IMG_EXTS:
            continue
        dst = os.path.join(out_dir, f"{label}_{count:04d}.jpg")
        try:
            img = Image.open(fpath)
            save_image(img, dst)
            count += 1
        except Exception as e:
            print(f"  [!] Skipping {fname}: {e}")
    return count


def prepare_from_pdfs(src_dir: str, out_dir: str, label: str) -> int:
    """Convert each page of every PDF to a separate JPEG."""
    os.makedirs(out_dir, exist_ok=True)
    count = 0
    for fname in sorted(os.listdir(src_dir)):
        if os.path.splitext(fname)[1].lower() != PDF_EXT:
            continue
        pdf_path = os.path.join(src_dir, fname)
        print(f"    Converting PDF: {fname}")
        pages = pdf_to_images(pdf_path)
        for i, page in enumerate(pages):
            dst = os.path.join(out_dir, f"{label}_{count:04d}_p{i:02d}.jpg")
            save_image(page, dst)
            count += 1
    return count


def main() -> None:
    print("=" * 60)
    print("  Institution Format Dataset Preparation")
    print("=" * 60)

    # Clean output
    if os.path.exists(OUTPUT_ROOT):
        shutil.rmtree(OUTPUT_ROOT)
        print(f"Cleared old prepared/ directory.\n")

    totals: dict[str, int] = {}

    for folder_name, class_label in CLASS_MAP.items():
        src_dir = os.path.join(DATA_ROOT, folder_name)
        out_dir = os.path.join(OUTPUT_ROOT, class_label)

        if not os.path.isdir(src_dir):
            print(f"[!] Source not found: {src_dir} — skipping.")
            continue

        print(f"[{folder_name}] → class '{class_label}'")

        # Determine source type
        all_files = os.listdir(src_dir)
        has_pdfs = any(f.lower().endswith(PDF_EXT) for f in all_files)
        has_imgs = any(os.path.splitext(f)[1].lower() in IMG_EXTS for f in all_files)

        if folder_name == "B.N.M INSTITUTE OF TECHNOLOGY":
            n = prepare_bnmit(src_dir, out_dir)
        elif has_pdfs and not has_imgs:
            n = prepare_from_pdfs(src_dir, out_dir, class_label)
        else:
            n = prepare_from_images(src_dir, out_dir, class_label)

        print(f"  → {n} images prepared.\n")
        totals[class_label] = n

    # Summary
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    total = 0
    for cls, n in totals.items():
        print(f"  {cls:<20} {n:>4} images")
        total += n
    print(f"  {'TOTAL':<20} {total:>4} images")
    print(f"\n  Output: {OUTPUT_ROOT}")
    print("=" * 60)

    if total == 0:
        print("\n[ERROR] No images prepared. Check data folder structure.")
        sys.exit(1)


if __name__ == "__main__":
    main()
