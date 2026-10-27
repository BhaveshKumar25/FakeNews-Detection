"""Safe URL fetcher and metadata extraction module."""
import ipaddress
import re
import socket
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from src.config import REQUEST_TIMEOUT_SECONDS

# Increased to 8MB — most real article pages are under this limit
MAX_RESPONSE_BYTES = 8 * 1024 * 1024  # 8 MB

# Extra-robust browser headers to avoid bot-detection 403s
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1"
}


def is_safe_url(url: str) -> tuple[bool, str]:
    """
    Validates that a URL uses HTTP/HTTPS and does not point to private,
    loopback, link-local, or reserved network addresses (SSRF prevention).
    Returns (is_safe, error_reason).
    """
    if not url or not isinstance(url, str):
        return False, "URL is empty or invalid."

    url = url.strip()
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Malformed URL format."

    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Unsupported URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "URL does not contain a valid hostname."

    if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        return False, "Access to localhost or loopback addresses is restricted."

    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)
            if (
                ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_reserved
                or ip_obj.is_multicast
            ):
                return False, f"Access to private or restricted network address ({ip_str}) is prohibited."
    except socket.gaierror:
        return False, f"Could not resolve domain name '{hostname}'. Please check the URL."
    except Exception as e:
        return False, f"Host validation failed: {str(e)}"

    return True, ""


def _extract_text_from_soup(soup: BeautifulSoup) -> str:
    """
    Tries multiple HTML content selectors to extract maximum readable article text.
    Removes navigation noise and returns cleaned paragraphs joined together.
    """
    # Remove noise tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form",
                     "svg", "figure", "figcaption", "button", "noscript", "iframe"]):
        tag.decompose()

    body_texts = []

    # Strategy 1: semantic <article> tag
    article_el = soup.find("article")
    if article_el:
        paragraphs = article_el.find_all(["p", "h1", "h2", "h3"])
        for p in paragraphs:
            txt = p.get_text(separator=" ", strip=True)
            if len(txt) > 30:
                body_texts.append(txt)

    # Strategy 2: common news CMS content selectors
    if not body_texts:
        for selector in [
            {"class": re.compile(r"article|content|story|post|entry|body", re.I)},
            {"class": re.compile(r"ArticleBody|articleBody|article-body|story-body", re.I)},
            {"id": re.compile(r"article|content|story|main-content", re.I)},
        ]:
            container = soup.find(attrs=selector)
            if container:
                for p in container.find_all(["p", "h2", "h3"]):
                    txt = p.get_text(separator=" ", strip=True)
                    if len(txt) > 30:
                        body_texts.append(txt)
                if body_texts:
                    break

    # Strategy 3: fallback — all <p> tags on the page
    if not body_texts:
        for p in soup.find_all("p"):
            txt = p.get_text(separator=" ", strip=True)
            if len(txt) > 40:
                body_texts.append(txt)

    # Limit to first 4000 characters of text to avoid noise
    combined = "\n\n".join(body_texts)
    return combined[:4000] if len(combined) > 4000 else combined


def _extract_title(soup: BeautifulSoup) -> str:
    """Extracts headline from og:title, page title, or h1 in priority order."""
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return og_title["content"].strip()

    twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
    if twitter_title and twitter_title.get("content"):
        return twitter_title["content"].strip()

    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    if soup.title and soup.title.string:
        return soup.title.string.strip()

    return ""


def _extract_date(soup: BeautifulSoup) -> str:
    """Extracts publication date from meta tags or <time> element."""
    for meta_args in [
        {"property": "article:published_time"},
        {"property": "og:published_time"},
        {"name": "publication_date"},
        {"name": "date"},
        {"name": "DC.date.issued"},
        {"itemprop": "datePublished"},
    ]:
        meta = soup.find("meta", attrs=meta_args)
        if meta:
            return meta.get("content", "").strip()

    time_el = soup.find("time", attrs={"datetime": True})
    if time_el:
        return time_el.get("datetime", "").strip()

    return ""


def fetch_article_from_url(url: str) -> dict:
    """
    Safely downloads and extracts article title, text, domain, and publication date.
    
    Security enforcements:
      - SSRF-safe: blocks private IPs, loopback, link-local, reserved networks
      - Response streamed and capped at 8MB
      - Redirect destination re-validated
      - Timeout enforced
    """
    is_safe, reason = is_safe_url(url)
    if not is_safe:
        return {
            "success": False,
            "error": reason,
            "title": "", "text": "", "domain": "", "publish_date": "", "url": url
        }

    parsed = urlparse(url)
    domain = parsed.netloc

    try:
        with requests.get(
            url,
            headers=BROWSER_HEADERS,
            timeout=REQUEST_TIMEOUT_SECONDS,
            stream=True,
            allow_redirects=True
        ) as response:
            # Re-validate after redirect
            if response.url != url:
                final_safe, final_reason = is_safe_url(response.url)
                if not final_safe:
                    return {
                        "success": False,
                        "error": f"Redirect to unsafe destination blocked: {final_reason}",
                        "title": "", "text": "", "domain": domain, "publish_date": "", "url": url
                    }

            if response.status_code == 403:
                return {
                    "success": False,
                    "error": (
                        "The website denied access (HTTP 403 Forbidden). "
                        "This typically means the site has anti-bot protection or a paywall. "
                        "Try copying the article text manually and pasting it in the Text tab."
                    ),
                    "title": "", "text": "", "domain": domain, "url": url
                }

            if response.status_code == 404:
                return {
                    "success": False,
                    "error": "Article not found at this URL (HTTP 404 Not Found). The link may be broken or outdated.",
                    "title": "", "text": "", "domain": domain, "url": url
                }

            if response.status_code not in (200, 201):
                return {
                    "success": False,
                    "error": f"Website responded with HTTP status {response.status_code}. Cannot retrieve article.",
                    "title": "", "text": "", "domain": domain, "url": url
                }

            # Stream with 8MB hard cap
            content_chunks = []
            total_bytes = 0
            for chunk in response.iter_content(chunk_size=32768):
                if not chunk:
                    continue
                total_bytes += len(chunk)
                content_chunks.append(chunk)
                if total_bytes >= MAX_RESPONSE_BYTES:
                    # Don't abort — process what we have so far
                    break

            raw_html = b"".join(content_chunks)

        # Parse HTML
        soup = BeautifulSoup(raw_html, "html.parser")

        title = _extract_title(soup)
        publish_date = _extract_date(soup)
        full_text = _extract_text_from_soup(soup)

        if not full_text.strip():
            return {
                "success": False,
                "error": (
                    "No readable article text could be extracted from this page. "
                    "The page may require JavaScript rendering, a login, or the text is embedded in images. "
                    "Try copying the article text manually and pasting it into the Text tab."
                ),
                "title": title,
                "text": "",
                "domain": domain,
                "publish_date": publish_date,
                "url": url
            }

        return {
            "success": True,
            "title": title,
            "text": full_text,
            "domain": domain,
            "publish_date": publish_date,
            "url": url,
            "verification_note": (
                "An HTTPS connection only confirms encrypted communication with this domain. "
                "It does NOT guarantee the truthfulness or credibility of the publisher."
            )
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": f"Request timed out after {REQUEST_TIMEOUT_SECONDS} seconds. The server may be slow or offline.",
            "title": "", "text": "", "domain": domain, "url": url
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Could not connect to the website. Check your internet connection or the URL.",
            "title": "", "text": "", "domain": domain, "url": url
        }
    except requests.exceptions.RequestException as exc:
        return {
            "success": False,
            "error": f"Failed to fetch article: {str(exc)}",
            "title": "", "text": "", "domain": domain, "url": url
        }
    except Exception as exc:
        return {
            "success": False,
            "error": f"Unexpected error while parsing article: {str(exc)}",
            "title": "", "text": "", "domain": domain, "url": url
        }
