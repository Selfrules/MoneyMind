"""Budget API routes."""
import sys
from pathlib import Path

# Add project root to path for importing src modules
ROUTES_DIR = Path(__file__).parent  # routes/
API_DIR = ROUTES_DIR.parent  # api/
APP_DIR = API_DIR.parent  # app/
BACKEND_DIR = APP_DIR.parent  # backend/
PROJECT_DIR = BACKEND_DIR.parent  # MoneyMind/
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime

from app.schemas.budgets import (
    BudgetStatusResponse,
    BudgetSummaryResponse,
    CategoryBudgetResponse,
    FixedDiscretionaryResponse,
)
from app.api.deps import get_db
from src.repositories.budget_repository import BudgetRepository
from src.core_finance.budget_classifier import BudgetClassifier


router = APIRouter()


# ============================================================================
# Fixed vs Discretionary Budget (MUST BE BEFORE /budgets/{month})
# ============================================================================

@router.get("/budgets/fixed-discretionary", response_model=FixedDiscretionaryResponse)
async def get_fixed_discretionary_breakdown(
    month: Optional[str] = Query(None, description="Month in YYYY-MM format")
):
    """
    Get fixed vs discretionary expense breakdown.

    Shows:
    - Fixed expenses (must pay): rent, utilities, financing, health, transportation
    - Discretionary expenses (can reduce): restaurants, shopping, entertainment

    For each discretionary category, shows remaining daily budget.
    """
    if month is None:
        month = datetime.now().strftime("%Y-%m")

    classifier = BudgetClassifier()
    summary = classifier.get_budget_summary(month)

    return FixedDiscretionaryResponse(
        month=summary.month,
        total_income=summary.total_income,
        total_fixed=summary.total_fixed,
        total_discretionary_budget=summary.total_discretionary_budget,
        total_discretionary_spent=summary.total_discretionary_spent,
        discretionary_remaining=summary.discretionary_remaining,
        savings_potential=summary.savings_potential,
        fixed_breakdown=[
            CategoryBudgetResponse(
                category=b.category,
                budget_type=b.budget_type,
                monthly_budget=b.monthly_budget,
                spent_this_month=b.spent_this_month,
                remaining=b.remaining,
                days_left_in_month=b.days_left_in_month,
                daily_budget_remaining=b.daily_budget_remaining,
                percent_used=b.percent_used,
                status=b.status,
            )
            for b in summary.fixed_breakdown
        ],
        discretionary_breakdown=[
            CategoryBudgetResponse(
                category=b.category,
                budget_type=b.budget_type,
                monthly_budget=b.monthly_budget,
                spent_this_month=b.spent_this_month,
                remaining=b.remaining,
                days_left_in_month=b.days_left_in_month,
                daily_budget_remaining=b.daily_budget_remaining,
                percent_used=b.percent_used,
                status=b.status,
            )
            for b in summary.discretionary_breakdown
        ],
    )


# ============================================================================
# Standard Budget Endpoints
# ============================================================================

@router.get("/budgets", response_model=BudgetSummaryResponse)
async def get_current_budget():
    """Get budget summary for current month."""
    month = datetime.now().strftime("%Y-%m")
    return await get_budget_summary(month)


@router.get("/budgets/{month}", response_model=BudgetSummaryResponse)
async def get_budget_summary(month: str):
    """
    Get budget summary for a month with spending status.

    Uses BudgetClassifier to calculate budgets dynamically from 3-month baseline,
    rather than reading from the (often empty) budgets table.
    """
    from src.database import get_categories

    # Get category info for ID and icon lookup
    categories_db = {c["name"]: c for c in get_categories()}

    # Use BudgetClassifier to get dynamic budget data (same as Dashboard uses)
    classifier = BudgetClassifier()
    summary = classifier.get_budget_summary(month)

    # Combine fixed and discretionary breakdowns
    all_budgets = summary.fixed_breakdown + summary.discretionary_breakdown

    # Build response
    categories = []
    total_budget = 0.0
    total_spent = 0.0
    over_budget_count = 0
    warning_count = 0

    for budget in all_budgets:
        # Skip categories with no activity
        if budget.monthly_budget == 0 and budget.spent_this_month == 0:
            continue

        # Get category info from database
        cat_info = categories_db.get(budget.category, {})
        cat_id = cat_info.get("id", 0)
        cat_icon = cat_info.get("icon", "📦")

        # Map status: 'on_track' -> 'ok', 'over_budget' -> 'exceeded'
        status = budget.status
        if status == "on_track":
            status = "ok"
        elif status == "over_budget":
            status = "exceeded"

        categories.append(BudgetStatusResponse(
            category_id=cat_id,
            category_name=budget.category,
            category_icon=cat_icon,
            budget_amount=budget.monthly_budget,
            spent_amount=budget.spent_this_month,
            remaining=budget.remaining,
            percent_used=budget.percent_used,
            status=status
        ))

        total_budget += budget.monthly_budget
        total_spent += budget.spent_this_month

        if status == "exceeded":
            over_budget_count += 1
        elif status == "warning":
            warning_count += 1

    return BudgetSummaryResponse(
        month=month,
        total_budget=total_budget,
        total_spent=total_spent,
        total_remaining=total_budget - total_spent,
        categories=sorted(categories, key=lambda x: x.percent_used, reverse=True),
        over_budget_count=over_budget_count,
        warning_count=warning_count
    )
