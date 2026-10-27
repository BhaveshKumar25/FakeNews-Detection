"""Tests for Feature 9: Google Fact Check Tools API and manual search portals."""
import pytest
from src.fact_checker import extract_search_query, build_manual_factcheck_links, search_fact_checks


def test_extract_search_query():
    """Verifies concise extraction of search query from headline text."""
    long_article = "Drinking twenty cups of coffee daily makes humans invisible according to viral internet rumors.\nAdditional paragraph text."
    query = extract_search_query(long_article, max_words=8)
    assert len(query.split()) <= 8
    assert "coffee" in query.lower()


def test_manual_links_generation():
    """Verifies that direct, properly encoded manual links are generated for trusted fact-check portals."""
    links = build_manual_factcheck_links("drinking coffee invisibility")
    assert len(links) >= 4
    names = [l["name"] for l in links]
    assert any("Google Fact Check" in n for n in names)
    assert any("Snopes" in n for n in names)
    assert any("PolitiFact" in n for n in names)
    assert any("Alt News" in n for n in names)
    for link in links:
        assert link["url"].startswith("https://")
        assert "drinking+coffee" in link["url"] or "drinking%20coffee" in link["url"]


def test_search_fact_checks_without_api_key(monkeypatch):
    """Verifies that missing API key returns honest explanation and manual search portals."""
    import src.fact_checker
    monkeypatch.setattr(src.fact_checker, "FACT_CHECK_API_KEY", "")

    result = search_fact_checks("Solar power breakthrough reported in California")
    assert result["api_configured"] is False
    assert len(result["manual_links"]) > 0
    assert "not configured" in result["message"]
    assert len(result["claims"]) == 0


def test_search_fact_checks_with_mock_api(monkeypatch):
    """Verifies successful parsing of Google Fact Check Tools API response."""
    import src.fact_checker
    monkeypatch.setattr(src.fact_checker, "FACT_CHECK_API_KEY", "MOCK_KEY_12345")

    class MockApiResponse:
        status_code = 200
        def json(self):
            return {
                "claims": [
                    {
                        "text": "Drinking coffee causes invisibility",
                        "claimant": "Social Media Viral Posts",
                        "claimDate": "2026-02-10",
                        "claimReview": [
                            {
                                "publisher": {"name": "Snopes", "site": "snopes.com"},
                                "textualRating": "False",
                                "url": "https://www.snopes.com/fact-check/coffee-invisible",
                                "title": "Coffee and Invisibility Claim Debunked",
                                "reviewDate": "2026-02-11"
                            }
                        ]
                    }
                ]
            }

    monkeypatch.setattr("src.fact_checker.requests.get", lambda *args, **kwargs: MockApiResponse())

    result = search_fact_checks("Drinking coffee causes invisibility")
    assert result["api_configured"] is True
    assert len(result["claims"]) == 1
    claim = result["claims"][0]
    assert claim["rating"] == "False"
    assert claim["publisher"] == "Snopes"
    assert claim["url"] == "https://www.snopes.com/fact-check/coffee-invisible"
