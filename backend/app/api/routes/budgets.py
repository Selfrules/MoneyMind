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
    """Get budget summary for a month with spending status."""
    repo = BudgetRepository()

    # Get budget status list
    status_list = repo.get_status_list(month)

    # Build response
    categories = []
    total_budget = 0.0
    total_spent = 0.0
    over_budget_count = 0
    warning_count = 0

    for status in status_list:
        categories.append(BudgetStatusResponse(
            category_id=status.category_id,
            category_name=status.category_name or "",
            category_icon=status.category_icon,
            budget_amount=status.budget_amount,
            spent_amount=status.spent_amount,
            remaining=status.remaining,
            percent_used=status.percent_used,
            status=status.status
        ))

        total_budget += status.budget_amount
        total_spent += status.spent_amount

        if status.status == "exceeded":
            over_budget_count += 1
        elif status.status == "warning":
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
