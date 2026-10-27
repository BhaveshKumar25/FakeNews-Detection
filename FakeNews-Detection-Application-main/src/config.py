"""Application configuration module."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")

# Model configuration
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "fake_news_model.pkl"))
DATASET_PATH = os.getenv("DATASET_PATH", str(BASE_DIR / "news_dataset.csv"))

# Database configuration
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "feedback.db"))

# Uncertainty threshold: if max probability is below this threshold, warn user
# Default is 0.65 (65% confidence)
UNCERTAINTY_THRESHOLD = float(os.getenv("UNCERTAINTY_THRESHOLD", "0.65"))

# Fact Check API
FACT_CHECK_API_KEY = os.getenv("FACT_CHECK_API_KEY", os.getenv("GOOGLE_FACTCHECK_API_KEY", ""))

# OCR Configuration
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "")

# Request constraints
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "6"))
MAX_ARTICLE_CHARS = int(os.getenv("MAX_ARTICLE_CHARS", "15000"))
MAX_UPLOAD_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(5 * 1024 * 1024)))  # 5 MB
MAX_URL_RESPONSE_BYTES = int(os.getenv("MAX_URL_RESPONSE_BYTES", str(2 * 1024 * 1024)))  # 2 MB
