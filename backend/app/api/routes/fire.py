"""FIRE Calculator API routes.

Uses XRayAnalyzer for consistent data with dashboard.
"""
import sys
from pathlib import Path

# Add project root to path for src imports
ROUTES_DIR = Path(__file__).parent
API_DIR = ROUTES_DIR.parent
APP_DIR = API_DIR.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_DIR = BACKEND_DIR.parent
SRC_DIR = PROJECT_DIR / "src"
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date

from src.core_finance.fire_calculator import FIRECalculator, calculate_fire_from_profile
from src.database import get_user_profile, get_total_debt, get_transactions
from core_finance.xray_analyzer import XRayAnalyzer

router = APIRouter()


class FIRECalculateRequest(BaseModel):
    """Request model for FIRE calculation."""
    annual_expenses: float = Field(..., description="Annual living expenses")
    current_net_worth: float = Field(0, description="Current total net worth")
    monthly_investment: float = Field(..., description="Monthly investment/savings amount")
    expected_return: float = Field(0.07, description="Expected annual return rate")
    inflation_rate: float = Field(0.02, description="Expected annual inflation rate")
    withdrawal_rate: float = Field(0.04, description="Safe withdrawal rate")


class FIREMilestoneResponse(BaseModel):
    """Response model for FIRE milestone."""
    name: str
    target_amount: float
    target_percent: float
    years_to_reach: float
    projected_date: str
    description: str
    is_achieved: bool = False


class FIREScenarioResponse(BaseModel):
    """Response model for FIRE scenario."""
    return_rate: float
    expenses: float
    fire_number: float
    years_to_fire: float
    fire_date: str


class FIRESummaryResponse(BaseModel):
    """Response model for FIRE summary."""
    fire_number: float
    current_net_worth: float
    progress_percent: float
    years_to_fire: float
    months_to_fire: int
    fire_date: str
    monthly_investment: float
    annual_expenses: float
    expected_return: float
    withdrawal_rate: float
    savings_rate: float
    milestones: List[FIREMilestoneResponse]
    scenarios: Dict[str, FIREScenarioResponse]


class MonthlyProjectionResponse(BaseModel):
    """Response model for monthly projection data point."""
    month: str
    months_from_now: int
    net_worth: float
    contributions: float
    investment_gains: float
    fire_percent: float


class ProjectionsResponse(BaseModel):
    """Response model for FIRE projections."""
    projections: List[MonthlyProjectionResponse]
    fire_number: float
    fire_date: str
    years_to_fire: float


class SensitivityResponse(BaseModel):
    """Response model for sensitivity analysis."""
    base_case: Dict[str, Any]
    return_sensitivity: List[Dict[str, Any]]
    expense_sensitivity: List[Dict[str, Any]]
    scenarios: Dict[str, Dict[str, Any]]


def get_user_financial_data() -> Dict[str, Any]:
    """
    Get user's current financial data for FIRE calculations.

    Uses XRayAnalyzer for consistent data with dashboard.

    Returns:
        Dictionary with monthly_income, monthly_expenses, current_net_worth
    """
    from datetime import datetime
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Use XRayAnalyzer for consistent data with dashboard
        analyzer = XRayAnalyzer()
        current_month = datetime.now().strftime("%Y-%m")

        # Get cash flow breakdown - same as dashboard
        logger.info(f"FIRE: Getting cash flow for month {current_month}")
        cash_flow = analyzer.calculate_cash_flow_breakdown(current_month)
        print(f"FIRE DEBUG: XRay cash_flow income={cash_flow.income}, available={cash_flow.available_for_savings}")
        logger.info(f"FIRE: XRay cash_flow income={cash_flow.income}, available={cash_flow.available_for_savings}")

        monthly_income = cash_flow.income
        monthly_expenses = cash_flow.total_expenses
        available_for_savings = cash_flow.available_for_savings

        # Get debt info
        total_debt = get_total_debt()

        # Calculate net worth (simplified: savings accumulation - debt)
        # For now, use a simple estimate based on available savings
        # In a real scenario, this would come from actual savings accounts
        transactions = get_transactions({})

        # Get savings transactions (money moved to savings)
        savings_txs = [
            t for t in transactions
            if t.get("category", "") in ["Risparmi Automatici", "Investimenti"]
            and t["amount"] < 0  # Money going to savings
        ]
        if savings_txs:
            total_savings = sum(abs(t["amount"]) for t in savings_txs)
        else:
            total_savings = 0

        # Simple net worth: savings - debt
        current_net_worth = max(0, total_savings - total_debt)

        return {
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "current_net_worth": current_net_worth,
            "total_debt": total_debt,
            "monthly_savings": available_for_savings,  # Use XRay's available_for_savings
        }
    except Exception as e:
        # Fallback to profile-based calculation
        print(f"FIRE DEBUG: XRay failed with error: {e}")
        import traceback
        print(f"FIRE DEBUG: Traceback: {traceback.format_exc()}")
        logger.error(f"FIRE: XRay failed with error: {e}")
        logger.error(f"FIRE: Traceback: {traceback.format_exc()}")
        profile = get_user_profile()
        monthly_income = profile.get("monthly_net_income", 0) if profile else 0

        # Estimate 70% of income as expenses
        monthly_expenses = monthly_income * 0.7
        monthly_savings = monthly_income - monthly_expenses
        total_debt = get_total_debt()

        return {
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "current_net_worth": 0,
            "total_debt": total_debt,
            "monthly_savings": max(0, monthly_savings),
        }


@router.get("/fire/summary", response_model=FIRESummaryResponse)
async def get_fire_summary(
    expected_return: float = Query(0.07, description="Expected annual return rate"),
    withdrawal_rate: float = Query(0.04, description="Safe withdrawal rate")
):
    """
    Get comprehensive FIRE summary based on user's current financial situation.

    Automatically calculates from user profile and transaction data.
    """
    financial_data = get_user_financial_data()

    result = calculate_fire_from_profile(
        monthly_income=financial_data["monthly_income"],
        monthly_expenses=financial_data["monthly_expenses"],
        current_net_worth=financial_data["current_net_worth"],
        expected_return=expected_return,
        withdrawal_rate=withdrawal_rate
    )

    return FIRESummaryResponse(
        fire_number=result["fire_number"],
        current_net_worth=result["current_net_worth"],
        progress_percent=result["progress_percent"],
        years_to_fire=result["years_to_fire"],
        months_to_fire=result["months_to_fire"],
        fire_date=result["fire_date"],
        monthly_investment=result["monthly_investment"],
        annual_expenses=result["annual_expenses"],
        expected_return=result["expected_return"],
        withdrawal_rate=result["withdrawal_rate"],
        savings_rate=result["savings_rate"],
        milestones=[
            FIREMilestoneResponse(
                name=m["name"],
                target_amount=m["target_amount"],
                target_percent=m["target_percent"],
                years_to_reach=m["years_to_reach"],
                projected_date=m["projected_date"],
                description=m["description"],
                is_achieved=m["is_achieved"]
            )
            for m in result["milestones"]
        ],
        scenarios={
            k: FIREScenarioResponse(
                return_rate=v["return_rate"],
                expenses=v["expenses"],
                fire_number=v["fire_number"],
                years_to_fire=v["years_to_fire"],
                fire_date=v["fire_date"]
            )
            for k, v in result["scenarios"].items()
        }
    )


@router.post("/fire/calculate", response_model=FIRESummaryResponse)
async def calculate_fire(request: FIRECalculateRequest):
    """
    Calculate FIRE projections with custom parameters.

    Allows users to explore different scenarios by providing custom values.
    """
    calculator = FIRECalculator(
        current_net_worth=request.current_net_worth,
        monthly_investment=request.monthly_investment,
        annual_expenses=request.annual_expenses,
        expected_return=request.expected_return,
        inflation_rate=request.inflation_rate,
        withdrawal_rate=request.withdrawal_rate
    )

    result = calculator.get_fire_summary()

    return FIRESummaryResponse(
        fire_number=result["fire_number"],
        current_net_worth=result["current_net_worth"],
        progress_percent=result["progress_percent"],
        years_to_fire=result["years_to_fire"],
        months_to_fire=result["months_to_fire"],
        fire_date=result["fire_date"],
        monthly_investment=result["monthly_investment"],
        annual_expenses=result["annual_expenses"],
        expected_return=result["expected_return"],
        withdrawal_rate=result["withdrawal_rate"],
        savings_rate=result["savings_rate"],
        milestones=[
            FIREMilestoneResponse(
                name=m["name"],
                target_amount=m["target_amount"],
                target_percent=m["target_percent"],
                years_to_reach=m["years_to_reach"],
                projected_date=m["projected_date"],
                description=m["description"],
                is_achieved=m["is_achieved"]
            )
            for m in result["milestones"]
        ],
        scenarios={
            k: FIREScenarioResponse(
                return_rate=v["return_rate"],
                expenses=v["expenses"],
                fire_number=v["fire_number"],
                years_to_fire=v["years_to_fire"],
                fire_date=v["fire_date"]
            )
            for k, v in result["scenarios"].items()
        }
    )


@router.get("/fire/projections", response_model=ProjectionsResponse)
async def get_fire_projections(
    years: int = Query(30, description="Years to project"),
    expected_return: float = Query(0.07, description="Expected annual return rate"),
    withdrawal_rate: float = Query(0.04, description="Safe withdrawal rate")
):
    """
    Get month-by-month FIRE projections for charting.

    Returns net worth projections over time.
    """
    financial_data = get_user_financial_data()

    calculator = FIRECalculator(
        current_net_worth=financial_data["current_net_worth"],
        monthly_investment=financial_data["monthly_savings"],
        annual_expenses=financial_data["monthly_expenses"] * 12,
        expected_return=expected_return,
        withdrawal_rate=withdrawal_rate
    )

    fire_number = calculator.calculate_fire_number()
    projection = calculator.project_to_fire()
    projections = calculator.generate_monthly_projections(years=years)

    return ProjectionsResponse(
        projections=[
            MonthlyProjectionResponse(
                month=p.month.isoformat(),
                months_from_now=p.months_from_now,
                net_worth=p.net_worth,
                contributions=p.contributions,
                investment_gains=p.investment_gains,
                fire_percent=p.fire_percent
            )
            for p in projections
        ],
        fire_number=fire_number,
        fire_date=projection.fire_date.isoformat(),
        years_to_fire=projection.years_to_fire
    )


@router.get("/fire/sensitivity", response_model=SensitivityResponse)
async def get_fire_sensitivity():
    """
    Get FIRE sensitivity analysis.

    Shows how changes in returns or expenses affect time to FIRE.
    """
    financial_data = get_user_financial_data()

    calculator = FIRECalculator(
        current_net_worth=financial_data["current_net_worth"],
        monthly_investment=financial_data["monthly_savings"],
        annual_expenses=financial_data["monthly_expenses"] * 12
    )

    result = calculator.sensitivity_analysis()

    return SensitivityResponse(
        base_case=result["base_case"],
        return_sensitivity=result["return_sensitivity"],
        expense_sensitivity=result["expense_sensitivity"],
        scenarios=result["scenarios"]
    )


@router.post("/fire/simulate-extra-savings")
async def simulate_extra_savings(
    extra_monthly: float = Query(..., description="Extra monthly savings amount")
):
    """
    Simulate the impact of adding extra monthly savings.

    Shows how additional savings accelerates FIRE timeline.
    """
    financial_data = get_user_financial_data()

    # Base case
    base_calculator = FIRECalculator(
        current_net_worth=financial_data["current_net_worth"],
        monthly_investment=financial_data["monthly_savings"],
        annual_expenses=financial_data["monthly_expenses"] * 12
    )
    base_projection = base_calculator.project_to_fire()

    # With extra savings
    new_calculator = FIRECalculator(
        current_net_worth=financial_data["current_net_worth"],
        monthly_investment=financial_data["monthly_savings"] + extra_monthly,
        annual_expenses=financial_data["monthly_expenses"] * 12
    )
    new_projection = new_calculator.project_to_fire()

    # Calculate impact
    years_saved = base_projection.years_to_fire - new_projection.years_to_fire
    months_saved = base_projection.months_to_fire - new_projection.months_to_fire

    return {
        "current": {
            "monthly_savings": financial_data["monthly_savings"],
            "years_to_fire": base_projection.years_to_fire,
            "fire_date": base_projection.fire_date.isoformat(),
        },
        "with_extra": {
            "monthly_savings": financial_data["monthly_savings"] + extra_monthly,
            "extra_amount": extra_monthly,
            "years_to_fire": new_projection.years_to_fire,
            "fire_date": new_projection.fire_date.isoformat(),
        },
        "impact": {
            "years_saved": round(years_saved, 1),
            "months_saved": months_saved,
            "time_saved_description": f"{int(years_saved)} anni e {months_saved % 12} mesi",
        }
    }
