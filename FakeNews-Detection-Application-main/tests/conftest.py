"""Pytest configuration and shared fixtures."""
import os
import sys
import tempfile
import pytest

# Ensure application package is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Switch working directory to project directory so relative paths work
os.chdir(BASE_DIR)

from app import app
from src import database


@pytest.fixture(scope="session")
def test_client():
    """Provides a Flask test client configured for testing."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def isolated_db(monkeypatch, tmp_path):
    """Isolates feedback database for each test in a temporary file."""
    temp_db = tmp_path / "test_feedback.db"
    monkeypatch.setattr(database, "DATABASE_PATH", str(temp_db))
    database.init_db()
    yield temp_db
