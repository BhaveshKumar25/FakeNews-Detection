"""Fact check integration module using Google Fact Check Tools API and trusted manual search portals."""
import logging
import urllib.parse
import requests

from src.config import FACT_CHECK_API_KEY, REQUEST_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)

GOOGLE_FACTCHECK_ENDPOINT = "https://factchecktools.googleapis.com/v1alpha1/claims:search"


def extract_search_query(text: str, max_words: int = 10) -> str:
    """Extracts a concise headline-like query from article text for claim search."""
    if not text:
        return ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    first_line = lines[0] if lines else text.strip()
    words = first_line.split()[:max_words]
    return " ".join(words)


def build_manual_factcheck_links(query: str) -> list[dict]:
    """Generates direct, prefilled search links to verified fact-checking organizations."""
    encoded_query = urllib.parse.quote_plus(query)
    return [
        {
            "name": "Google Fact Check Explorer",
            "url": f"https://toolbox.google.com/factcheck/explorer/search/{encoded_query}",
            "description": "Search global fact-check database directly"
        },
        {
            "name": "Snopes Fact Check",
            "url": f"https://www.snopes.com/?s={encoded_query}",
            "description": "Urban legends, rumors, and viral news verification"
        },
        {
            "name": "PolitiFact",
            "url": f"https://www.politifact.com/search/?q={encoded_query}",
            "description": "Political claims and public statements fact-checking"
        },
        {
            "name": "Alt News (India / Regional)",
            "url": f"https://www.altnews.in/?s={encoded_query}",
            "description": "Indian and regional viral misinformation verification"
        },
        {
            "name": "BOOM Live",
            "url": f"https://www.boomlive.in/search?q={encoded_query}",
            "description": "Independent South Asian fact-checking initiative"
        }
    ]


def search_fact_checks(query: str, language_code: str = "en") -> dict:
    """
    Searches for related claims via the Google Fact Check Tools API.
    
    If no API key is configured or the API is unreachable, provides
    honest explanation and curated manual search alternatives.
    Never fabricates fake fact-check claims.
    """
    clean_query = extract_search_query(query)
    if not clean_query:
        return {
            "api_configured": bool(FACT_CHECK_API_KEY),
            "claims": [],
            "manual_links": [],
            "message": "No query could be derived from the text.",
            "query_used": ""
        }

    manual_links = build_manual_factcheck_links(clean_query)

    if not FACT_CHECK_API_KEY:
        return {
            "api_configured": False,
            "claims": [],
            "manual_links": manual_links,
            "query_used": clean_query,
            "message": (
                "Google Fact Check API key is not configured in environment variables (FACT_CHECK_API_KEY). "
                "You can search trusted independent fact-checking databases manually using the links below."
            ),
            "note": "A related fact-check discusses similar public claims and may not match this exact article."
        }

    params = {
        "query": clean_query,
        "key": FACT_CHECK_API_KEY,
        "languageCode": language_code,
        "pageSize": 5
    }

    try:
        response = requests.get(
            GOOGLE_FACTCHECK_ENDPOINT,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS
        )

        if response.status_code == 400:
            return {
                "api_configured": True,
                "claims": [],
                "manual_links": manual_links,
                "query_used": clean_query,
                "message": "Invalid query parameters sent to Fact Check API.",
                "note": "Try adjusting your article headline."
            }

        if response.status_code == 403:
            return {
                "api_configured": True,
                "claims": [],
                "manual_links": manual_links,
                "query_used": clean_query,
                "message": "Fact Check API key is invalid or quota has been reached.",
                "note": "Use the manual search links below."
            }

        if response.status_code != 200:
            return {
                "api_configured": True,
                "claims": [],
                "manual_links": manual_links,
                "query_used": clean_query,
                "message": f"Fact Check API returned status {response.status_code}.",
                "note": "Use the manual search links below."
            }

        data = response.json()
        raw_claims = data.get("claims", [])

        parsed_claims = []
        for c in raw_claims:
            claim_text = c.get("text", "")
            claimant = c.get("claimant", "Unknown Claimant")
            claim_date = c.get("claimDate", "")
            reviews = c.get("claimReview", [])

            for r in reviews:
                publisher = r.get("publisher", {}).get("name", "Independent Fact-Checker")
                publisher_site = r.get("publisher", {}).get("site", "")
                rating = r.get("textualRating", "Unrated")
                review_url = r.get("url", "")
                title = r.get("title", "")
                review_date = r.get("reviewDate", "")

                parsed_claims.append({
                    "claim": claim_text,
                    "claimant": claimant,
                    "claim_date": claim_date,
                    "publisher": publisher,
                    "publisher_site": publisher_site,
                    "rating": rating,
                    "url": review_url,
                    "title": title,
                    "review_date": review_date
                })

        return {
            "api_configured": True,
            "claims": parsed_claims,
            "manual_links": manual_links,
            "query_used": clean_query,
            "message": "Fact check results retrieved successfully." if parsed_claims else "No exact public claims matched this query in the Fact Check database.",
            "note": (
                "Related fact-checks may discuss a similar topic or general claim rather than this exact article. "
                "Always review the publisher's full article for detailed context."
            )
        }

    except requests.exceptions.Timeout:
        return {
            "api_configured": True,
            "claims": [],
            "manual_links": manual_links,
            "query_used": clean_query,
            "message": "Fact Check API request timed out.",
            "note": "Use the manual search links below."
        }
    except Exception as e:
        logger.error("Fact check query error: %s", e)
        return {
            "api_configured": True,
            "claims": [],
            "manual_links": manual_links,
            "query_used": clean_query,
            "message": f"Fact Check API error: {str(e)}",
            "note": "Use the manual search links below."
        }
