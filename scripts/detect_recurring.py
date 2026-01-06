"""
Detect Recurring Expenses Script for MoneyMind v4.0

Analyzes transaction history to identify recurring payment patterns
and populates the recurring_expenses table.

Patterns detected:
- Subscription services (Netflix, Spotify, etc.)
- Utility bills (Hera, Enel, etc.)
- Loan payments (Agos, Findomestic, etc.)
- Other regular payments (gym, insurance, etc.)

Usage:
    python scripts/detect_recurring.py
"""

import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
import re

# Add project root to path
PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.database import (
    get_transactions,
    get_categories,
    add_recurring_expense,
    get_db_context,
)


# Provider patterns for identification
PROVIDER_PATTERNS = {
    # Streaming & Entertainment
    "netflix": ("Netflix", "Abbonamenti", True),
    "spotify": ("Spotify", "Abbonamenti", True),
    "amazon prime": ("Amazon Prime", "Abbonamenti", False),
    "disney": ("Disney+", "Abbonamenti", False),
    "audible": ("Audible", "Abbonamenti", False),
    "youtube": ("YouTube Premium", "Abbonamenti", False),
    "apple.com/bill": ("Apple Services", "Abbonamenti", False),
    "steam": ("Steam", "Abbonamenti", False),

    # Productivity & Work
    "chatgpt": ("ChatGPT Plus", "Abbonamenti", True),
    "openai": ("OpenAI", "Abbonamenti", True),
    "github": ("GitHub", "Abbonamenti", True),
    "notion": ("Notion", "Abbonamenti", False),
    "google workspace": ("Google Workspace", "Abbonamenti", True),
    "make": ("Make.com", "Abbonamenti", True),
    "linkedin": ("LinkedIn Premium", "Abbonamenti", False),
    "adobe": ("Adobe", "Abbonamenti", False),

    # Fitness & Health
    "unobravo": ("Unobravo", "Psicologo", True),
    "serenis": ("Serenis", "Psicologo", True),
    "whoop": ("Whoop", "Abbonamenti", False),
    "21 lab": ("21 Lab Palestra", "Palestra", False),
    "mcfit": ("McFit", "Palestra", False),
    "virgin active": ("Virgin Active", "Palestra", False),

    # Utilities
    "octopus": ("Octopus Energy", "Utenze", True),
    "hera": ("Hera", "Utenze", True),
    "iren": ("Iren", "Utenze", True),
    "enel": ("Enel", "Utenze", True),
    "eni plenitude": ("Eni Plenitude", "Utenze", True),
    "a2a": ("A2A", "Utenze", True),

    # Telecom
    "tim": ("TIM", "Utenze", True),
    "vodafone": ("Vodafone", "Utenze", True),
    "iliad": ("Iliad", "Utenze", True),
    "fastweb": ("Fastweb", "Utenze", True),
    "windtre": ("WindTre", "Utenze", True),

    # Finance & Banking
    "agos": ("Agos", "Finanziamenti", True),
    "findomestic": ("Findomestic", "Finanziamenti", True),
    "revolut credit": ("Revolut Credit", "Finanziamenti", True),
    "personal loan": ("Prestito Personale", "Finanziamenti", True),
    "paga in 3": ("Paga in 3", "Finanziamenti", True),
    "klarna": ("Klarna", "Finanziamenti", True),

    # Insurance
    "generali": ("Generali", "Assicurazioni", True),
    "unipol": ("UnipolSai", "Assicurazioni", True),
    "axa": ("AXA", "Assicurazioni", True),
    "allianz": ("Allianz", "Assicurazioni", True),

    # Transport
    "telepass": ("Telepass", "Trasporti", True),

    # Pets
    "arcaplanet": ("Arcaplanet", "Gatti", False),

    # Financial Services
    "nexi": ("Nexi", "Abbonamenti", True),
    "wise": ("Wise", "Abbonamenti", False),
}


def detect_frequency(dates: list) -> tuple:
    """
    Detect payment frequency from a list of dates.
    Returns (frequency, confidence_score)
    """
    if len(dates) < 2:
        return "unknown", 0.0

    dates = sorted(dates)
    intervals = []
    for i in range(1, len(dates)):
        delta = (dates[i] - dates[i-1]).days
        intervals.append(delta)

    avg_interval = sum(intervals) / len(intervals)

    # Monthly: 25-35 days
    if 25 <= avg_interval <= 35:
        variance = sum((x - avg_interval)**2 for x in intervals) / len(intervals)
        confidence = max(0.5, 1.0 - (variance / 100))
        return "monthly", confidence

    # Quarterly: 85-95 days
    elif 85 <= avg_interval <= 95:
        return "quarterly", 0.8

    # Annual: 350-380 days
    elif 350 <= avg_interval <= 380:
        return "annual", 0.7

    # Weekly: 5-9 days
    elif 5 <= avg_interval <= 9:
        return "weekly", 0.9

    else:
        return "irregular", 0.3


def identify_provider(description: str) -> tuple:
    """
    Identify provider from transaction description.
    Returns (provider_name, category_name, is_essential) or None
    """
    desc_lower = description.lower()

    for pattern, (provider, category, essential) in PROVIDER_PATTERNS.items():
        if pattern in desc_lower:
            return provider, category, essential

    return None, None, None


def group_transactions_by_pattern(transactions: list) -> dict:
    """
    Group transactions by similar descriptions to detect recurring patterns.
    """
    patterns = defaultdict(list)

    for tx in transactions:
        # Skip income and transfers
        if tx["amount"] > 0:
            continue
        if tx.get("category_name") in ["Trasferimenti", "Risparmi Automatici"]:
            continue

        desc = tx.get("description", "").strip()
        if not desc:
            continue

        # Normalize description for matching
        normalized = desc.lower()

        # Remove common prefixes/suffixes
        normalized = re.sub(r'\b(ref|rif|bonifico|pagamento|addebito)\b', '', normalized)
        normalized = re.sub(r'\d{2}/\d{2}/\d{2,4}', '', normalized)  # Remove dates
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        # Try to identify provider first
        provider, _, _ = identify_provider(desc)

        if provider:
            key = provider.lower()
        else:
            # Use first 30 chars as pattern key
            key = normalized[:30] if len(normalized) > 30 else normalized

        patterns[key].append({
            "date": tx["date"],
            "amount": abs(tx["amount"]),
            "description": desc,
            "category_id": tx.get("category_id"),
            "category_name": tx.get("category_name"),
            "category_icon": tx.get("category_icon"),
        })

    return patterns


def analyze_patterns(patterns: dict, min_occurrences: int = 2) -> list:
    """
    Analyze grouped patterns to identify recurring expenses.
    """
    recurring = []

    for pattern_key, transactions in patterns.items():
        if len(transactions) < min_occurrences:
            continue

        # Get dates
        dates = [datetime.strptime(tx["date"], "%Y-%m-%d") if isinstance(tx["date"], str) else tx["date"]
                 for tx in transactions]

        # Detect frequency
        frequency, confidence = detect_frequency(dates)

        if frequency == "unknown" or confidence < 0.4:
            continue

        # Calculate stats
        amounts = [tx["amount"] for tx in transactions]
        avg_amount = sum(amounts) / len(amounts)
        min_amount = min(amounts)
        max_amount = max(amounts)
        last_amount = transactions[-1]["amount"]

        # Calculate trend (first half vs second half)
        if len(amounts) >= 4:
            mid = len(amounts) // 2
            first_half_avg = sum(amounts[:mid]) / mid
            second_half_avg = sum(amounts[mid:]) / (len(amounts) - mid)
            if first_half_avg > 0:
                trend_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100
            else:
                trend_percent = 0
        else:
            trend_percent = 0

        # Get dates
        first_occurrence = min(dates).strftime("%Y-%m-%d")
        last_occurrence = max(dates).strftime("%Y-%m-%d")

        # Identify provider
        desc = transactions[0]["description"]
        provider, suggested_category, is_essential = identify_provider(desc)

        # Use identified category or fall back to transaction category
        category_name = suggested_category or transactions[0].get("category_name", "Altro")

        # Create pattern name
        if provider:
            pattern_name = provider
        else:
            # Capitalize and clean
            pattern_name = pattern_key.title()[:50]

        recurring.append({
            "pattern_name": pattern_name,
            "category_name": category_name,
            "category_id": transactions[0].get("category_id"),
            "category_icon": transactions[0].get("category_icon"),
            "frequency": frequency,
            "avg_amount": round(avg_amount, 2),
            "min_amount": round(min_amount, 2),
            "max_amount": round(max_amount, 2),
            "last_amount": round(last_amount, 2),
            "trend_percent": round(trend_percent, 1),
            "first_occurrence": first_occurrence,
            "last_occurrence": last_occurrence,
            "occurrence_count": len(transactions),
            "provider": provider,
            "is_essential": is_essential if is_essential is not None else False,
            "confidence_score": round(confidence, 2),
        })

    return recurring


def get_category_id_by_name(category_name: str, categories: list) -> int:
    """Get category ID from name."""
    for cat in categories:
        if cat["name"] == category_name:
            return cat["id"]
    # Default to "Altro"
    for cat in categories:
        if cat["name"] == "Altro":
            return cat["id"]
    return 1


def clear_existing_recurring():
    """Clear existing recurring expenses before repopulating."""
    with get_db_context() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM recurring_expenses")
        print(f"Cleared existing recurring expenses")


def main():
    print("=" * 60)
    print("MoneyMind - Recurring Expense Detection")
    print("=" * 60)

    # Get all transactions (last 24 months)
    start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
    transactions = get_transactions({"start_date": start_date})

    if not transactions:
        print("No transactions found!")
        return

    print(f"\nAnalyzing {len(transactions)} transactions...")

    # Get categories
    categories = get_categories()

    # Group by pattern
    patterns = group_transactions_by_pattern(transactions)
    print(f"Found {len(patterns)} unique patterns")

    # Analyze patterns
    recurring = analyze_patterns(patterns, min_occurrences=2)
    print(f"Detected {len(recurring)} recurring expenses")

    if not recurring:
        print("No recurring patterns detected!")
        return

    # Clear existing and insert new
    clear_existing_recurring()

    # Insert recurring expenses
    inserted = 0
    for rec in recurring:
        # Get correct category ID
        category_id = get_category_id_by_name(rec["category_name"], categories)

        try:
            add_recurring_expense({
                "pattern_name": rec["pattern_name"],
                "category_id": category_id,
                "frequency": rec["frequency"],
                "avg_amount": rec["avg_amount"],
                "min_amount": rec["min_amount"],
                "max_amount": rec["max_amount"],
                "last_amount": rec["last_amount"],
                "trend_percent": rec["trend_percent"],
                "first_occurrence": rec["first_occurrence"],
                "last_occurrence": rec["last_occurrence"],
                "occurrence_count": rec["occurrence_count"],
                "provider": rec["provider"],
                "is_essential": 1 if rec["is_essential"] else 0,
                "confidence_score": rec["confidence_score"],
            })
            inserted += 1
        except Exception as e:
            print(f"Error inserting {rec['pattern_name']}: {e}")

    print(f"\nInserted {inserted} recurring expenses")

    # Print summary
    print("\n" + "=" * 60)
    print("Detected Recurring Expenses:")
    print("=" * 60)

    # Sort by avg_amount descending
    recurring.sort(key=lambda x: x["avg_amount"], reverse=True)

    total_monthly = 0
    for rec in recurring[:20]:  # Top 20
        freq = rec["frequency"]
        monthly = rec["avg_amount"]
        if freq == "quarterly":
            monthly = rec["avg_amount"] / 3
        elif freq == "annual":
            monthly = rec["avg_amount"] / 12

        total_monthly += monthly

        essential = "E" if rec["is_essential"] else " "
        print(f"[{essential}] {rec['pattern_name'][:30]:<30} {rec['avg_amount']:>8.2f}€/{freq[:3]} "
              f"({rec['occurrence_count']:>2}x, {rec['confidence_score']:.0%})")

    print("-" * 60)
    print(f"Total Monthly (top 20): {total_monthly:,.2f}€")
    print("=" * 60)


if __name__ == "__main__":
    main()
