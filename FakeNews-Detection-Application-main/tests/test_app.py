"""Tests for Flask routes, model inference, and uncertainty warnings."""
import json
import pytest
from src.preprocess import clean_text


def test_home_page_loads(test_client):
    """Verifies that the home page loads successfully with HTTP 200."""
    response = test_client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "FakeNews" in html
    assert "Analyze News" in html
    assert "id=\"news\"" in html


def test_empty_prediction_input(test_client):
    """Verifies that empty news input returns HTTP 400 with helpful error."""
    response = test_client.post("/predict", data={"news": "   "})
    assert response.status_code == 400
    data = response.get_json()
    assert data["prediction"] == "Error"
    assert "enter news" in data["message"].lower()


def test_stopwords_only_input(test_client):
    """Verifies that input containing only stopwords or punctuation returns HTTP 400."""
    response = test_client.post("/predict", data={"news": "the and of in a to"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["prediction"] == "Error"
    assert "stopwords" in data["message"].lower()


def test_normal_english_prediction(test_client):
    """Verifies that normal English text produces a prediction, confidence, and explanation."""
    sample = (
        "WASHINGTON (Reuters) - The Senate voted overwhelmingly on Thursday to confirm "
        "the new budget agreement, clearing the path for presidential signature."
    )
    response = test_client.post("/predict", data={"news": sample})
    assert response.status_code == 200
    data = response.get_json()

    assert data["prediction"] in ["Real", "Fake"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert 0.0 <= data["prob_real"] <= 1.0
    assert 0.0 <= data["prob_fake"] <= 1.0
    assert "explanation" in data
    assert data["explanation"]["supported"] is True
    assert "fact_check" in data
    assert data["was_translated"] is False


def test_real_fake_class_mapping(test_client):
    """Verifies that class 1 maps to Real and class 0 maps to Fake."""
    from app import model
    assert model is not None
    # Verify model class labels
    assert list(model.classes_) == [0, 1]

    # Test that prediction string logic maps 1 -> Real and 0 -> Fake
    cleaned = clean_text("Reuters Washington Senate legislation passed")
    proba = model.predict_proba([cleaned])[0]
    pred = model.predict([cleaned])[0]

    if pred == 1:
        expected = "Real"
    else:
        expected = "Fake"

    response = test_client.post("/predict", data={"news": "Reuters Washington Senate legislation passed"})
    data = response.get_json()
    assert data["prediction"] == expected


def test_uncertainty_warning_triggered(test_client, monkeypatch):
    """Verifies that predictions with confidence below UNCERTAINTY_THRESHOLD flag uncertainty."""
    # Temporarily set threshold high (0.99) so the prediction is classified as uncertain
    import src.config
    import app

    monkeypatch.setattr(src.config, "UNCERTAINTY_THRESHOLD", 0.99)
    monkeypatch.setattr(app, "UNCERTAINTY_THRESHOLD", 0.99)

    response = test_client.post("/predict", data={"news": "Some mixed report with ambiguous claims."})
    assert response.status_code == 200
    data = response.get_json()
    assert data["is_uncertain"] is True
    assert data["uncertainty_warning"] is not None
    assert data["uncertainty_warning"]["flagged"] is True
    assert "Low confidence" in data["uncertainty_warning"]["message_en"]


def test_json_payload_support(test_client):
    """Verifies that /predict accepts application/json payloads."""
    payload = {
        "news": "Global climate summit agrees on joint conservation targets.",
        "language": "en",
        "simple_mode": True
    }
    response = test_client.post(
        "/predict",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["prediction"] in ["Real", "Fake"]


def test_hindi_prediction_endpoint_success(test_client, monkeypatch):
    """Verifies that Hindi news triggers translation and completes inference."""
    monkeypatch.setattr(
        "app.translate_to_english",
        lambda text, source_lang="hi": {
            "success": True,
            "translated_text": "Scientists announce major breakthrough in clean solar energy technology.",
            "original_text": text,
            "was_translated": True,
            "error": None,
            "provider": "MockTranslator"
        }
    )

    hindi_news = "वैज्ञानिकों ने स्वच्छ सौर ऊर्जा प्रौद्योगिकी में बड़ी सफलता की घोषणा की।"
    response = test_client.post("/predict", data={"news": hindi_news, "language": "hi"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["prediction"] in ["Real", "Fake"]
    assert data["was_translated"] is True
    assert data["original_hindi"] == hindi_news


def test_hindi_translation_failure_endpoint(test_client, monkeypatch):
    """Verifies that translation network failure returns HTTP 422 with explanation."""
    monkeypatch.setattr(
        "app.translate_to_english",
        lambda text, source_lang="hi": {
            "success": False,
            "translated_text": "",
            "original_text": text,
            "was_translated": False,
            "error": "Hindi translation service is currently unavailable.",
            "provider": None
        }
    )

    hindi_news = "ताजा खबर: तकनीकी सम्मेलन आयोजित किया गया।"
    response = test_client.post("/predict", data={"news": hindi_news, "language": "hi"})
    assert response.status_code == 422
    data = response.get_json()
    assert data["prediction"] == "Error"
    assert data["translation_failed"] is True
    assert "translation service" in data["message"].lower()


def test_model_unloaded_error(test_client, monkeypatch):
    """Verifies HTTP 503 is returned if ML model is unavailable."""
    import app
    monkeypatch.setattr(app, "model", None)

    response = test_client.post("/predict", data={"news": "Some breaking headline."})
    assert response.status_code == 503
    data = response.get_json()
    assert data["prediction"] == "Error"
    assert "not currently loaded" in data["message"].lower()


def test_keyboard_shortcuts_and_fitts_elements_in_html(test_client):
    """Verifies Shneiderman Rule 2 shortcut badges, modal, and Fitts' Law attributes."""
    response = test_client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Shneiderman Rule 2: Shortcut cues
    assert 'aria-keyshortcuts="Control+Enter"' in html
    assert 'aria-keyshortcuts="Escape"' in html
    assert 'id="shortcutsModal"' in html
    assert 'id="shortcutsBtn"' in html
    assert 'Alt+1' in html
    assert 'Alt+2' in html
    assert 'Alt+3' in html

    # Fitts' Law: Primary & secondary action button targets
    assert 'id="analyzeBtn"' in html
    assert 'id="clearBtn"' in html
