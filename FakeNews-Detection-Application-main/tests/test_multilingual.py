"""Tests for Feature 1: Hindi and English regional language pipeline."""
import pytest
from src.translator import detect_language, contains_hindi, translate_to_english


def test_language_detection():
    """Verifies accurate detection of Hindi (Devanagari) and English text."""
    assert detect_language("This is a verified news article in English.") == "en"
    assert detect_language("यह एक हिन्दी समाचार लेख है।") == "hi"
    assert contains_hindi("ताज़ा समाचार") is True
    assert contains_hindi("Breaking News") is False


def test_english_translation_bypass():
    """Verifies that English text bypasses unnecessary translation."""
    result = translate_to_english("Standard English headline", source_lang="en")
    assert result["success"] is True
    assert result["was_translated"] is False
    assert result["translated_text"] == "Standard English headline"


def test_hindi_translation_pipeline_success(monkeypatch):
    """Verifies that Hindi input triggers translation and informs caller."""
    # Mock translator to ensure deterministic, offline-capable unit testing
    def mock_translate(text, source_lang="hi"):
        return {
            "success": True,
            "translated_text": "This is a translated English news article about clean energy.",
            "original_text": text,
            "was_translated": True,
            "error": None,
            "provider": "MockTranslator"
        }

    import src.translator
    monkeypatch.setattr(src.translator, "translate_to_english", mock_translate)

    result = src.translator.translate_to_english("यह सौर ऊर्जा पर एक समाचार लेख है।", source_lang="hi")
    assert result["success"] is True
    assert result["was_translated"] is True
    assert "clean energy" in result["translated_text"]


def test_hindi_translation_failure_handling(test_client, monkeypatch):
    """Verifies that translation network failure returns HTTP 422 with clear explanation."""
    def mock_failing_translate(text, source_lang="hi"):
        return {
            "success": False,
            "translated_text": "",
            "original_text": text,
            "was_translated": False,
            "error": "Hindi translation service is currently unavailable.",
            "provider": None
        }

    import app
    monkeypatch.setattr(app, "translate_to_english", mock_failing_translate)

    response = test_client.post("/predict", data={"news": "यह एक परीक्षण समाचार है"})
    assert response.status_code == 422
    data = response.get_json()
    assert data["prediction"] == "Error"
    assert data["translation_failed"] is True
    assert "translation service is currently unavailable" in data["message"]
