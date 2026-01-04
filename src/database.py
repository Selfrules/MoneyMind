"""
MoneyMind Database Module

SQLite database management for financial transactions, categories, and budgets.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager


# Database path relative to this module's location
# data/moneymind.db relative to project root (moneymind/)
MODULE_DIR = Path(__file__).parent  # src/
PROJECT_DIR = MODULE_DIR.parent     # moneymind/
DATA_DIR = PROJECT_DIR / "data"
DB_PATH = DATA_DIR / "moneymind.db"


# Default categories with icons and colors
DEFAULT_CATEGORIES = [
    ("Stipendio", "\U0001F4B0", "#4CAF50"),      # Money bag
    ("Affitto", "\U0001F3E0", "#FF5722"),        # House
    ("Utenze", "\U0001F4A1", "#FFC107"),         # Light bulb
    ("Spesa", "\U0001F6D2", "#8BC34A"),          # Shopping cart
    ("Ristoranti", "\U0001F355", "#E91E63"),     # Pizza
    ("Trasporti", "\U0001F697", "#00BCD4"),      # Car
    ("Salute", "\U0001F48A", "#F44336"),         # Pill
    ("Palestra", "\U0001F3CB\uFE0F", "#9C27B0"), # Weight lifter
    ("Abbonamenti", "\U0001F4F1", "#673AB7"),    # Mobile phone
    ("Shopping", "\U0001F6CD\uFE0F", "#3F51B5"), # Shopping bags
    ("Psicologo", "\U0001F9E0", "#009688"),      # Brain
    ("Gatti", "\U0001F431", "#FF9800"),          # Cat face
    ("Viaggi", "\u2708\uFE0F", "#2196F3"),       # Airplane
    ("Caffe", "\u2615", "#795548"),              # Coffee
    ("Barbiere", "\U0001F488", "#607D8B"),       # Barber pole
    ("Trasferimenti", "\U0001F504", "#9E9E9E"), # Arrows circle
    ("Altro", "\U0001F4E6", "#757575"),          # Package
]


# SQL Schema
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    icon TEXT,
    color TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    date DATE NOT NULL,
    description TEXT,
    amount REAL NOT NULL,
    category_id INTEGER,
    bank TEXT NOT NULL,
    account_type TEXT,
    type TEXT,
    balance REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    month TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    UNIQUE(category_id, month)
);

CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id);
CREATE INDEX IF NOT EXISTS idx_transactions_bank ON transactions(bank);
CREATE INDEX IF NOT EXISTS idx_budgets_month ON budgets(month);
"""


def get_connection() -> sqlite3.Connection:
    """
    Returns a database connection with row_factory set for dict-like access.

    Returns:
        sqlite3.Connection: Database connection object
    """
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db_context():
    """
    Context manager for database connections with automatic commit/rollback.

    Yields:
        sqlite3.Connection: Database connection object
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """
    Initialize the database by creating tables and seeding default categories.

    Creates the categories, transactions, and budgets tables if they don't exist,
    then seeds the default categories.
    """
    with get_db_context() as conn:
        cursor = conn.cursor()

        # Create tables
        cursor.executescript(SCHEMA_SQL)

        # Seed categories (INSERT OR IGNORE to avoid duplicates)
        cursor.executemany(
            "INSERT OR IGNORE INTO categories (name, icon, color) VALUES (?, ?, ?)",
            DEFAULT_CATEGORIES
        )


def get_categories() -> list[dict]:
    """
    Returns all categories from the database.

    Returns:
        list[dict]: List of category dictionaries with id, name, icon, color
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, icon, color FROM categories ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]


def get_category_by_name(name: str) -> Optional[dict]:
    """
    Returns a category by its name.

    Args:
        name: Category name to search for

    Returns:
        dict or None: Category dictionary if found, None otherwise
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, icon, color FROM categories WHERE name = ?",
            (name,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def insert_transaction(tx_dict: dict) -> str:
    """
    Insert a single transaction into the database.

    Args:
        tx_dict: Dictionary with transaction data:
            - id (str): Unique transaction ID
            - date (str): Transaction date (YYYY-MM-DD)
            - description (str): Transaction description
            - amount (float): Transaction amount
            - category_id (int, optional): Category ID
            - bank (str): Bank name
            - account_type (str, optional): Account type
            - type (str, optional): Transaction type
            - balance (float, optional): Balance after transaction

    Returns:
        str: The transaction ID
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO transactions
            (id, date, description, amount, category_id, bank, account_type, type, balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tx_dict["id"],
                tx_dict["date"],
                tx_dict.get("description"),
                tx_dict["amount"],
                tx_dict.get("category_id"),
                tx_dict["bank"],
                tx_dict.get("account_type"),
                tx_dict.get("type"),
                tx_dict.get("balance"),
            )
        )
        return tx_dict["id"]


def insert_transactions(tx_list: list[dict]) -> int:
    """
    Bulk insert transactions into the database.

    Args:
        tx_list: List of transaction dictionaries (see insert_transaction for format)

    Returns:
        int: Number of transactions inserted
    """
    if not tx_list:
        return 0

    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO transactions
            (id, date, description, amount, category_id, bank, account_type, type, balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    tx["id"],
                    tx["date"],
                    tx.get("description"),
                    tx["amount"],
                    tx.get("category_id"),
                    tx["bank"],
                    tx.get("account_type"),
                    tx.get("type"),
                    tx.get("balance"),
                )
                for tx in tx_list
            ]
        )
        return len(tx_list)


def get_transactions(
    filters: Optional[dict] = None
) -> list[dict]:
    """
    Get transactions with optional filters.

    Args:
        filters: Optional dictionary with filter criteria:
            - start_date (str): Start date (YYYY-MM-DD)
            - end_date (str): End date (YYYY-MM-DD)
            - category_id (int): Category ID
            - category (str): Category name
            - bank (str): Bank name
            - type (str): Transaction type

    Returns:
        list[dict]: List of transaction dictionaries with category info joined
    """
    query = """
        SELECT
            t.id, t.date, t.description, t.amount, t.category_id,
            t.bank, t.account_type, t.type, t.balance, t.created_at,
            c.name as category_name, c.icon as category_icon, c.color as category_color
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE 1=1
    """
    params = []

    if filters:
        if "start_date" in filters:
            query += " AND t.date >= ?"
            params.append(filters["start_date"])

        if "end_date" in filters:
            query += " AND t.date <= ?"
            params.append(filters["end_date"])

        if "category_id" in filters:
            query += " AND t.category_id = ?"
            params.append(filters["category_id"])

        if "category" in filters:
            query += " AND c.name = ?"
            params.append(filters["category"])

        if "bank" in filters:
            query += " AND t.bank = ?"
            params.append(filters["bank"])

        if "type" in filters:
            query += " AND t.type = ?"
            params.append(filters["type"])

        if "month" in filters:
            query += " AND strftime('%Y-%m', t.date) = ?"
            params.append(filters["month"])

    query += " ORDER BY t.date DESC, t.created_at DESC"

    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def update_transaction_category(tx_id: str, category_id: int) -> bool:
    """
    Update the category of a transaction.

    Args:
        tx_id: Transaction ID
        category_id: New category ID

    Returns:
        bool: True if transaction was updated, False if not found
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE transactions SET category_id = ? WHERE id = ?",
            (category_id, tx_id)
        )
        return cursor.rowcount > 0


def get_budgets(month: str) -> list[dict]:
    """
    Get all budgets for a specific month.

    Args:
        month: Month in YYYY-MM format

    Returns:
        list[dict]: List of budget dictionaries with category info
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                b.id, b.category_id, b.amount, b.month,
                c.name as category_name, c.icon as category_icon, c.color as category_color
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            WHERE b.month = ?
            ORDER BY c.name
            """,
            (month,)
        )
        return [dict(row) for row in cursor.fetchall()]


def set_budget(category_id: int, amount: float, month: str) -> int:
    """
    Set or update a budget for a category and month.

    Args:
        category_id: Category ID
        amount: Budget amount
        month: Month in YYYY-MM format

    Returns:
        int: Budget ID
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO budgets (category_id, amount, month)
            VALUES (?, ?, ?)
            ON CONFLICT(category_id, month) DO UPDATE SET amount = excluded.amount
            """,
            (category_id, amount, month)
        )
        return cursor.lastrowid


def get_spending_by_category(month: str) -> list[dict]:
    """
    Get aggregate spending by category for a specific month.

    Only includes expenses (negative amounts).

    Args:
        month: Month in YYYY-MM format (e.g., "2024-01")

    Returns:
        list[dict]: List with category info and total spending
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                c.id as category_id,
                c.name as category_name,
                c.icon as category_icon,
                c.color as category_color,
                COALESCE(SUM(ABS(t.amount)), 0) as total_spent,
                COUNT(t.id) as transaction_count
            FROM categories c
            LEFT JOIN transactions t ON c.id = t.category_id
                AND strftime('%Y-%m', t.date) = ?
                AND t.amount < 0
            GROUP BY c.id, c.name, c.icon, c.color
            HAVING total_spent > 0 OR c.id IS NOT NULL
            ORDER BY total_spent DESC
            """,
            (month,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_latest_balances() -> list[dict]:
    """
    Get the most recent balance for each bank.

    Returns:
        list[dict]: List with bank name, balance, date, and account_type
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                bank,
                account_type,
                balance,
                date
            FROM transactions t1
            WHERE date = (
                SELECT MAX(t2.date)
                FROM transactions t2
                WHERE t2.bank = t1.bank
                AND t2.balance IS NOT NULL
            )
            AND balance IS NOT NULL
            GROUP BY bank
            ORDER BY bank
            """
        )
        return [dict(row) for row in cursor.fetchall()]


def delete_transaction(tx_id: str) -> bool:
    """
    Delete a transaction by ID.

    Args:
        tx_id: Transaction ID to delete

    Returns:
        bool: True if deleted, False if not found
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        return cursor.rowcount > 0


def get_transaction_by_id(tx_id: str) -> Optional[dict]:
    """
    Get a single transaction by ID.

    Args:
        tx_id: Transaction ID

    Returns:
        dict or None: Transaction dictionary if found
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                t.id, t.date, t.description, t.amount, t.category_id,
                t.bank, t.account_type, t.type, t.balance, t.created_at,
                c.name as category_name, c.icon as category_icon, c.color as category_color
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.id = ?
            """,
            (tx_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_monthly_summary(month: str) -> dict:
    """
    Get a summary of income and expenses for a month.

    Args:
        month: Month in YYYY-MM format

    Returns:
        dict: Summary with total_income, total_expenses, net, transaction_count
    """
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) as total_income,
                COALESCE(SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END), 0) as total_expenses,
                COALESCE(SUM(amount), 0) as net,
                COUNT(*) as transaction_count
            FROM transactions
            WHERE strftime('%Y-%m', date) = ?
            """,
            (month,)
        )
        row = cursor.fetchone()
        return dict(row) if row else {
            "total_income": 0,
            "total_expenses": 0,
            "net": 0,
            "transaction_count": 0
        }


# Initialize database when module is imported (optional - can be called explicitly)
if __name__ == "__main__":
    init_db()
    print(f"Database initialized at: {DB_PATH}")
    print(f"Categories: {len(get_categories())}")
