"""Persistent SQLite database module for user feedback."""
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from src.config import DATABASE_PATH

# Simple in-memory tracker for rate limiting: IP/client identifier -> list of timestamps
_RATE_LIMIT_STORE: dict[str, list[float]] = {}
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_SUBMISSIONS = 8


def get_db_connection():
    """Returns a SQLite connection with row factory enabled."""
    db_path = Path(DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the feedback table schema."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                comment TEXT,
                prediction TEXT,
                confidence REAL,
                news_excerpt TEXT
            )
        """)
        conn.commit()


def check_rate_limit(client_id: str) -> bool:
    """
    Returns True if client is within limits, False if rate-limited.
    Sliding window rate limit.
    """
    now = time.time()
    timestamps = _RATE_LIMIT_STORE.get(client_id, [])
    # Filter timestamps within window
    timestamps = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW_SECONDS]
    if len(timestamps) >= RATE_LIMIT_MAX_SUBMISSIONS:
        _RATE_LIMIT_STORE[client_id] = timestamps
        return False
    timestamps.append(now)
    _RATE_LIMIT_STORE[client_id] = timestamps
    return True


def save_feedback(
    sentiment: str,
    comment: str = "",
    prediction: str = "",
    confidence: float = 0.0,
    news_excerpt: str = "",
    client_id: str = "unknown"
) -> dict:
    """
    Validates and stores user feedback in SQLite database.
    Does NOT collect personal data (PII).
    """
    if not check_rate_limit(client_id):
        return {
            "success": False,
            "error": "Too many feedback submissions. Please wait a moment before trying again."
        }

    valid_sentiments = {"helpful", "incorrect", "unsure"}
    clean_sentiment = (sentiment or "").strip().lower()

    if clean_sentiment not in valid_sentiments:
        return {
            "success": False,
            "error": f"Invalid feedback type '{sentiment}'. Must be 'helpful', 'incorrect', or 'unsure'."
        }

    clean_comment = (comment or "").strip()[:1000]  # Max 1000 chars
    clean_prediction = (prediction or "").strip()[:50]
    clean_excerpt = (news_excerpt or "").strip()[:200]  # Safe short excerpt

    try:
        conf_float = float(confidence)
        if not (0.0 <= conf_float <= 1.0):
            conf_float = 0.0
    except (ValueError, TypeError):
        conf_float = 0.0

    now_iso = datetime.now(timezone.utc).isoformat()

    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO feedback (created_at, sentiment, comment, prediction, confidence, news_excerpt)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (now_iso, clean_sentiment, clean_comment, clean_prediction, conf_float, clean_excerpt)
            )
            conn.commit()
            record_id = cursor.lastrowid

        return {
            "success": True,
            "id": record_id,
            "message": "Thank you! Your feedback has been recorded."
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Database storage failed: {str(e)}"
        }


def get_feedback_count() -> int:
    """Returns total number of feedback entries saved."""
    try:
        with get_db_connection() as conn:
            cur = conn.execute("SELECT COUNT(*) FROM feedback")
            return cur.fetchone()[0]
    except Exception:
        return 0
