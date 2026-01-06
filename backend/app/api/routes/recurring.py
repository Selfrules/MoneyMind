"""Recurring expenses API routes."""
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

from fastapi import APIRouter, Depends

from app.schemas.recurring import (
    RecurringExpenseResponse,
    RecurringSummaryResponse,
)
from app.api.deps import get_db
from src.repositories.recurring_repository import RecurringRepository


router = APIRouter()


@router.get("/recurring", response_model=RecurringSummaryResponse)
async def get_recurring_summary():
    """Get summary of all recurring expenses."""
    repo = RecurringRepository()

    # Get all active recurring expenses
    expenses = repo.get_active()

    # Build response
    expense_list = []
    total_monthly = 0.0
    essential_monthly = 0.0
    non_essential_monthly = 0.0
    potential_savings = 0.0
    optimizable_count = 0

    for exp in expenses:
        # Normalize to monthly amount
        monthly_amount = exp.avg_amount
        if exp.frequency == "quarterly":
            monthly_amount = exp.avg_amount / 3
        elif exp.frequency == "annual":
            monthly_amount = exp.avg_amount / 12

        expense_list.append(RecurringExpenseResponse(
            id=exp.id,
            pattern_name=exp.pattern_name or "",
            category_id=exp.category_id,
            category_name=exp.category_name,
            category_icon=exp.category_icon,
            frequency=exp.frequency,
            avg_amount=exp.avg_amount,
            last_amount=exp.last_amount,
            trend_percent=exp.trend_percent,
            last_occurrence=exp.last_occurrence,
            occurrence_count=exp.occurrence_count,
            provider=exp.provider,
            is_essential=exp.is_essential,
            optimization_status=exp.optimization_status,
            optimization_suggestion=exp.optimization_suggestion,
            estimated_savings_monthly=exp.estimated_savings_monthly
        ))

        total_monthly += monthly_amount
        if exp.is_essential:
            essential_monthly += monthly_amount
        else:
            non_essential_monthly += monthly_amount

        if exp.estimated_savings_monthly:
            potential_savings += exp.estimated_savings_monthly

        if exp.optimization_status == "not_reviewed" and not exp.is_essential:
            optimizable_count += 1

    return RecurringSummaryResponse(
        total_monthly=total_monthly,
        essential_monthly=essential_monthly,
        non_essential_monthly=non_essential_monthly,
        potential_savings=potential_savings,
        expenses=sorted(expense_list, key=lambda x: x.avg_amount, reverse=True),
        optimizable_count=optimizable_count
    )
