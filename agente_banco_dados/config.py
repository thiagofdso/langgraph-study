"""Configuration constants for the SQLite sales agent."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "sales.db"

MIN_SEED_PRODUCTS = 5
MIN_SEED_SELLERS = 3
MIN_SEED_SALES = 20

TOP_N_PRODUCTS = 3
TOP_N_SELLERS = 3

DEFAULT_MODEL_ID = "gemini-2.5-flash"
