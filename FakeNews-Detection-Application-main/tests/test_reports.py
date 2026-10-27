"""Tests for Feature 10: Shareable Analysis Report Generation."""
import pytest
from src.report_generator import generate_text_report, generate_html_report


def test_generate_text_report():
    """Verifies that plain text report contains all required verification and HCI fields."""
    sample_data = {
        "timestamp": "2026-10-20 12:00:00 UTC",
        "prediction": "Real",
        "confidence": 0.88,
        "is_uncertain": False,
        "input_type": "URL",
        "source_url": "https://www.reuters.com/article",
        "source_domain": "www.reuters.com",
        "was_translated": False,
        "explanation_summary": "Linguistic style matches traditional reporting patterns.",
        "influential_real": [{"word": "spokesperson", "impact": 0.12}],
        "influential_fake": [{"word": "shocking", "impact": -0.05}],
        "article_excerpt": "Official announcement made today regarding environmental regulations.",
        "fact_check_message": "Manual portal verification available.",
        "fact_check_links": [{"name": "Google Fact Check", "url": "https://factcheck.google.com"}]
    }

    report = generate_text_report(sample_data)
    assert "FAKENEWS AI" in report
    assert "REAL NEWS" in report
    assert "88.0%" in report
    assert "www.reuters.com" in report
    assert "spokesperson" in report
    assert "RESPONSIBLE AI" in report
    assert "HTTPS" in report


def test_generate_html_report_escaping():
    """Verifies safe HTML encoding preventing XSS injection."""
    malicious_data = {
        "timestamp": "2026-10-20",
        "prediction": "Fake",
        "confidence": 0.95,
        "is_uncertain": False,
        "input_type": "<script>alert('xss')</script>",
        "source_url": "javascript:alert(1)",
        "source_domain": "malicious.com",
        "explanation_summary": "<b>bold text</b>",
        "article_excerpt": "<img src=x onerror=alert(1)>",
        "influential_real": [],
        "influential_fake": []
    }

    html_report = generate_html_report(malicious_data)
    assert "<script>" not in html_report
    assert "&lt;script&gt;" in html_report
    assert "<img src=x" not in html_report


def test_download_report_endpoint(test_client):
    """Verifies that /download-report returns attachment for HTML and TXT formats."""
    payload = {
        "format": "html",
        "prediction": "Real",
        "confidence": 0.91,
        "is_uncertain": False,
        "input_type": "Text"
    }

    # Test HTML format
    resp_html = test_client.post("/download-report", json=payload)
    assert resp_html.status_code == 200
    assert "text/html" in resp_html.content_type
    assert "attachment" in resp_html.headers.get("Content-Disposition", "")

    # Test TXT format
    payload["format"] = "txt"
    resp_txt = test_client.post("/download-report", json=payload)
    assert resp_txt.status_code == 200
    assert "text/plain" in resp_txt.content_type
    assert "attachment" in resp_txt.headers.get("Content-Disposition", "")
