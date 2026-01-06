"""
API Dependencies for dependency injection.
"""
import sys
from pathlib import Path
from typing import Generator
import sqlite3

# Add src directory to path for importing existing modules
BACKEND_DIR = Path(__file__).parent.parent.parent  # backend/
PROJECT_DIR = BACKEND_DIR.parent  # MoneyMind/
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

# Import existing database module
from database import get_db_context, get_connection


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    FastAPI dependency for database connection.
    Uses existing database module's connection management.
    """
    with get_db_context() as conn:
        yield conn
