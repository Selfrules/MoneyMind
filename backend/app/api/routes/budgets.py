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
)
from app.api.deps import get_db
from src.repositories.budget_repository import BudgetRepository


router = APIRouter()


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


@router.get("/budgets", response_model=BudgetSummaryResponse)
async def get_current_budget():
    """Get budget summary for current month."""
    month = datetime.now().strftime("%Y-%m")
    return await get_budget_summary(month)
