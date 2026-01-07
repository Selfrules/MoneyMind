"""Profile API routes."""
import sys
from pathlib import Path

# Add project root to path for src imports
ROUTES_DIR = Path(__file__).parent
API_DIR = ROUTES_DIR.parent
APP_DIR = API_DIR.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_DIR = BACKEND_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime

from app.schemas.profile import (
    UserProfileResponse,
    UpdateProfileRequest,
    KPIHistoryEntry,
    KPIHistoryResponse,
    MonthlyReportResponse,
)
from app.api.deps import get_db
from src.database import (
    get_user_profile,
    save_user_profile,
    get_kpi_history,
    get_transactions,
    get_budgets,
    get_insights,
    get_debts,
)
from src.analytics import (
    get_financial_snapshot,
    get_top_spending_categories,
    calculate_savings_rate,
)

router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(db=Depends(get_db)):
    """Get user profile."""
    profile = get_user_profile()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return UserProfileResponse(
        id=profile.get("id", 1),
        income_type=profile.get("income_type"),
        monthly_net_income=profile.get("monthly_net_income", 0),
        risk_tolerance=profile.get("risk_tolerance"),
        financial_knowledge=profile.get("financial_knowledge"),
        coaching_style=profile.get("coaching_style"),
        emergency_fund_target_months=profile.get("emergency_fund_target_months", 6),
        created_at=profile.get("created_at"),
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile_endpoint(
    request: UpdateProfileRequest,
    db=Depends(get_db)
):
    """Update user profile."""
    # Get current profile or create default
    current = get_user_profile() or {}

    # Merge updates
    if request.income_type is not None:
        current["income_type"] = request.income_type
    if request.monthly_net_income is not None:
        current["monthly_net_income"] = request.monthly_net_income
    if request.risk_tolerance is not None:
        current["risk_tolerance"] = request.risk_tolerance
    if request.financial_knowledge is not None:
        current["financial_knowledge"] = request.financial_knowledge
    if request.coaching_style is not None:
        current["coaching_style"] = request.coaching_style
    if request.emergency_fund_target_months is not None:
        current["emergency_fund_target_months"] = request.emergency_fund_target_months

    # Save merged profile
    try:
        save_user_profile(current)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

    profile = get_user_profile()
    return UserProfileResponse(
        id=profile.get("id", 1),
        income_type=profile.get("income_type"),
        monthly_net_income=profile.get("monthly_net_income", 0),
        risk_tolerance=profile.get("risk_tolerance"),
        financial_knowledge=profile.get("financial_knowledge"),
        coaching_style=profile.get("coaching_style"),
        emergency_fund_target_months=profile.get("emergency_fund_target_months", 6),
        created_at=profile.get("created_at"),
    )


@router.get("/profile/kpi-history", response_model=KPIHistoryResponse)
async def get_kpi_history_endpoint(
    months: int = Query(12, description="Number of months of history"),
    db=Depends(get_db)
):
    """Get KPI history for trend analysis."""
    history = get_kpi_history(months)

    entries = []
    for entry in history:
        entries.append(KPIHistoryEntry(
            month=entry["month"],
            net_worth=entry.get("net_worth", 0),
            total_debt=entry.get("total_debt", 0),
            savings_rate=entry.get("savings_rate", 0),
            dti_ratio=entry.get("dti_ratio", 0),
            emergency_fund_months=entry.get("emergency_fund_months", 0),
        ))

    # Determine trend direction
    if len(entries) >= 2:
        recent_savings = entries[-1].savings_rate
        older_savings = entries[0].savings_rate
        if recent_savings > older_savings + 5:
            trend = "improving"
        elif recent_savings < older_savings - 5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"

    return KPIHistoryResponse(
        entries=entries,
        months_count=len(entries),
        trend_direction=trend
    )


@router.get("/reports/monthly/{month}", response_model=MonthlyReportResponse)
async def get_monthly_report(
    month: str,
    db=Depends(get_db)
):
    """Get detailed monthly financial report."""
    # Get financial snapshot for the month
    snapshot = get_financial_snapshot(month)

    # Get top spending categories
    top_cats = get_top_spending_categories(month, limit=10)

    # Get budget performance
    budgets = get_budgets(month)
    if budgets:
        total_budgets = len(budgets)
        under_budget = len([b for b in budgets if b.get("spent_amount", 0) <= b.get("amount", 0)])
        budget_performance = (under_budget / total_budgets * 100) if total_budgets > 0 else 100
    else:
        budget_performance = 100

    # Get debt info
    debts = get_debts(active_only=True)
    total_debt_payment = sum(d.get("monthly_payment", 0) for d in debts)

    # Get insights count (simplified)
    all_insights = get_insights(limit=100)
    insights_count = len(all_insights)

    # Top expense categories from spending analysis
    top_categories = []
    for cat_data in top_cats[:5]:
        top_categories.append({
            "category": cat_data.get("category_name", "Unknown"),
            "amount": cat_data.get("amount", 0)
        })

    # Get savings rate
    savings_rate = calculate_savings_rate(month) or 0

    return MonthlyReportResponse(
        month=month,
        income=snapshot.get("total_income", 0),
        expenses=snapshot.get("total_expenses", 0),
        savings=snapshot.get("total_income", 0) - snapshot.get("total_expenses", 0),
        savings_rate=savings_rate,
        vs_previous_month_savings=None,  # Would need previous month calculation
        top_expense_categories=top_categories,
        budget_performance=budget_performance,
        debt_payments_made=total_debt_payment,
        debt_balance_reduction=0,  # Would need month-over-month calculation
        insights_generated=insights_count,
        actions_completed=0,
        actions_total=0
    )
