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
    ("Trasferimenti", "\U0001F504", "#9E9E9E"),  # Arrows circle
    ("Finanziamenti", "\U0001F4B3", "#E53935"),  # Credit card - loans/financing
    ("Risparmi Automatici", "\U0001F416", "#10B981"),  # Piggy bank - Revolut roundups
    ("Intrattenimento", "\U0001F3AC", "#9C27B0"),  # Clapper board - entertainment
    ("Regali", "\U0001F381", "#E91E63"),          # Gift - presents
    ("Contanti", "\U0001F4B5", "#9CA3AF"),        # Cash - v7.0 cash expenses
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

-- User profile and financial preferences
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    income_type TEXT NOT NULL DEFAULT 'employed',
    monthly_net_income REAL,
    risk_tolerance TEXT DEFAULT 'moderate',
    financial_knowledge TEXT DEFAULT 'beginner',
    coaching_style TEXT DEFAULT 'guided',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Individual debt tracking
CREATE TABLE IF NOT EXISTS debts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'personal_loan',
    original_amount REAL NOT NULL,
    current_balance REAL NOT NULL,
    interest_rate REAL,
    monthly_payment REAL,
    payment_day INTEGER,
    start_date DATE,
    expected_end_date DATE,
    is_active INTEGER DEFAULT 1,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Financial goals
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    target_amount REAL NOT NULL,
    current_amount REAL DEFAULT 0,
    priority INTEGER DEFAULT 1,
    status TEXT DEFAULT 'active',
    target_date DATE,
    monthly_contribution REAL,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- AI-generated insights and alerts
CREATE TABLE IF NOT EXISTS insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    category TEXT,
    severity TEXT DEFAULT 'info',
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    action_text TEXT,
    data_json TEXT,
    is_read INTEGER DEFAULT 0,
    is_dismissed INTEGER DEFAULT 0,
    expires_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Monthly KPI history for trend tracking
CREATE TABLE IF NOT EXISTS kpi_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL UNIQUE,
    net_worth REAL,
    total_debt REAL,
    total_assets REAL,
    savings_rate REAL,
    dti_ratio REAL,
    emergency_fund_months REAL,
    total_income REAL,
    total_expenses REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- AI coach chat history
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    tokens_used INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MoneyMind v4.0 - New Tables for Directive Assistant
-- ============================================================================

-- User decisions with impact tracking (Pillar 2)
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_date DATE NOT NULL,
    type TEXT NOT NULL,  -- 'taglio_spesa', 'aumento_rata', 'cambio_fornitore', 'cancella_abbonamento', 'nuovo_budget'
    category_id INTEGER,
    debt_id INTEGER,
    recurring_expense_id INTEGER,
    amount REAL,
    description TEXT,
    status TEXT DEFAULT 'pending',  -- 'pending', 'accepted', 'rejected', 'postponed', 'completed'
    expected_impact_monthly REAL,  -- Expected monthly savings in EUR
    expected_impact_payoff_days INTEGER,  -- Days earlier to debt freedom
    actual_impact_monthly REAL,
    actual_impact_verified INTEGER DEFAULT 0,
    verification_date DATE,
    verification_notes TEXT,
    insight_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (debt_id) REFERENCES debts(id),
    FOREIGN KEY (insight_id) REFERENCES insights(id)
);

-- Monthly debt payment plans (Pillar 1)
CREATE TABLE IF NOT EXISTS debt_monthly_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL,
    debt_id INTEGER NOT NULL,
    planned_payment REAL NOT NULL,
    extra_payment REAL DEFAULT 0,
    actual_payment REAL,
    order_in_strategy INTEGER,  -- 1 = first to pay off (highest priority)
    strategy_type TEXT DEFAULT 'avalanche',  -- 'avalanche' or 'snowball'
    projected_payoff_date DATE,
    status TEXT DEFAULT 'planned',  -- 'planned', 'on_track', 'behind', 'ahead', 'completed'
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (debt_id) REFERENCES debts(id),
    UNIQUE(month, debt_id)
);

-- Detected recurring expenses (Pillar 3)
CREATE TABLE IF NOT EXISTS recurring_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL,  -- e.g., "Netflix", "HERA Gas", "Agos Prestito"
    category_id INTEGER NOT NULL,
    frequency TEXT NOT NULL,  -- 'monthly', 'quarterly', 'annual'
    avg_amount REAL,
    min_amount REAL,
    max_amount REAL,
    last_amount REAL,
    trend_percent REAL,  -- % change over last 6 months
    first_occurrence DATE,
    last_occurrence DATE,
    occurrence_count INTEGER DEFAULT 0,
    provider TEXT,  -- Extracted provider name
    is_essential INTEGER DEFAULT 0,  -- 1 = necessary expense
    is_active INTEGER DEFAULT 1,
    optimization_status TEXT DEFAULT 'not_reviewed',  -- 'not_reviewed', 'reviewed', 'optimized', 'canceled', 'kept'
    optimization_suggestion TEXT,  -- AI-generated suggestion
    estimated_savings_monthly REAL,
    confidence_score REAL,  -- 0.0-1.0 pattern detection confidence
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Link transactions to recurring expense patterns
CREATE TABLE IF NOT EXISTS transaction_recurring_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT NOT NULL,
    recurring_expense_id INTEGER NOT NULL,
    match_confidence REAL,  -- 0.0-1.0 confidence this transaction matches pattern
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (recurring_expense_id) REFERENCES recurring_expenses(id),
    UNIQUE(transaction_id, recurring_expense_id)
);

-- Daily action tasks (Full Auto generation)
CREATE TABLE IF NOT EXISTS daily_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_date DATE NOT NULL,
    priority INTEGER DEFAULT 1,  -- 1 = highest priority
    title TEXT NOT NULL,
    description TEXT,
    action_type TEXT,  -- 'review_subscription', 'increase_payment', 'cut_category', 'confirm_budget', 'check_anomaly'
    impact_type TEXT,  -- 'savings', 'payoff_acceleration', 'budget_control'
    estimated_impact_monthly REAL,  -- EUR saved per month
    estimated_impact_payoff_days INTEGER,  -- Days closer to debt freedom
    status TEXT DEFAULT 'pending',  -- 'pending', 'completed', 'dismissed', 'snoozed'
    completed_at DATETIME,
    snoozed_until DATE,
    decision_id INTEGER,
    insight_id INTEGER,
    recurring_expense_id INTEGER,
    debt_id INTEGER,
    category_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (decision_id) REFERENCES decisions(id),
    FOREIGN KEY (insight_id) REFERENCES insights(id),
    FOREIGN KEY (recurring_expense_id) REFERENCES recurring_expenses(id),
    FOREIGN KEY (debt_id) REFERENCES debts(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Baseline snapshots for comparison (3-month rolling averages)
CREATE TABLE IF NOT EXISTS baseline_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_month TEXT NOT NULL,
    category_id INTEGER,  -- NULL for overall metrics
    metric_type TEXT NOT NULL,  -- 'spending', 'income', 'savings', 'payoff_projection'
    avg_value_3mo REAL,  -- 3-month rolling average
    calculation_start_month TEXT,
    calculation_end_month TEXT,
    projected_payoff_date DATE,  -- For payoff_projection type
    projected_payoff_months INTEGER,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(snapshot_month, category_id, metric_type)
);

-- ============================================================================
-- Indexes for v4.0 tables
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id);
CREATE INDEX IF NOT EXISTS idx_transactions_bank ON transactions(bank);
CREATE INDEX IF NOT EXISTS idx_budgets_month ON budgets(month);
CREATE INDEX IF NOT EXISTS idx_debts_active ON debts(is_active);
CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);
CREATE INDEX IF NOT EXISTS idx_insights_read ON insights(is_read, is_dismissed);
CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(type);
CREATE INDEX IF NOT EXISTS idx_kpi_history_month ON kpi_history(month);
CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id);

-- v4.0 indexes
CREATE INDEX IF NOT EXISTS idx_decisions_status ON decisions(status);
CREATE INDEX IF NOT EXISTS idx_decisions_date ON decisions(decision_date);
CREATE INDEX IF NOT EXISTS idx_decisions_type ON decisions(type);
CREATE INDEX IF NOT EXISTS idx_debt_plans_month ON debt_monthly_plans(month);
CREATE INDEX IF NOT EXISTS idx_debt_plans_debt ON debt_monthly_plans(debt_id);
CREATE INDEX IF NOT EXISTS idx_recurring_active ON recurring_expenses(is_active);
CREATE INDEX IF NOT EXISTS idx_recurring_category ON recurring_expenses(category_id);
CREATE INDEX IF NOT EXISTS idx_recurring_provider ON recurring_expenses(provider);
CREATE INDEX IF NOT EXISTS idx_tx_recurring_tx ON transaction_recurring_links(transaction_id);
CREATE INDEX IF NOT EXISTS idx_tx_recurring_recurring ON transaction_recurring_links(recurring_expense_id);
CREATE INDEX IF NOT EXISTS idx_daily_actions_date ON daily_actions(action_date);
CREATE INDEX IF NOT EXISTS idx_daily_actions_status ON daily_actions(status);
CREATE INDEX IF NOT EXISTS idx_baseline_month ON baseline_snapshots(snapshot_month);
CREATE INDEX IF NOT EXISTS idx_baseline_type ON baseline_snapshots(metric_type);

-- ============================================================================
-- MoneyMind v6.0 - Desktop Personal Finance Coach Tables
-- ============================================================================

-- Onboarding Profile (Fase Diagnosi)
CREATE TABLE IF NOT EXISTS onboarding_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    financial_freedom_goal TEXT,          -- 'debt_free', 'fire', 'wealth_building'
    primary_pain_point TEXT,              -- Problema principale da risolvere
    target_monthly_savings REAL,          -- Target risparmio mensile
    risk_tolerance TEXT,                  -- 'conservative', 'moderate', 'aggressive'
    preferred_pace TEXT,                  -- 'slow_steady', 'aggressive', 'flexible'
    fire_target_age INTEGER,              -- Eta target per FIRE
    monthly_essential_expenses REAL,      -- Spese essenziali stimate
    onboarding_completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Goal Milestones (Fase Crescita)
CREATE TABLE IF NOT EXISTS goal_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL,
    milestone_number INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    target_amount REAL,
    target_date DATE,
    status TEXT DEFAULT 'pending',        -- 'pending', 'achieved', 'missed'
    achieved_at DATETIME,
    actual_amount REAL,
    celebration_shown INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES goals(id)
);

-- FIRE Projections
CREATE TABLE IF NOT EXISTS fire_projections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projection_date DATE NOT NULL,
    scenario_name TEXT,                   -- 'conservative', 'expected', 'optimistic'
    fire_number REAL,                     -- 25x annual expenses
    years_to_fire REAL,
    projected_fire_date DATE,
    annual_expenses REAL,
    expected_return_rate REAL,
    inflation_rate REAL,
    current_net_worth REAL,
    monthly_investment REAL,
    confidence_score REAL,                -- 0-1 based on data quality
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- What-If Scenarios
CREATE TABLE IF NOT EXISTS scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    scenario_type TEXT,                   -- 'income_change', 'expense_cut', 'debt_payoff', 'custom'
    base_values TEXT,                     -- JSON: original values
    modified_values TEXT,                 -- JSON: scenario changes
    impact_summary TEXT,                  -- JSON: calculated impact
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Coaching Events (Proactive)
CREATE TABLE IF NOT EXISTS coaching_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,             -- 'nudge', 'celebration', 'alert', 'milestone'
    title TEXT NOT NULL,
    message TEXT,
    priority TEXT DEFAULT 'medium',       -- 'low', 'medium', 'high', 'critical'
    trigger_condition TEXT,               -- What triggered this event
    action_url TEXT,                      -- Deep link to action
    is_shown INTEGER DEFAULT 0,
    shown_at DATETIME,
    is_dismissed INTEGER DEFAULT 0,
    dismissed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- User Streaks (Gamification)
CREATE TABLE IF NOT EXISTS user_streaks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    streak_type TEXT NOT NULL,            -- 'daily_check', 'budget_adherence', 'savings_goal'
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    streak_started_at DATE,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- v6.0 indexes
CREATE INDEX IF NOT EXISTS idx_onboarding_goal ON onboarding_profile(financial_freedom_goal);
CREATE INDEX IF NOT EXISTS idx_goal_milestones_goal ON goal_milestones(goal_id);
CREATE INDEX IF NOT EXISTS idx_goal_milestones_status ON goal_milestones(status);
CREATE INDEX IF NOT EXISTS idx_fire_projections_date ON fire_projections(projection_date);
CREATE INDEX IF NOT EXISTS idx_fire_projections_scenario ON fire_projections(scenario_name);
CREATE INDEX IF NOT EXISTS idx_scenarios_type ON scenarios(scenario_type);
CREATE INDEX IF NOT EXISTS idx_scenarios_active ON scenarios(is_active);
CREATE INDEX IF NOT EXISTS idx_coaching_events_type ON coaching_events(event_type);
CREATE INDEX IF NOT EXISTS idx_coaching_events_shown ON coaching_events(is_shown, is_dismissed);
CREATE INDEX IF NOT EXISTS idx_user_streaks_type ON user_streaks(streak_type);
"""


def get_connection() -> sqlite3.Connection:
    """
    Returns a database connection with row_factory set for dict-like access.

    Returns:
        sqlite3.Connection: Database connection object
    """
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
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


# ============================================================================
# User Profile Functions
# ============================================================================

def get_user_profile() -> Optional[dict]:
    """Get the user profile (singleton - only one profile)."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profile ORDER BY id LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None


def save_user_profile(profile: dict) -> int:
    """Create or update user profile."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        existing = get_user_profile()

        if existing:
            cursor.execute(
                """
                UPDATE user_profile SET
                    income_type = ?,
                    monthly_net_income = ?,
                    risk_tolerance = ?,
                    financial_knowledge = ?,
                    coaching_style = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    profile.get("income_type", "employed"),
                    profile.get("monthly_net_income"),
                    profile.get("risk_tolerance", "moderate"),
                    profile.get("financial_knowledge", "beginner"),
                    profile.get("coaching_style", "guided"),
                    existing["id"]
                )
            )
            return existing["id"]
        else:
            cursor.execute(
                """
                INSERT INTO user_profile
                (income_type, monthly_net_income, risk_tolerance, financial_knowledge, coaching_style)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    profile.get("income_type", "employed"),
                    profile.get("monthly_net_income"),
                    profile.get("risk_tolerance", "moderate"),
                    profile.get("financial_knowledge", "beginner"),
                    profile.get("coaching_style", "guided")
                )
            )
            return cursor.lastrowid


# ============================================================================
# Debt Functions
# ============================================================================

def get_debts(active_only: bool = True) -> list[dict]:
    """Get all debts, optionally filtering by active status."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM debts"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY interest_rate DESC, current_balance DESC"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]


def get_debt_by_id(debt_id: int) -> Optional[dict]:
    """Get a single debt by ID."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM debts WHERE id = ?", (debt_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def add_debt(debt: dict) -> int:
    """Add a new debt."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO debts
            (name, type, original_amount, current_balance, interest_rate,
             monthly_payment, payment_day, start_date, expected_end_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                debt["name"],
                debt.get("type", "personal_loan"),
                debt["original_amount"],
                debt["current_balance"],
                debt.get("interest_rate"),
                debt.get("monthly_payment"),
                debt.get("payment_day"),
                debt.get("start_date"),
                debt.get("expected_end_date"),
                debt.get("notes")
            )
        )
        return cursor.lastrowid


def update_debt(debt_id: int, updates: dict) -> bool:
    """Update a debt record."""
    with get_db_context() as conn:
        cursor = conn.cursor()

        # Build dynamic update query
        set_clauses = []
        values = []
        for key, value in updates.items():
            if key not in ("id", "created_at"):
                set_clauses.append(f"{key} = ?")
                values.append(value)

        if not set_clauses:
            return False

        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(debt_id)

        cursor.execute(
            f"UPDATE debts SET {', '.join(set_clauses)} WHERE id = ?",
            values
        )
        return cursor.rowcount > 0


def delete_debt(debt_id: int) -> bool:
    """Delete a debt (or mark as inactive)."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE debts SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (debt_id,)
        )
        return cursor.rowcount > 0


def get_total_debt() -> float:
    """Get total current debt balance."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(current_balance), 0) as total FROM debts WHERE is_active = 1"
        )
        return cursor.fetchone()["total"]


# ============================================================================
# Goals Functions
# ============================================================================

def get_goals(status: str = None) -> list[dict]:
    """Get all goals, optionally filtering by status."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM goals"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY priority ASC, created_at ASC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_goal_by_id(goal_id: int) -> Optional[dict]:
    """Get a single goal by ID."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def add_goal(goal: dict) -> int:
    """Add a new financial goal."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO goals
            (name, type, target_amount, current_amount, priority, status,
             target_date, monthly_contribution, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                goal["name"],
                goal["type"],
                goal["target_amount"],
                goal.get("current_amount", 0),
                goal.get("priority", 1),
                goal.get("status", "active"),
                goal.get("target_date"),
                goal.get("monthly_contribution"),
                goal.get("notes")
            )
        )
        return cursor.lastrowid


def update_goal(goal_id: int, updates: dict) -> bool:
    """Update a goal record."""
    with get_db_context() as conn:
        cursor = conn.cursor()

        set_clauses = []
        values = []
        for key, value in updates.items():
            if key not in ("id", "created_at"):
                set_clauses.append(f"{key} = ?")
                values.append(value)

        if not set_clauses:
            return False

        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(goal_id)

        cursor.execute(
            f"UPDATE goals SET {', '.join(set_clauses)} WHERE id = ?",
            values
        )
        return cursor.rowcount > 0


def delete_goal(goal_id: int) -> bool:
    """Delete a goal."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        return cursor.rowcount > 0


# ============================================================================
# Insights Functions
# ============================================================================

def get_insights(unread_only: bool = False, limit: int = 50) -> list[dict]:
    """Get insights/alerts, optionally filtering to unread only."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        query = """
            SELECT * FROM insights
            WHERE is_dismissed = 0
            AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        """
        if unread_only:
            query += " AND is_read = 0"
        query += " ORDER BY created_at DESC LIMIT ?"
        cursor.execute(query, (limit,))
        return [dict(row) for row in cursor.fetchall()]


def add_insight(insight: dict) -> int:
    """Add a new insight/alert."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO insights
            (type, category, severity, title, message, action_text, data_json, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                insight["type"],
                insight.get("category"),
                insight.get("severity", "info"),
                insight["title"],
                insight["message"],
                insight.get("action_text"),
                insight.get("data_json"),
                insight.get("expires_at")
            )
        )
        return cursor.lastrowid


def mark_insight_read(insight_id: int) -> bool:
    """Mark an insight as read."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE insights SET is_read = 1 WHERE id = ?",
            (insight_id,)
        )
        return cursor.rowcount > 0


def dismiss_insight(insight_id: int) -> bool:
    """Dismiss an insight."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE insights SET is_dismissed = 1 WHERE id = ?",
            (insight_id,)
        )
        return cursor.rowcount > 0


def get_unread_insight_count() -> int:
    """Get count of unread insights."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) as count FROM insights
            WHERE is_read = 0 AND is_dismissed = 0
            AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
            """
        )
        return cursor.fetchone()["count"]


# ============================================================================
# KPI History Functions
# ============================================================================

def save_kpi_snapshot(month: str, kpis: dict) -> int:
    """Save a monthly KPI snapshot."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO kpi_history
            (month, net_worth, total_debt, total_assets, savings_rate,
             dti_ratio, emergency_fund_months, total_income, total_expenses)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(month) DO UPDATE SET
                net_worth = excluded.net_worth,
                total_debt = excluded.total_debt,
                total_assets = excluded.total_assets,
                savings_rate = excluded.savings_rate,
                dti_ratio = excluded.dti_ratio,
                emergency_fund_months = excluded.emergency_fund_months,
                total_income = excluded.total_income,
                total_expenses = excluded.total_expenses
            """,
            (
                month,
                kpis.get("net_worth"),
                kpis.get("total_debt"),
                kpis.get("total_assets"),
                kpis.get("savings_rate"),
                kpis.get("dti_ratio"),
                kpis.get("emergency_fund_months"),
                kpis.get("total_income"),
                kpis.get("total_expenses")
            )
        )
        return cursor.lastrowid


def get_kpi_history(months: int = 12) -> list[dict]:
    """Get KPI history for the last N months."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM kpi_history
            ORDER BY month DESC
            LIMIT ?
            """,
            (months,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_kpi_for_month(month: str) -> Optional[dict]:
    """Get KPI snapshot for a specific month."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kpi_history WHERE month = ?", (month,))
        row = cursor.fetchone()
        return dict(row) if row else None


# ============================================================================
# Chat History Functions
# ============================================================================

def add_chat_message(session_id: str, role: str, content: str, tokens: int = None) -> int:
    """Add a chat message to history."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO chat_history (session_id, role, content, tokens_used)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, role, content, tokens)
        )
        return cursor.lastrowid


def get_chat_history(session_id: str, limit: int = 50) -> list[dict]:
    """Get chat history for a session."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM chat_history
            WHERE session_id = ?
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (session_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_chat_sessions(limit: int = 20) -> list[dict]:
    """Get list of chat sessions with latest message preview."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                session_id,
                MIN(created_at) as started_at,
                MAX(created_at) as last_message_at,
                COUNT(*) as message_count
            FROM chat_history
            GROUP BY session_id
            ORDER BY last_message_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]


def delete_chat_session(session_id: str) -> bool:
    """Delete all messages in a chat session."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
        return cursor.rowcount > 0


# ============================================================================
# MoneyMind v4.0 - Decision Functions
# ============================================================================

def add_decision(decision: dict) -> int:
    """Add a new decision record."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO decisions
            (decision_date, type, category_id, debt_id, recurring_expense_id,
             amount, description, status, expected_impact_monthly,
             expected_impact_payoff_days, insight_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision["decision_date"],
                decision["type"],
                decision.get("category_id"),
                decision.get("debt_id"),
                decision.get("recurring_expense_id"),
                decision.get("amount"),
                decision.get("description"),
                decision.get("status", "pending"),
                decision.get("expected_impact_monthly"),
                decision.get("expected_impact_payoff_days"),
                decision.get("insight_id")
            )
        )
        return cursor.lastrowid


def update_decision(decision_id: int, updates: dict) -> bool:
    """Update a decision record."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        set_clauses = []
        values = []
        for key, value in updates.items():
            if key not in ("id", "created_at"):
                set_clauses.append(f"{key} = ?")
                values.append(value)
        if not set_clauses:
            return False
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(decision_id)
        cursor.execute(
            f"UPDATE decisions SET {', '.join(set_clauses)} WHERE id = ?",
            values
        )
        return cursor.rowcount > 0


def get_decisions(status: str = None, limit: int = 50) -> list[dict]:
    """Get decisions, optionally filtered by status."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM decisions WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY decision_date DESC LIMIT ?"
        params.append(limit)
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_pending_decisions() -> list[dict]:
    """Get all pending decisions."""
    return get_decisions(status="pending")


def get_decision_by_id(decision_id: int) -> Optional[dict]:
    """Get a single decision by ID."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def verify_decision_impact(decision_id: int, actual_impact: float, notes: str = None) -> bool:
    """Mark a decision as verified with actual impact."""
    return update_decision(decision_id, {
        "actual_impact_monthly": actual_impact,
        "actual_impact_verified": 1,
        "verification_date": datetime.now().strftime("%Y-%m-%d"),
        "verification_notes": notes
    })


# ============================================================================
# MoneyMind v4.0 - Debt Monthly Plan Functions
# ============================================================================

def create_debt_monthly_plan(plan: dict) -> int:
    """Create or update a monthly debt payment plan."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO debt_monthly_plans
            (month, debt_id, planned_payment, extra_payment, order_in_strategy,
             strategy_type, projected_payoff_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(month, debt_id) DO UPDATE SET
                planned_payment = excluded.planned_payment,
                extra_payment = excluded.extra_payment,
                order_in_strategy = excluded.order_in_strategy,
                strategy_type = excluded.strategy_type,
                projected_payoff_date = excluded.projected_payoff_date,
                status = excluded.status,
                notes = excluded.notes,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                plan["month"],
                plan["debt_id"],
                plan["planned_payment"],
                plan.get("extra_payment", 0),
                plan.get("order_in_strategy"),
                plan.get("strategy_type", "avalanche"),
                plan.get("projected_payoff_date"),
                plan.get("status", "planned"),
                plan.get("notes")
            )
        )
        return cursor.lastrowid


def get_debt_plans_for_month(month: str) -> list[dict]:
    """Get all debt payment plans for a specific month."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT dmp.*, d.name as debt_name, d.current_balance, d.interest_rate
            FROM debt_monthly_plans dmp
            JOIN debts d ON dmp.debt_id = d.id
            WHERE dmp.month = ?
            ORDER BY dmp.order_in_strategy ASC
            """,
            (month,)
        )
        return [dict(row) for row in cursor.fetchall()]


def update_plan_actual_payment(month: str, debt_id: int, actual_payment: float) -> bool:
    """Update actual payment for a debt plan."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE debt_monthly_plans
            SET actual_payment = ?, updated_at = CURRENT_TIMESTAMP
            WHERE month = ? AND debt_id = ?
            """,
            (actual_payment, month, debt_id)
        )
        return cursor.rowcount > 0


def update_plan_status(month: str, debt_id: int, status: str) -> bool:
    """Update status of a debt plan (on_track, behind, ahead, completed)."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE debt_monthly_plans
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE month = ? AND debt_id = ?
            """,
            (status, month, debt_id)
        )
        return cursor.rowcount > 0


def get_debt_plan_history(debt_id: int, months: int = 12) -> list[dict]:
    """Get payment plan history for a specific debt."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM debt_monthly_plans
            WHERE debt_id = ?
            ORDER BY month DESC
            LIMIT ?
            """,
            (debt_id, months)
        )
        return [dict(row) for row in cursor.fetchall()]


# ============================================================================
# MoneyMind v4.0 - Recurring Expense Functions
# ============================================================================

def add_recurring_expense(recurring: dict) -> int:
    """Add a new recurring expense pattern."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO recurring_expenses
            (pattern_name, category_id, frequency, avg_amount, min_amount, max_amount,
             last_amount, trend_percent, first_occurrence, last_occurrence,
             occurrence_count, provider, is_essential, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                recurring["pattern_name"],
                recurring["category_id"],
                recurring["frequency"],
                recurring.get("avg_amount"),
                recurring.get("min_amount"),
                recurring.get("max_amount"),
                recurring.get("last_amount"),
                recurring.get("trend_percent"),
                recurring.get("first_occurrence"),
                recurring.get("last_occurrence"),
                recurring.get("occurrence_count", 0),
                recurring.get("provider"),
                recurring.get("is_essential", 0),
                recurring.get("confidence_score")
            )
        )
        return cursor.lastrowid


def update_recurring_expense(recurring_id: int, updates: dict) -> bool:
    """Update a recurring expense record."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        set_clauses = []
        values = []
        for key, value in updates.items():
            if key not in ("id", "created_at"):
                set_clauses.append(f"{key} = ?")
                values.append(value)
        if not set_clauses:
            return False
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(recurring_id)
        cursor.execute(
            f"UPDATE recurring_expenses SET {', '.join(set_clauses)} WHERE id = ?",
            values
        )
        return cursor.rowcount > 0


def get_recurring_expenses(active_only: bool = True, category_id: int = None) -> list[dict]:
    """Get recurring expenses with optional filters."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        query = """
            SELECT re.*, c.name as category_name, c.icon as category_icon
            FROM recurring_expenses re
            JOIN categories c ON re.category_id = c.id
            WHERE 1=1
        """
        params = []
        if active_only:
            query += " AND re.is_active = 1"
        if category_id:
            query += " AND re.category_id = ?"
            params.append(category_id)
        query += " ORDER BY re.avg_amount DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_recurring_expense_by_id(recurring_id: int) -> Optional[dict]:
    """Get a single recurring expense by ID."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT re.*, c.name as category_name, c.icon as category_icon
            FROM recurring_expenses re
            JOIN categories c ON re.category_id = c.id
            WHERE re.id = ?
            """,
            (recurring_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def set_recurring_optimization(recurring_id: int, status: str,
                                suggestion: str = None, savings: float = None) -> bool:
    """Set optimization status and suggestion for a recurring expense."""
    updates = {"optimization_status": status}
    if suggestion:
        updates["optimization_suggestion"] = suggestion
    if savings is not None:
        updates["estimated_savings_monthly"] = savings
    return update_recurring_expense(recurring_id, updates)


def link_transaction_to_recurring(transaction_id: str, recurring_id: int,
                                   confidence: float = 1.0) -> bool:
    """Link a transaction to a recurring expense pattern."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO transaction_recurring_links
                (transaction_id, recurring_expense_id, match_confidence)
                VALUES (?, ?, ?)
                """,
                (transaction_id, recurring_id, confidence)
            )
            return True
        except Exception:
            return False


def get_transactions_for_recurring(recurring_id: int, limit: int = 20) -> list[dict]:
    """Get transactions linked to a recurring expense."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT t.*, trl.match_confidence
            FROM transactions t
            JOIN transaction_recurring_links trl ON t.id = trl.transaction_id
            WHERE trl.recurring_expense_id = ?
            ORDER BY t.date DESC
            LIMIT ?
            """,
            (recurring_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_recurring_summary() -> dict:
    """Get summary of recurring expenses by category type."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                c.name as category_name,
                COUNT(re.id) as count,
                SUM(re.avg_amount) as total_monthly,
                SUM(CASE WHEN re.is_essential = 1 THEN re.avg_amount ELSE 0 END) as essential_monthly,
                SUM(CASE WHEN re.is_essential = 0 THEN re.avg_amount ELSE 0 END) as non_essential_monthly
            FROM recurring_expenses re
            JOIN categories c ON re.category_id = c.id
            WHERE re.is_active = 1
            GROUP BY c.name
            ORDER BY total_monthly DESC
            """
        )
        categories = [dict(row) for row in cursor.fetchall()]

        total = sum(c["total_monthly"] or 0 for c in categories)
        essential = sum(c["essential_monthly"] or 0 for c in categories)

        return {
            "total_monthly": total,
            "essential_monthly": essential,
            "non_essential_monthly": total - essential,
            "by_category": categories
        }


# ============================================================================
# MoneyMind v4.0 - Daily Actions Functions
# ============================================================================

def create_daily_action(action: dict) -> int:
    """Create a new daily action task."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO daily_actions
            (action_date, priority, title, description, action_type, impact_type,
             estimated_impact_monthly, estimated_impact_payoff_days, status,
             decision_id, insight_id, recurring_expense_id, debt_id, category_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                action["action_date"],
                action.get("priority", 1),
                action["title"],
                action.get("description"),
                action.get("action_type"),
                action.get("impact_type"),
                action.get("estimated_impact_monthly"),
                action.get("estimated_impact_payoff_days"),
                action.get("status", "pending"),
                action.get("decision_id"),
                action.get("insight_id"),
                action.get("recurring_expense_id"),
                action.get("debt_id"),
                action.get("category_id")
            )
        )
        return cursor.lastrowid


def get_today_actions(date: str = None) -> list[dict]:
    """Get pending actions for today (or specified date)."""
    if date is None:
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT da.*, c.name as category_name, d.name as debt_name,
                   re.pattern_name as recurring_name
            FROM daily_actions da
            LEFT JOIN categories c ON da.category_id = c.id
            LEFT JOIN debts d ON da.debt_id = d.id
            LEFT JOIN recurring_expenses re ON da.recurring_expense_id = re.id
            WHERE da.action_date = ?
            AND da.status = 'pending'
            ORDER BY da.priority ASC
            LIMIT 3
            """,
            (date,)
        )
        return [dict(row) for row in cursor.fetchall()]


def complete_daily_action(action_id: int, decision_id: int = None) -> bool:
    """Mark a daily action as completed."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE daily_actions
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP, decision_id = ?
            WHERE id = ?
            """,
            (decision_id, action_id)
        )
        return cursor.rowcount > 0


def dismiss_daily_action(action_id: int) -> bool:
    """Dismiss a daily action (user chose not to act)."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE daily_actions SET status = 'dismissed' WHERE id = ?",
            (action_id,)
        )
        return cursor.rowcount > 0


def snooze_daily_action(action_id: int, snooze_until: str) -> bool:
    """Snooze a daily action until a future date."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE daily_actions
            SET status = 'snoozed', snoozed_until = ?
            WHERE id = ?
            """,
            (snooze_until, action_id)
        )
        return cursor.rowcount > 0


def get_pending_action_count(date: str = None) -> int:
    """Get count of pending actions for badge display."""
    if date is None:
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) as count FROM daily_actions
            WHERE action_date <= ? AND status = 'pending'
            """,
            (date,)
        )
        return cursor.fetchone()["count"]


def get_action_history(days: int = 30) -> list[dict]:
    """Get action history for tracking completion rates."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                action_date,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'dismissed' THEN 1 ELSE 0 END) as dismissed
            FROM daily_actions
            WHERE action_date >= date('now', ? || ' days')
            GROUP BY action_date
            ORDER BY action_date DESC
            """,
            (f"-{days}",)
        )
        return [dict(row) for row in cursor.fetchall()]


# ============================================================================
# MoneyMind v4.0 - Baseline Snapshot Functions
# ============================================================================

def save_baseline_snapshot(snapshot: dict) -> int:
    """Save or update a baseline snapshot."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO baseline_snapshots
            (snapshot_month, category_id, metric_type, avg_value_3mo,
             calculation_start_month, calculation_end_month,
             projected_payoff_date, projected_payoff_months, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(snapshot_month, category_id, metric_type) DO UPDATE SET
                avg_value_3mo = excluded.avg_value_3mo,
                calculation_start_month = excluded.calculation_start_month,
                calculation_end_month = excluded.calculation_end_month,
                projected_payoff_date = excluded.projected_payoff_date,
                projected_payoff_months = excluded.projected_payoff_months,
                notes = excluded.notes
            """,
            (
                snapshot["snapshot_month"],
                snapshot.get("category_id"),
                snapshot["metric_type"],
                snapshot.get("avg_value_3mo"),
                snapshot.get("calculation_start_month"),
                snapshot.get("calculation_end_month"),
                snapshot.get("projected_payoff_date"),
                snapshot.get("projected_payoff_months"),
                snapshot.get("notes")
            )
        )
        return cursor.lastrowid


def get_baseline_for_month(month: str, metric_type: str = None) -> list[dict]:
    """Get baseline snapshots for a month."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        query = """
            SELECT bs.*, c.name as category_name
            FROM baseline_snapshots bs
            LEFT JOIN categories c ON bs.category_id = c.id
            WHERE bs.snapshot_month = ?
        """
        params = [month]
        if metric_type:
            query += " AND bs.metric_type = ?"
            params.append(metric_type)
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_overall_baseline(month: str) -> Optional[dict]:
    """Get overall baseline metrics (not category-specific)."""
    baselines = get_baseline_for_month(month)
    result = {}
    for b in baselines:
        if b.get("category_id") is None:
            result[b["metric_type"]] = {
                "avg_value_3mo": b["avg_value_3mo"],
                "projected_payoff_date": b.get("projected_payoff_date"),
                "projected_payoff_months": b.get("projected_payoff_months")
            }
    return result if result else None


def compare_to_baseline(current_month: str, baseline_month: str) -> dict:
    """Compare current month metrics to baseline."""
    current = get_baseline_for_month(current_month)
    baseline = get_baseline_for_month(baseline_month)

    if not baseline:
        return {"error": "No baseline data available"}

    baseline_by_key = {
        (b.get("category_id"), b["metric_type"]): b
        for b in baseline
    }

    comparisons = []
    for c in current:
        key = (c.get("category_id"), c["metric_type"])
        b = baseline_by_key.get(key)
        if b and b["avg_value_3mo"] and c["avg_value_3mo"]:
            delta = c["avg_value_3mo"] - b["avg_value_3mo"]
            delta_percent = (delta / b["avg_value_3mo"]) * 100 if b["avg_value_3mo"] != 0 else 0
            comparisons.append({
                "metric_type": c["metric_type"],
                "category_name": c.get("category_name"),
                "current": c["avg_value_3mo"],
                "baseline": b["avg_value_3mo"],
                "delta": delta,
                "delta_percent": delta_percent,
                "improved": delta < 0 if c["metric_type"] == "spending" else delta > 0
            })

    return {"comparisons": comparisons}


# Import datetime at module level for functions that need it
from datetime import datetime


# ============================================================================
# MoneyMind v6.0 - Onboarding Profile Functions
# ============================================================================

def get_onboarding_profile() -> Optional[dict]:
    """Get the onboarding profile (singleton)."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM onboarding_profile ORDER BY id LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None


def save_onboarding_profile(profile: dict) -> int:
    """Create or update onboarding profile."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        existing = get_onboarding_profile()

        if existing:
            cursor.execute(
                """
                UPDATE onboarding_profile SET
                    financial_freedom_goal = ?,
                    primary_pain_point = ?,
                    target_monthly_savings = ?,
                    risk_tolerance = ?,
                    preferred_pace = ?,
                    fire_target_age = ?,
                    monthly_essential_expenses = ?,
                    onboarding_completed_at = ?
                WHERE id = ?
                """,
                (
                    profile.get("financial_freedom_goal"),
                    profile.get("primary_pain_point"),
                    profile.get("target_monthly_savings"),
                    profile.get("risk_tolerance"),
                    profile.get("preferred_pace"),
                    profile.get("fire_target_age"),
                    profile.get("monthly_essential_expenses"),
                    profile.get("onboarding_completed_at"),
                    existing["id"]
                )
            )
            return existing["id"]
        else:
            cursor.execute(
                """
                INSERT INTO onboarding_profile
                (financial_freedom_goal, primary_pain_point, target_monthly_savings,
                 risk_tolerance, preferred_pace, fire_target_age,
                 monthly_essential_expenses, onboarding_completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.get("financial_freedom_goal"),
                    profile.get("primary_pain_point"),
                    profile.get("target_monthly_savings"),
                    profile.get("risk_tolerance"),
                    profile.get("preferred_pace"),
                    profile.get("fire_target_age"),
                    profile.get("monthly_essential_expenses"),
                    profile.get("onboarding_completed_at")
                )
            )
            return cursor.lastrowid


def complete_onboarding() -> bool:
    """Mark onboarding as complete."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE onboarding_profile
            SET onboarding_completed_at = CURRENT_TIMESTAMP
            WHERE id = (SELECT id FROM onboarding_profile LIMIT 1)
            """
        )
        return cursor.rowcount > 0


def is_onboarding_complete() -> bool:
    """Check if onboarding is complete."""
    profile = get_onboarding_profile()
    return profile is not None and profile.get("onboarding_completed_at") is not None


# ============================================================================
# MoneyMind v6.0 - Goal Milestones Functions
# ============================================================================

def add_milestone(milestone: dict) -> int:
    """Add a milestone to a goal."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO goal_milestones
            (goal_id, milestone_number, title, description, target_amount,
             target_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                milestone["goal_id"],
                milestone.get("milestone_number", 1),
                milestone["title"],
                milestone.get("description"),
                milestone.get("target_amount"),
                milestone.get("target_date"),
                milestone.get("status", "pending")
            )
        )
        return cursor.lastrowid


def get_milestones_for_goal(goal_id: int) -> list[dict]:
    """Get all milestones for a goal."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM goal_milestones
            WHERE goal_id = ?
            ORDER BY milestone_number ASC
            """,
            (goal_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def achieve_milestone(milestone_id: int, actual_amount: float = None) -> bool:
    """Mark a milestone as achieved."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE goal_milestones
            SET status = 'achieved', achieved_at = CURRENT_TIMESTAMP, actual_amount = ?
            WHERE id = ?
            """,
            (actual_amount, milestone_id)
        )
        return cursor.rowcount > 0


def mark_milestone_celebration_shown(milestone_id: int) -> bool:
    """Mark that celebration was shown for a milestone."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE goal_milestones SET celebration_shown = 1 WHERE id = ?",
            (milestone_id,)
        )
        return cursor.rowcount > 0


def get_pending_celebrations() -> list[dict]:
    """Get milestones achieved but not celebrated."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT gm.*, g.name as goal_name
            FROM goal_milestones gm
            JOIN goals g ON gm.goal_id = g.id
            WHERE gm.status = 'achieved' AND gm.celebration_shown = 0
            ORDER BY gm.achieved_at DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]


# ============================================================================
# MoneyMind v6.0 - FIRE Projections Functions
# ============================================================================

def save_fire_projection(projection: dict) -> int:
    """Save a FIRE projection."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO fire_projections
            (projection_date, scenario_name, fire_number, years_to_fire,
             projected_fire_date, annual_expenses, expected_return_rate,
             inflation_rate, current_net_worth, monthly_investment, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                projection["projection_date"],
                projection.get("scenario_name", "expected"),
                projection.get("fire_number"),
                projection.get("years_to_fire"),
                projection.get("projected_fire_date"),
                projection.get("annual_expenses"),
                projection.get("expected_return_rate"),
                projection.get("inflation_rate"),
                projection.get("current_net_worth"),
                projection.get("monthly_investment"),
                projection.get("confidence_score")
            )
        )
        return cursor.lastrowid


def get_latest_fire_projection(scenario: str = "expected") -> Optional[dict]:
    """Get the most recent FIRE projection for a scenario."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM fire_projections
            WHERE scenario_name = ?
            ORDER BY projection_date DESC
            LIMIT 1
            """,
            (scenario,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_fire_projection_history(months: int = 12) -> list[dict]:
    """Get FIRE projection history for trending."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM fire_projections
            WHERE scenario_name = 'expected'
            ORDER BY projection_date DESC
            LIMIT ?
            """,
            (months,)
        )
        return [dict(row) for row in cursor.fetchall()]


# ============================================================================
# MoneyMind v6.0 - Scenarios Functions
# ============================================================================

def save_scenario(scenario: dict) -> int:
    """Save a what-if scenario."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO scenarios
            (name, description, scenario_type, base_values, modified_values, impact_summary)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                scenario["name"],
                scenario.get("description"),
                scenario.get("scenario_type"),
                scenario.get("base_values"),  # JSON string
                scenario.get("modified_values"),  # JSON string
                scenario.get("impact_summary")  # JSON string
            )
        )
        return cursor.lastrowid


def get_scenarios(active_only: bool = True) -> list[dict]:
    """Get all scenarios."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM scenarios"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY created_at DESC"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]


def get_scenario_by_id(scenario_id: int) -> Optional[dict]:
    """Get a scenario by ID."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scenarios WHERE id = ?", (scenario_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def deactivate_scenario(scenario_id: int) -> bool:
    """Deactivate a scenario."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE scenarios SET is_active = 0 WHERE id = ?", (scenario_id,))
        return cursor.rowcount > 0


# ============================================================================
# MoneyMind v6.0 - Coaching Events Functions
# ============================================================================

def create_coaching_event(event: dict) -> int:
    """Create a coaching event (nudge, celebration, alert)."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO coaching_events
            (event_type, title, message, priority, trigger_condition, action_url)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event["event_type"],
                event["title"],
                event.get("message"),
                event.get("priority", "medium"),
                event.get("trigger_condition"),
                event.get("action_url")
            )
        )
        return cursor.lastrowid


def get_active_coaching_events(event_type: str = None) -> list[dict]:
    """Get active (not shown or dismissed) coaching events."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        query = """
            SELECT * FROM coaching_events
            WHERE is_shown = 0 AND is_dismissed = 0
        """
        params = []
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        query += " ORDER BY CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END, created_at DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_nudges() -> list[dict]:
    """Get active nudges."""
    return get_active_coaching_events("nudge")


def get_celebrations() -> list[dict]:
    """Get pending celebrations."""
    return get_active_coaching_events("celebration")


def mark_event_shown(event_id: int) -> bool:
    """Mark a coaching event as shown."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE coaching_events
            SET is_shown = 1, shown_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (event_id,)
        )
        return cursor.rowcount > 0


def dismiss_coaching_event(event_id: int) -> bool:
    """Dismiss a coaching event."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE coaching_events
            SET is_dismissed = 1, dismissed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (event_id,)
        )
        return cursor.rowcount > 0


# ============================================================================
# MoneyMind v6.0 - User Streaks Functions
# ============================================================================

def get_or_create_streak(streak_type: str) -> dict:
    """Get or create a streak record."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM user_streaks WHERE streak_type = ?",
            (streak_type,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)

        # Create new streak
        cursor.execute(
            """
            INSERT INTO user_streaks (streak_type, current_streak, longest_streak)
            VALUES (?, 0, 0)
            """,
            (streak_type,)
        )
        return {
            "id": cursor.lastrowid,
            "streak_type": streak_type,
            "current_streak": 0,
            "longest_streak": 0,
            "last_activity_date": None,
            "streak_started_at": None
        }


def update_streak(streak_type: str) -> dict:
    """Update a streak (call when user performs the tracked action)."""
    streak = get_or_create_streak(streak_type)
    today = datetime.now().strftime("%Y-%m-%d")
    last_activity = streak.get("last_activity_date")

    with get_db_context() as conn:
        cursor = conn.cursor()

        if last_activity == today:
            # Already updated today
            return streak
        elif last_activity == (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"):
            # Consecutive day - increment streak
            new_streak = streak["current_streak"] + 1
            longest = max(new_streak, streak["longest_streak"])
            cursor.execute(
                """
                UPDATE user_streaks
                SET current_streak = ?, longest_streak = ?, last_activity_date = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE streak_type = ?
                """,
                (new_streak, longest, today, streak_type)
            )
        else:
            # Streak broken - restart
            cursor.execute(
                """
                UPDATE user_streaks
                SET current_streak = 1, last_activity_date = ?, streak_started_at = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE streak_type = ?
                """,
                (today, today, streak_type)
            )

    return get_or_create_streak(streak_type)


def get_all_streaks() -> list[dict]:
    """Get all user streaks."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_streaks ORDER BY current_streak DESC")
        return [dict(row) for row in cursor.fetchall()]


# ============================================================================
# MoneyMind v6.0 - Schema Migration Functions
# ============================================================================

def run_migrations() -> None:
    """Run any pending schema migrations for v6.0 and v7.0."""
    with get_db_context() as conn:
        cursor = conn.cursor()

        # Check if columns exist before adding them
        # This is safe for SQLite - it will raise an error if column exists
        migrations = [
            # user_profile extensions for FIRE
            ("user_profile", "fire_target_date", "DATE"),
            ("user_profile", "fire_target_amount", "REAL"),
            ("user_profile", "preferred_investment_return", "REAL DEFAULT 0.07"),
            ("user_profile", "preferred_inflation_rate", "REAL DEFAULT 0.02"),

            # goals extensions for phases
            ("goals", "phase", "TEXT"),
            ("goals", "milestone_count", "INTEGER DEFAULT 0"),
            ("goals", "next_milestone_id", "INTEGER"),

            # decisions extensions for tracking
            ("decisions", "source", "TEXT"),
            ("decisions", "user_confidence", "INTEGER"),
            ("decisions", "long_term_verified", "INTEGER DEFAULT 0"),
            ("decisions", "verified_at", "DATETIME"),

            # ============================================================================
            # v7.0 - Data Quality Improvements
            # ============================================================================

            # transactions - expense classification
            ("transactions", "expense_type", "TEXT DEFAULT 'variable'"),  # 'fixed', 'variable', 'one_time'
            ("transactions", "is_internal_transfer", "INTEGER DEFAULT 0"),
            ("transactions", "categorization_method", "TEXT"),  # 'RULE', 'AI', 'MANUAL'
            ("transactions", "categorization_confidence", "REAL DEFAULT 1.0"),

            # recurring_expenses - type classification
            ("recurring_expenses", "recurring_type", "TEXT DEFAULT 'subscription'"),  # 'subscription', 'financing', 'essential', 'service'
            ("recurring_expenses", "cancellability", "TEXT DEFAULT 'easy'"),  # 'easy', 'medium', 'hard', 'locked'
            ("recurring_expenses", "contract_end_date", "DATE"),
            ("recurring_expenses", "auto_detected", "INTEGER DEFAULT 0"),
        ]

        for table, column, column_type in migrations:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
            except Exception:
                # Column already exists, skip
                pass

        # Seed new category if not exists
        cursor.execute(
            "INSERT OR IGNORE INTO categories (name, icon, color) VALUES (?, ?, ?)",
            ("Contanti", "\U0001F4B5", "#9CA3AF")
        )


# Import timedelta for streak calculations
from datetime import timedelta


# Initialize database when module is imported (optional - can be called explicitly)
if __name__ == "__main__":
    init_db()
    run_migrations()
    print(f"Database initialized at: {DB_PATH}")
    print(f"Categories: {len(get_categories())}")
