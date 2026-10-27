"""Tests for Feature 2 & Feature 5: Safe URL Fetching and SSRF Protection."""
import pytest
from unittest.mock import MagicMock
from src.url_fetcher import is_safe_url, fetch_article_from_url


def test_url_ssrf_filtering():
    """Verifies that localhost, private IPs, loopback, and invalid protocols are blocked."""
    # Loopback
    is_safe, msg = is_safe_url("http://127.0.0.1/admin")
    assert is_safe is False
    assert "restricted" in msg.lower() or "prohibited" in msg.lower()

    # Localhost
    is_safe, msg = is_safe_url("http://localhost:5000/api")
    assert is_safe is False

    # Private IPv4 addresses
    is_safe, msg = is_safe_url("http://192.168.1.10/router")
    assert is_safe is False
    assert "prohibited" in msg.lower()

    is_safe, msg = is_safe_url("http://10.0.0.5/")
    assert is_safe is False

    is_safe, msg = is_safe_url("http://172.16.0.1/")
    assert is_safe is False

    # Non-HTTP schemes
    is_safe, msg = is_safe_url("file:///etc/passwd")
    assert is_safe is False
    assert "unsupported" in msg.lower()

    is_safe, msg = is_safe_url("ftp://ftp.example.com/file")
    assert is_safe is False


def test_valid_public_url():
    """Verifies that standard public HTTPS URLs pass validation."""
    is_safe, msg = is_safe_url("https://www.reuters.com/world/article-test")
    assert is_safe is True
    assert msg == ""


def test_fetch_url_success(monkeypatch):
    """Verifies parsing of article title, body text, domain, and publication date."""
    mock_html = b"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta property="og:title" content="Verified Summit Reaches Climate Accord">
        <meta property="article:published_time" content="2026-03-15T12:00:00Z">
    </head>
    <body>
        <nav><a href="/">Home</a></nav>
        <article>
            <p>Delegates from nearly two hundred nations concluded intense deliberations today.</p>
            <p>The agreement outlines concrete milestones for renewable infrastructure financing.</p>
        </article>
        <footer>Copyright 2026</footer>
    </body>
    </html>
    """

    class MockResponse:
        status_code = 200
        url = "https://www.example-news.org/article"
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def iter_content(self, chunk_size=1024):
            yield mock_html

    monkeypatch.setattr("src.url_fetcher.requests.get", lambda *args, **kwargs: MockResponse())
    monkeypatch.setattr("src.url_fetcher.is_safe_url", lambda url: (True, ""))

    result = fetch_article_from_url("https://www.example-news.org/article")
    assert result["success"] is True
    assert result["title"] == "Verified Summit Reaches Climate Accord"
    assert "Delegates from nearly two hundred nations" in result["text"]
    assert result["domain"] == "www.example-news.org"
    assert result["publish_date"] == "2026-03-15T12:00:00Z"
    assert "HTTPS" in result["verification_note"]


def test_fetch_url_timeout_handling(monkeypatch):
    """Verifies graceful handling of network timeouts."""
    import requests
    def mock_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout("Connection timed out.")

    monkeypatch.setattr("src.url_fetcher.requests.get", mock_timeout)
    monkeypatch.setattr("src.url_fetcher.is_safe_url", lambda url: (True, ""))

    result = fetch_article_from_url("https://www.slow-server.org/news")
    assert result["success"] is False
    assert "timed out" in result["error"].lower()


def test_fetch_url_forbidden_handling(monkeypatch):
    """Verifies that HTTP 403 Forbidden returns paywall/anti-scraping guidance."""
    class Mock403Response:
        status_code = 403
        url = "https://www.paywall-news.com/article"
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    monkeypatch.setattr("src.url_fetcher.requests.get", lambda *args, **kwargs: Mock403Response())
    monkeypatch.setattr("src.url_fetcher.is_safe_url", lambda url: (True, ""))

    result = fetch_article_from_url("https://www.paywall-news.com/article")
    assert result["success"] is False
    assert "403" in result["error"]
