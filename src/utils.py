"""Utility functions for MoneyMind."""

import hashlib
from datetime import datetime
from typing import Union


def generate_transaction_id(date: Union[datetime, str], amount: float, description: str, bank: str) -> str:
    """Generate unique hash for transaction deduplication."""
    if isinstance(date, datetime):
        date_str = date.strftime("%Y-%m-%d")
    else:
        date_str = str(date)

    raw = f"{date_str}|{amount}|{description}|{bank}"
    return hashlib.sha256(raw.encode()).hexdigest()


def format_currency(amount: float) -> str:
    """Format amount as EUR currency."""
    sign = "+" if amount >= 0 else ""
    return f"{sign}€{amount:,.2f}".replace(",", " ").replace(".", ",")


def get_month_range(year: int, month: int) -> tuple:
    """Get start and end date for a month."""
    from calendar import monthrange

    start = datetime(year, month, 1)
    _, last_day = monthrange(year, month)
    end = datetime(year, month, last_day)

    return start, end
