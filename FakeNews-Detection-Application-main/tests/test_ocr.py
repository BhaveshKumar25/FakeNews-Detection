"""Tests for Feature 3: News Screenshot OCR Analysis."""
import os
import io
import pytest
from PIL import Image
from src.ocr_reader import extract_text_from_image


def test_ocr_invalid_file_extension(tmp_path):
    """Verifies that non-image file extensions are rejected."""
    bad_file = tmp_path / "test.txt"
    bad_file.write_text("Not an image")
    result = extract_text_from_image(str(bad_file))
    assert result["success"] is False
    assert "unsupported" in result["error"].lower() or "invalid" in result["error"].lower()


def test_ocr_small_dimensions(tmp_path):
    """Verifies that images smaller than 50x50 are rejected as too small."""
    tiny_img = Image.new("RGB", (20, 20), color="white")
    img_path = tmp_path / "tiny.png"
    tiny_img.save(str(img_path))

    result = extract_text_from_image(str(img_path))
    assert result["success"] is False
    assert "dimensions are too small" in result["error"].lower()


def test_ocr_oversized_file(tmp_path, monkeypatch):
    """Verifies that images larger than MAX_UPLOAD_SIZE_BYTES are rejected."""
    # Set limit very low (100 bytes) in src.ocr_reader to trigger size error without writing 5MB to disk
    monkeypatch.setattr("src.ocr_reader.MAX_UPLOAD_SIZE_BYTES", 100)

    img = Image.new("RGB", (100, 100), color="white")
    img_path = tmp_path / "oversized.png"
    img.save(str(img_path))

    result = extract_text_from_image(str(img_path))
    assert result["success"] is False
    assert "exceeds" in result["error"].lower()


def test_ocr_mock_success(tmp_path, monkeypatch):
    """Verifies successful text extraction when Tesseract OCR is available."""
    valid_img = Image.new("RGB", (300, 100), color="white")
    img_path = tmp_path / "screenshot.png"
    valid_img.save(str(img_path))

    # Mock winocr unavailable so it exercises Tesseract fallback
    monkeypatch.setattr("src.ocr_reader.is_winocr_available", lambda: False)
    monkeypatch.setattr("src.ocr_reader.resolve_tesseract_command", lambda: "mock_tesseract.exe")
    monkeypatch.setattr("src.ocr_reader.pytesseract.image_to_string", lambda *args, **kwargs: "Breaking: Economic summit announces stimulus package.")
    monkeypatch.setattr("src.ocr_reader.pytesseract.get_languages", lambda *args: ["eng", "hin"])

    result = extract_text_from_image(str(img_path), preferred_lang="eng")
    assert result["success"] is True
    assert "Economic summit announces stimulus package" in result["text"]


def test_ocr_winocr_mock_success(tmp_path, monkeypatch):
    """Verifies successful text extraction when Windows OCR (winocr) is available."""
    valid_img = Image.new("RGB", (300, 100), color="white")
    img_path = tmp_path / "screenshot_winocr.png"
    valid_img.save(str(img_path))

    monkeypatch.setattr("src.ocr_reader.is_winocr_available", lambda: True)
    monkeypatch.setattr("src.ocr_reader.winocr.recognize_pil_sync", lambda img, lang: {"text": "Parliament passes new healthcare reforms bill."})

    result = extract_text_from_image(str(img_path), preferred_lang="eng")
    assert result["success"] is True
    assert "healthcare reforms" in result["text"]


def test_ocr_upload_endpoint_cleanup(test_client, tmp_path, monkeypatch):
    """Verifies that uploaded temporary screenshots are always deleted after processing."""
    # Create valid dummy image in memory
    img_byte_arr = io.BytesIO()
    img = Image.new("RGB", (200, 80), color="white")
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    monkeypatch.setattr("src.ocr_reader.is_winocr_available", lambda: False)
    monkeypatch.setattr("src.ocr_reader.resolve_tesseract_command", lambda: "mock_tesseract.exe")
    monkeypatch.setattr("src.ocr_reader.pytesseract.image_to_string", lambda *args, **kwargs: "Extracted news text from uploaded file.")
    monkeypatch.setattr("src.ocr_reader.pytesseract.get_languages", lambda *args: ["eng"])

    response = test_client.post(
        "/ocr-upload",
        data={"image": (img_byte_arr, "test_article.png"), "language": "eng"},
        content_type="multipart/form-data"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "Extracted news text" in data["text"]
