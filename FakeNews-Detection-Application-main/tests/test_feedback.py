"""Tests for Feature 6: SQLite User Feedback Storage and Rate Limiting."""
import pytest
from src.database import save_feedback, get_feedback_count, get_db_connection


def test_save_valid_feedback():
    """Verifies storing valid feedback in SQLite database."""
    initial_count = get_feedback_count()

    result = save_feedback(
        sentiment="helpful",
        comment="The explanation of words was very clear.",
        prediction="Real",
        confidence=0.92,
        news_excerpt="Reuters reporting on economic indicators",
        client_id="test_client_1"
    )

    assert result["success"] is True
    assert result["id"] is not None
    assert get_feedback_count() == initial_count + 1

    # Verify database content directly
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM feedback WHERE id = ?", (result["id"],)).fetchone()
        assert row["sentiment"] == "helpful"
        assert "The explanation" in row["comment"]
        assert row["prediction"] == "Real"
        assert row["confidence"] == 0.92


def test_reject_invalid_sentiment():
    """Verifies rejection of invalid feedback sentiment values."""
    result = save_feedback(sentiment="malicious_type", client_id="test_client_2")
    assert result["success"] is False
    assert "Invalid feedback type" in result["error"]


def test_feedback_endpoint_post(test_client):
    """Verifies that /feedback endpoint processes POST requests correctly."""
    response = test_client.post("/feedback", json={
        "sentiment": "incorrect",
        "comment": "The article uses satire which the model missed.",
        "prediction": "Real",
        "confidence": 0.58,
        "news_excerpt": "Satirical article text"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "recorded" in data["message"].lower()


def test_feedback_rate_limiting():
    """Verifies that excessive rapid feedback submissions from the same client are throttled."""
    client_ip = "198.51.100.99"
    # Make multiple submissions up to threshold
    for i in range(8):
        res = save_feedback(sentiment="helpful", client_id=client_ip)
        assert res["success"] is True

    # 9th submission should trigger rate limit
    blocked_res = save_feedback(sentiment="helpful", client_id=client_ip)
    assert blocked_res["success"] is False
    assert "too many" in blocked_res["error"].lower()
