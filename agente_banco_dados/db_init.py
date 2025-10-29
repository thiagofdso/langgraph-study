"""SQLite database initialization for the sales agent."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from .config import DATA_DIR, DB_PATH, MIN_SEED_PRODUCTS, MIN_SEED_SELLERS, MIN_SEED_SALES

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT,
    unit_price REAL NOT NULL CHECK(unit_price >= 0)
);

CREATE TABLE IF NOT EXISTS sellers (
    seller_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    region TEXT
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_code TEXT NOT NULL UNIQUE,
    product_id INTEGER NOT NULL,
    seller_id INTEGER NOT NULL,
    sale_date TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price REAL NOT NULL CHECK(unit_price >= 0),
    FOREIGN KEY(product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
    FOREIGN KEY(seller_id) REFERENCES sellers(seller_id) ON DELETE RESTRICT
);
"""

PRODUCT_SEED: list[tuple[str, str, str | None, float]] = [
    ("P-100", "Laptop Essentials", "Electronics", 2500.00),
    ("P-200", "Noise-Cancelling Headphones", "Electronics", 890.00),
    ("P-300", "Ergonomic Chair", "Office", 1290.00),
    ("P-400", "Standing Desk", "Office", 1890.00),
    ("P-500", "Smart Monitor", "Electronics", 1590.00),
    ("P-600", "Conference Speaker", "Accessories", 420.00),
]

SELLER_SEED: list[tuple[str, str, str | None]] = [
    ("S-100", "Alice Alves", "São Paulo"),
    ("S-200", "Bruno Batista", "Rio de Janeiro"),
    ("S-300", "Carla Costa", "Minas Gerais"),
    ("S-400", "Daniela Dias", "Paraná"),
]

SALE_SEED: list[tuple[str, str, str, int, float]] = [
    ("ORD-001", "P-100", "S-100", "2025-01-05", 4, 2500.00),
    ("ORD-002", "P-200", "S-100", "2025-01-06", 8, 890.00),
    ("ORD-003", "P-300", "S-200", "2025-01-08", 3, 1290.00),
    ("ORD-004", "P-400", "S-200", "2025-01-09", 2, 1890.00),
    ("ORD-005", "P-500", "S-300", "2025-01-10", 6, 1590.00),
    ("ORD-006", "P-600", "S-300", "2025-01-11", 10, 420.00),
    ("ORD-007", "P-100", "S-200", "2025-01-12", 2, 2500.00),
    ("ORD-008", "P-200", "S-300", "2025-01-12", 5, 890.00),
    ("ORD-009", "P-300", "S-100", "2025-01-13", 4, 1290.00),
    ("ORD-010", "P-400", "S-100", "2025-01-14", 3, 1890.00),
    ("ORD-011", "P-500", "S-200", "2025-01-15", 7, 1590.00),
    ("ORD-012", "P-600", "S-100", "2025-01-16", 9, 420.00),
    ("ORD-013", "P-100", "S-300", "2025-01-17", 5, 2500.00),
    ("ORD-014", "P-200", "S-400", "2025-01-18", 6, 890.00),
    ("ORD-015", "P-300", "S-400", "2025-01-19", 4, 1290.00),
    ("ORD-016", "P-400", "S-300", "2025-01-20", 3, 1890.00),
    ("ORD-017", "P-500", "S-400", "2025-01-21", 5, 1590.00),
    ("ORD-018", "P-600", "S-200", "2025-01-22", 8, 420.00),
    ("ORD-019", "P-100", "S-400", "2025-01-23", 6, 2500.00),
    ("ORD-020", "P-500", "S-100", "2025-01-24", 4, 1590.00),
    ("ORD-021", "P-600", "S-400", "2025-01-25", 7, 420.00),
    ("ORD-022", "P-200", "S-300", "2025-01-26", 9, 890.00),
    ("ORD-023", "P-300", "S-200", "2025-01-26", 5, 1290.00),
    ("ORD-024", "P-400", "S-100", "2025-01-27", 4, 1890.00),
]


def ensure_data_directory() -> None:
    """Create the data directory if it does not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row factory enabled."""
    ensure_data_directory()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def apply_schema(connection: sqlite3.Connection) -> None:
    """Create tables if they are missing."""
    connection.executescript(SCHEMA_SQL)


def seed_products(connection: sqlite3.Connection) -> None:
    """Insert the default products."""
    connection.executemany(
        """
        INSERT OR IGNORE INTO products (sku, name, category, unit_price)
        VALUES (?, ?, ?, ?)
        """,
        PRODUCT_SEED,
    )


def seed_sellers(connection: sqlite3.Connection) -> None:
    """Insert the default sellers."""
    connection.executemany(
        """
        INSERT OR IGNORE INTO sellers (code, name, region)
        VALUES (?, ?, ?)
        """,
        SELLER_SEED,
    )


def seed_sales(connection: sqlite3.Connection) -> None:
    """Insert the default sales rows using existing product and seller ids."""
    product_id_by_sku = {
        row["sku"]: row["product_id"]
        for row in connection.execute("SELECT product_id, sku FROM products")
    }
    seller_id_by_code = {
        row["code"]: row["seller_id"]
        for row in connection.execute("SELECT seller_id, code FROM sellers")
    }

    records: Iterable[tuple[int, int, str, int, float, str]] = (
        (
            product_id_by_sku[sale[1]],
            seller_id_by_code[sale[2]],
            sale[3],
            sale[4],
            sale[5],
            sale[0],
        )
        for sale in SALE_SEED
    )

    connection.executemany(
        """
        INSERT OR IGNORE INTO sales (
            product_id,
            seller_id,
            sale_date,
            quantity,
            unit_price,
            order_code
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        records,
    )


def get_row_counts(connection: sqlite3.Connection) -> dict[str, int]:
    """Return a summary of row counts per table."""
    cursor = connection.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM products) AS products,
            (SELECT COUNT(*) FROM sellers) AS sellers,
            (SELECT COUNT(*) FROM sales) AS sales
        """
    )
    row = cursor.fetchone()
    return {"products": row["products"], "sellers": row["sellers"], "sales": row["sales"]}


def validate_seed_counts(counts: dict[str, int]) -> None:
    """Raise an error if minimum seed counts are not met."""
    if counts["products"] < MIN_SEED_PRODUCTS:
        raise RuntimeError("Seeded product count below required minimum.")
    if counts["sellers"] < MIN_SEED_SELLERS:
        raise RuntimeError("Seeded seller count below required minimum.")
    if counts["sales"] < MIN_SEED_SALES:
        raise RuntimeError("Seeded sales count below required minimum.")


def initialize_database() -> dict[str, int]:
    """Create the database schema and seed sample data."""
    with get_connection() as connection:
        apply_schema(connection)
        seed_products(connection)
        seed_sellers(connection)
        seed_sales(connection)
        connection.commit()
        counts = get_row_counts(connection)
    validate_seed_counts(counts)
    return counts

