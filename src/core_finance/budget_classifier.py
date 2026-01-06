"""
Budget Classifier - Fixed vs Discretionary Expense Classification

Distinguishes between:
- FIXED: Must-pay expenses (rent, utilities, financing, health, base transportation)
- DISCRETIONARY: Can-reduce expenses (restaurants, shopping, entertainment, travel)

Provides "remaining budget" calculations for discretionary spending control.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dateutil.relativedelta import relativedelta

from src.database import (
    get_db_context, get_categories, get_spending_by_category
)


# ============================================================================
# Category Classification
# ============================================================================

FIXED_EXPENSE_CATEGORIES = [
    "Affitto",           # Must pay - housing
    "Utenze",            # Must pay - utilities
    "Finanziamenti",     # Must pay - contracts
    "Salute",            # Must pay - health
    "Cura Personale",    # Necessary - personal care
    "Trasporti",         # Necessary - basic transportation
    "Spesa",             # Necessary - groceries
    "Gatti",             # Necessary - pet care
    "Contanti",          # Variable but often necessary
]

DISCRETIONARY_CATEGORIES = [
    "Ristoranti",        # Can reduce - dining out
    "Caffe",             # Can reduce - coffee/snacks
    "Shopping",          # Can eliminate - shopping
    "Abbonamenti",       # Can optimize - subscriptions
    "Viaggi",            # Can postpone - travel
    "Intrattenimento",   # Can reduce - entertainment
    "Regali",            # Can reduce - gifts
]

# Categories to exclude from budget analysis
EXCLUDE_CATEGORIES = [
    "Stipendio",              # Income
    "Trasferimenti",          # Internal transfers
    "Risparmi Automatici",    # Savings (not expense)
    "Altro",                  # Uncategorized
]


@dataclass
class CategoryBudget:
    """Budget status for a single category."""
    category: str
    budget_type: str  # 'fixed' or 'discretionary'
    monthly_budget: float
    spent_this_month: float
    remaining: float
    days_left_in_month: int
    daily_budget_remaining: float
    percent_used: float
    status: str  # 'on_track', 'warning', 'over_budget'


@dataclass
class BudgetSummary:
    """Complete budget breakdown."""
    month: str
    total_income: float
    total_fixed: float
    total_discretionary_budget: float
    total_discretionary_spent: float
    discretionary_remaining: float
    savings_potential: float
    fixed_breakdown: List[CategoryBudget]
    discretionary_breakdown: List[CategoryBudget]


class BudgetClassifier:
    """
    Classifies expenses as fixed or discretionary and calculates
    remaining budget for spending control.
    """

    def __init__(self, budget_buffer: float = 1.1):
        """
        Initialize the classifier.

        Args:
            budget_buffer: Multiplier for calculating budget from 3-month avg (default 1.1 = 10% buffer)
        """
        self.budget_buffer = budget_buffer
        self.categories = {c["name"]: c for c in get_categories()}

    def classify_category(self, category_name: str) -> str:
        """
        Classify a category as fixed or discretionary.

        Args:
            category_name: Name of the category

        Returns:
            'fixed', 'discretionary', or 'excluded'
        """
        if category_name in EXCLUDE_CATEGORIES:
            return "excluded"
        elif category_name in FIXED_EXPENSE_CATEGORIES:
            return "fixed"
        elif category_name in DISCRETIONARY_CATEGORIES:
            return "discretionary"
        else:
            # Unknown categories default to discretionary
            return "discretionary"

    def get_budget_summary(self, month: Optional[str] = None) -> BudgetSummary:
        """
        Get complete budget breakdown for a month.

        Args:
            month: Month in YYYY-MM format (defaults to current month)

        Returns:
            BudgetSummary with fixed/discretionary breakdown
        """
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        # Get current month spending
        current_spending = get_spending_by_category(month)

        # Calculate 3-month averages
        ref_date = datetime.strptime(month + "-01", "%Y-%m-%d")
        historical = {}

        for i in range(1, 4):
            past_month = (ref_date - relativedelta(months=i)).strftime("%Y-%m")
            past_spending = get_spending_by_category(past_month)
            for cat in past_spending:
                cat_name = cat.get("category_name", "")
                if cat_name not in historical:
                    historical[cat_name] = []
                historical[cat_name].append(abs(cat.get("total_spent", 0) or 0))

        # Calculate averages
        averages = {
            cat: sum(vals) / len(vals) if vals else 0
            for cat, vals in historical.items()
        }

        # Calculate days remaining in month
        year, month_num = map(int, month.split("-"))
        today = datetime.now()
        if today.year == year and today.month == month_num:
            # Current month - calculate actual days left
            import calendar
            last_day = calendar.monthrange(year, month_num)[1]
            days_left = last_day - today.day
        else:
            # Past/future month - use 0 or full month
            days_left = 0 if today > datetime(year, month_num, 1) else 30

        # Build category budgets
        fixed_breakdown = []
        discretionary_breakdown = []
        total_fixed = 0
        total_discretionary_budget = 0
        total_discretionary_spent = 0
        total_income = 0

        # Create lookup for current spending
        spending_lookup = {
            item["category_name"]: abs(item.get("total_spent", 0) or 0)
            for item in current_spending
        }

        # Get income
        for item in current_spending:
            cat_name = item.get("category_name", "")
            if cat_name == "Stipendio":
                total_income = item.get("total_spent", 0) or 0

        # Process all known categories
        processed = set()
        for cat_name in list(FIXED_EXPENSE_CATEGORIES) + list(DISCRETIONARY_CATEGORIES):
            if cat_name in processed:
                continue
            processed.add(cat_name)

            budget_type = self.classify_category(cat_name)
            if budget_type == "excluded":
                continue

            # Get amounts
            spent = spending_lookup.get(cat_name, 0)
            avg_3m = averages.get(cat_name, 0)

            # Calculate budget (from 3-month average with buffer)
            if avg_3m > 0:
                budget = avg_3m * self.budget_buffer
            else:
                # No history - use a reasonable default or 0
                budget = 0

            remaining = max(0, budget - spent)
            percent_used = (spent / budget * 100) if budget > 0 else 0
            daily_remaining = remaining / days_left if days_left > 0 else 0

            # Determine status
            if percent_used > 100:
                status = "over_budget"
            elif percent_used > 80:
                status = "warning"
            else:
                status = "on_track"

            category_budget = CategoryBudget(
                category=cat_name,
                budget_type=budget_type,
                monthly_budget=round(budget, 2),
                spent_this_month=round(spent, 2),
                remaining=round(remaining, 2),
                days_left_in_month=days_left,
                daily_budget_remaining=round(daily_remaining, 2),
                percent_used=round(percent_used, 1),
                status=status,
            )

            if budget_type == "fixed":
                fixed_breakdown.append(category_budget)
                total_fixed += spent
            else:
                discretionary_breakdown.append(category_budget)
                total_discretionary_budget += budget
                total_discretionary_spent += spent

        # Sort by percent used (descending) - show problems first
        fixed_breakdown.sort(key=lambda x: -x.percent_used)
        discretionary_breakdown.sort(key=lambda x: -x.percent_used)

        # Calculate savings potential
        discretionary_remaining = total_discretionary_budget - total_discretionary_spent
        savings_potential = max(0, discretionary_remaining)

        return BudgetSummary(
            month=month,
            total_income=round(total_income, 2),
            total_fixed=round(total_fixed, 2),
            total_discretionary_budget=round(total_discretionary_budget, 2),
            total_discretionary_spent=round(total_discretionary_spent, 2),
            discretionary_remaining=round(discretionary_remaining, 2),
            savings_potential=round(savings_potential, 2),
            fixed_breakdown=fixed_breakdown,
            discretionary_breakdown=discretionary_breakdown,
        )

    def to_dict(self, summary: BudgetSummary) -> Dict:
        """Convert BudgetSummary to dictionary for API response."""
        return {
            "month": summary.month,
            "total_income": summary.total_income,
            "total_fixed": summary.total_fixed,
            "total_discretionary_budget": summary.total_discretionary_budget,
            "total_discretionary_spent": summary.total_discretionary_spent,
            "discretionary_remaining": summary.discretionary_remaining,
            "savings_potential": summary.savings_potential,
            "fixed_breakdown": [
                {
                    "category": b.category,
                    "budget_type": b.budget_type,
                    "monthly_budget": b.monthly_budget,
                    "spent_this_month": b.spent_this_month,
                    "remaining": b.remaining,
                    "days_left_in_month": b.days_left_in_month,
                    "daily_budget_remaining": b.daily_budget_remaining,
                    "percent_used": b.percent_used,
                    "status": b.status,
                }
                for b in summary.fixed_breakdown
            ],
            "discretionary_breakdown": [
                {
                    "category": b.category,
                    "budget_type": b.budget_type,
                    "monthly_budget": b.monthly_budget,
                    "spent_this_month": b.spent_this_month,
                    "remaining": b.remaining,
                    "days_left_in_month": b.days_left_in_month,
                    "daily_budget_remaining": b.daily_budget_remaining,
                    "percent_used": b.percent_used,
                    "status": b.status,
                }
                for b in summary.discretionary_breakdown
            ],
        }


# CLI entry point for testing
if __name__ == "__main__":
    print("Budget Classifier - Fixed vs Discretionary Analysis\n")

    classifier = BudgetClassifier()
    summary = classifier.get_budget_summary()

    print(f"=== {summary.month} Budget Summary ===\n")
    print(f"Total Income: EUR {summary.total_income:.0f}")
    print(f"Total Fixed Expenses: EUR {summary.total_fixed:.0f}")
    print(f"Discretionary Budget: EUR {summary.total_discretionary_budget:.0f}")
    print(f"Discretionary Spent: EUR {summary.total_discretionary_spent:.0f}")
    print(f"Discretionary Remaining: EUR {summary.discretionary_remaining:.0f}")
    print(f"Savings Potential: EUR {summary.savings_potential:.0f}\n")

    print("=== Fixed Expenses (Must Pay) ===")
    for b in summary.fixed_breakdown[:5]:
        status_icon = {"on_track": "OK", "warning": "!!", "over_budget": "XX"}[b.status]
        print(f"  [{status_icon}] {b.category}: EUR {b.spent_this_month:.0f} ({b.percent_used:.0f}% of budget)")

    print("\n=== Discretionary (Can Reduce) ===")
    for b in summary.discretionary_breakdown[:5]:
        status_icon = {"on_track": "OK", "warning": "!!", "over_budget": "XX"}[b.status]
        print(f"  [{status_icon}] {b.category}: EUR {b.spent_this_month:.0f} / EUR {b.monthly_budget:.0f}")
        if b.days_left_in_month > 0 and b.remaining > 0:
            print(f"       EUR {b.daily_budget_remaining:.2f}/day remaining ({b.days_left_in_month} days)")
