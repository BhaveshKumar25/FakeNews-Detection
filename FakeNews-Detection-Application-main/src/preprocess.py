"""Text preprocessing module for Fake News Detection."""
import os
import re
import sys
import nltk
from nltk.corpus import stopwords

# Standard fallback stopwords list if NLTK corpus cannot be downloaded offline
FALLBACK_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

# Ensure NLTK data directory exists and is cross-platform
if sys.platform.startswith("win"):
    NLTK_DATA = os.path.join(os.environ.get("APPDATA", "C:\\"), "nltk_data")
else:
    NLTK_DATA = "/tmp/nltk_data"

if os.path.exists(NLTK_DATA):
    nltk.data.path.append(NLTK_DATA)

try:
    stop_words = set(stopwords.words("english"))
except (LookupError, Exception):
    try:
        nltk.download("stopwords", download_dir=NLTK_DATA, quiet=True)
        stop_words = set(stopwords.words("english"))
    except Exception:
        stop_words = FALLBACK_STOPWORDS


def clean_text(text):
    """
    Cleans input text by lowercasing, removing URLs, HTML tags,
    non-alphabetic characters, and English stopwords.
    Preserves exact preprocessing used during model training.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    words = [word for word in text.split() if word not in stop_words]

    return " ".join(words)
