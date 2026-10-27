"""Optical Character Recognition (OCR) module for screenshot analysis.

Primary OCR Engine: Windows OCR (winocr) — Built into Windows 10/11.
Requires no separate Tesseract installation. Uses Windows.Media.Ocr WinRT APIs.

Fallback OCR Engine: Tesseract (pytesseract) — If winocr is unavailable.
"""
import os
import shutil
import asyncio
from pathlib import Path
from PIL import Image

from src.config import TESSERACT_CMD, MAX_UPLOAD_SIZE_BYTES

try:
    import winocr
except ImportError:
    winocr = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

# Allowed file formats
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
ALLOWED_PIL_FORMATS = {"PNG", "JPEG"}

# Standard Windows Tesseract paths (fallback only)
STANDARD_WINDOWS_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
]


def is_winocr_available() -> bool:
    """Returns True if winocr (Windows built-in OCR) is installed and functional."""
    return winocr is not None


def resolve_tesseract_command() -> str | None:
    """Locates the Tesseract executable on the system."""
    if TESSERACT_CMD and os.path.isfile(TESSERACT_CMD):
        return TESSERACT_CMD
    path_binary = shutil.which("tesseract")
    if path_binary:
        return path_binary
    for path in STANDARD_WINDOWS_TESSERACT_PATHS:
        if os.path.isfile(path):
            return path
    return None


def is_ocr_available() -> bool:
    """Returns True if ANY OCR engine is available (winocr or Tesseract)."""
    return is_winocr_available() or resolve_tesseract_command() is not None


def _validate_image(image_path: str) -> tuple[bool, str, str | None, int, int]:
    """
    Validates image path, file size, format, and dimensions.
    Returns (is_valid, error_message, pil_format, width, height).
    """
    if not os.path.isfile(image_path):
        return False, "Uploaded image file does not exist on disk.", None, 0, 0

    file_size = os.path.getsize(image_path)
    if file_size > MAX_UPLOAD_SIZE_BYTES:
        return False, f"Image file size ({file_size / (1024*1024):.1f}MB) exceeds the 5MB limit.", None, 0, 0

    try:
        with Image.open(image_path) as img:
            fmt = img.format
            w, h = img.size

        if fmt not in ALLOWED_PIL_FORMATS:
            return False, f"Unsupported image format '{fmt}'. Please upload a PNG or JPG/JPEG image.", None, 0, 0
        if w < 50 or h < 50:
            return False, "Image dimensions are too small (minimum 50×50 pixels).", fmt, w, h
        if w > 8000 or h > 8000:
            return False, "Image dimensions are too large (maximum 8000×8000 pixels).", fmt, w, h

        return True, "", fmt, w, h
    except Exception as e:
        return False, f"Invalid or corrupted image file: {str(e)}", None, 0, 0


def _ocr_with_winocr(image_path: str, preferred_lang: str = "eng") -> dict:
    """
    Performs OCR using the Windows 10/11 built-in Windows.Media.Ocr engine via winocr.
    No separate installation required — works out-of-the-box on Windows 10/11.
    """
    if winocr is None:
        return {
            "success": False,
            "error": "Windows OCR (winocr) is not available.",
            "text": "",
            "language_used": None,
            "engine": "none"
        }

    # Map OCR lang codes to winocr/BCP-47 format
    lang_map = {
        "eng": "en", "en": "en",
        "hin": "hi", "hi": "hi",
        "eng+hin": "en"  # winocr processes one language at a time; use English
    }
    lang_code = lang_map.get(preferred_lang.lower(), "en")

    try:
        with Image.open(image_path) as img:
            # Ensure RGB mode for best compatibility
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            # Attempt OCR with selected language
            try:
                result = winocr.recognize_pil_sync(img, lang_code)
            except Exception:
                # Language not installed — fall back to English
                lang_code = "en"
                result = winocr.recognize_pil_sync(img, "en")

        # winocr returns a plain dict with 'text' key
        extracted_text = ""
        if isinstance(result, dict):
            extracted_text = result.get("text", "").strip()
        elif hasattr(result, "text"):
            extracted_text = (result.text or "").strip()
        else:
            extracted_text = str(result).strip()

        # Clean up control characters and normalize whitespace
        extracted_text = " ".join(extracted_text.split())

        if not extracted_text:
            return {
                "success": False,
                "error": "No readable text was identified in the uploaded screenshot. "
                         "Please ensure the image has clear, dark text on a light background.",
                "text": "",
                "language_used": f"Windows OCR ({lang_code})",
                "engine": "winocr"
            }

        return {
            "success": True,
            "error": None,
            "text": extracted_text,
            "language_used": f"Windows OCR ({lang_code})",
            "engine": "winocr"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Windows OCR extraction failed: {str(e)}",
            "text": "",
            "language_used": f"Windows OCR ({lang_code})",
            "engine": "winocr"
        }


def _ocr_with_tesseract(image_path: str, preferred_lang: str = "eng") -> dict:
    """
    Performs OCR using the Tesseract engine (fallback when winocr unavailable).
    """
    if pytesseract is None:
        return {
            "success": False,
            "error": "Tesseract OCR (pytesseract) is not installed in Python.",
            "text": "",
            "language_used": None,
            "engine": "none"
        }

    tess_path = resolve_tesseract_command()
    if not tess_path:
        return {
            "success": False,
            "error": (
                "No OCR engine is available on this system.\n"
                "Option 1 (Recommended): Install winocr — run: pip install winocr\n"
                "Option 2: Install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki\n"
                "You can still paste the article text manually to analyze it."
            ),
            "text": "",
            "language_used": None,
            "engine": "none"
        }

    pytesseract.pytesseract.tesseract_cmd = tess_path

    lang_to_use = "eng"
    try:
        available_langs = pytesseract.get_languages()
        if "hin" in available_langs and ("hin" in preferred_lang or preferred_lang == "hi"):
            lang_to_use = "eng+hin"
        elif "hin" in available_langs:
            lang_to_use = "eng+hin"
    except Exception:
        lang_to_use = "eng"

    try:
        with Image.open(image_path) as img:
            if img.mode not in ("L", "RGB"):
                img = img.convert("RGB")
            extracted = pytesseract.image_to_string(img, lang=lang_to_use)

        cleaned_text = " ".join(extracted.split())
        if not cleaned_text:
            return {
                "success": False,
                "error": "No readable text could be found in the uploaded image.",
                "text": "",
                "language_used": lang_to_use,
                "engine": "tesseract"
            }
        return {
            "success": True,
            "error": None,
            "text": cleaned_text,
            "language_used": lang_to_use,
            "engine": "tesseract"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Tesseract OCR extraction failed: {str(e)}",
            "text": "",
            "language_used": lang_to_use,
            "engine": "tesseract"
        }


def extract_text_from_image(image_path: str, preferred_lang: str = "eng") -> dict:
    """
    Main entry point. Validates the uploaded image, then runs OCR.
    
    Priority:
      1. Windows OCR (winocr) — built-in, no extra install on Windows 10/11
      2. Tesseract OCR — fallback if winocr not available
      3. Helpful error message if neither is available
      
    Always ensures caller can delete the temporary file after processing.
    """
    # Step 1: Validate image file
    is_valid, error_msg, fmt, w, h = _validate_image(image_path)
    if not is_valid:
        return {
            "success": False,
            "error": error_msg,
            "text": "",
            "language_used": None,
            "engine": None
        }

    # Step 2: Try winocr first (Windows built-in OCR — no separate install needed)
    if is_winocr_available():
        return _ocr_with_winocr(image_path, preferred_lang)

    # Step 3: Fall back to Tesseract
    if resolve_tesseract_command():
        return _ocr_with_tesseract(image_path, preferred_lang)

    # Step 4: No OCR engine available
    return {
        "success": False,
        "error": (
            "No OCR engine is available. "
            "Windows OCR (winocr) is the recommended option — install it with: pip install winocr\n"
            "Alternatively, install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki\n"
            "You can also paste the article text directly into the text input tab."
        ),
        "text": "",
        "language_used": None,
        "engine": None
    }
