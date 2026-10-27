"""Tests for Feature 4 & Feature 8: Explainable AI and Simple Language Mode."""
import pytest
from app import model
from src.preprocess import clean_text
from src.explainer import explain_prediction


def test_explainer_with_real_model():
    """Verifies that model generates feature contributions aligned with class definitions."""
    sample = "Scientists at the university confirmed significant discoveries in laboratory experiments."
    cleaned = clean_text(sample)

    explanation = explain_prediction(
        model=model,
        cleaned_text=cleaned,
        raw_text=sample,
        simple_mode=False,
        language="en"
    )

    assert explanation["supported"] is True
    assert "disclaimer" in explanation
    assert len(explanation["real_words"]) > 0 or len(explanation["fake_words"]) > 0

    # Verify that positive impact words are categorized as Real
    for word_info in explanation["real_words"]:
        assert word_info["impact"] > 0
        assert word_info["favors"] == "Real"

    # Verify that negative impact words are categorized as Fake
    for word_info in explanation["fake_words"]:
        assert word_info["impact"] < 0
        assert word_info["favors"] == "Fake"


def test_explainer_empty_input_honesty():
    """Verifies that input with no extractable words reports an honest limitation instead of fabricating."""
    explanation = explain_prediction(
        model=model,
        cleaned_text="",
        raw_text="",
        simple_mode=True,
        language="en"
    )
    assert explanation["supported"] is False
    assert "cannot be generated" in explanation["summary"].lower() or "no extractable" in explanation["summary"].lower()


def test_simple_vs_detailed_mode():
    """Verifies that simple and detailed modes produce appropriately worded summaries."""
    sample = "Official spokesperson issued a verified statement regarding the legislation."
    cleaned = clean_text(sample)

    simple_exp = explain_prediction(model, cleaned, sample, simple_mode=True, language="en")
    detailed_exp = explain_prediction(model, cleaned, sample, simple_mode=False, language="en")

    assert simple_exp["simple_mode"] is True
    assert detailed_exp["simple_mode"] is False
    assert len(simple_exp["summary"]) > 0
    assert len(detailed_exp["summary"]) > 0
    # Detailed mode includes technical log-odds or decomposition reference
    assert "log-odds" in detailed_exp["summary"].lower() or "tokens" in detailed_exp["summary"].lower()


def test_hindi_explanation_summary():
    """Verifies that Hindi explanation summary is correctly rendered in Hindi."""
    sample = "Government officials released a report on economic development."
    cleaned = clean_text(sample)

    hi_exp = explain_prediction(model, cleaned, sample, simple_mode=True, language="hi")
    assert hi_exp["language"] == "hi"
    assert any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in hi_exp["summary"])
