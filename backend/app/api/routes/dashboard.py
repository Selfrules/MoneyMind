"""
Dashboard API endpoints.
"""
import sys
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
import sqlite3

# Add project root and src directory to path
BACKEND_DIR = Path(__file__).parent.parent.parent.parent
PROJECT_DIR = BACKEND_DIR.parent
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(PROJECT_DIR))  # For 'src.xxx' imports
sys.path.insert(0, str(SRC_DIR))       # For 'xxx' imports

from app.api.deps import get_db
from app.schemas.dashboard import (
    DashboardResponse,
    KPIs,
    HealthScore,
    ScenarioComparison,
    MonthSummary,
)

# Import existing analytics functions
from analytics import (
    get_financial_snapshot,
    calculate_financial_health_score,
    compare_payoff_strategies,
)
from database import (
    get_pending_action_count,
    get_unread_insight_count,
    get_user_profile,
)
from core_finance.baseline import BaselineCalculator

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(db: sqlite3.Connection = Depends(get_db)):
    """
    Get complete dashboard data including KPIs, health score, and summaries.
    """
    try:
        current_month = datetime.now().strftime("%Y-%m")

        # Get financial snapshot
        snapshot = get_financial_snapshot(current_month)

        # Get user profile for fallback income
        profile = get_user_profile()
        monthly_income = snapshot.get("total_income") or 0
        if profile and monthly_income < (profile.get("monthly_net_income", 0) or 0) * 0.5:
            monthly_income = profile.get("monthly_net_income") or monthly_income

        # Build KPIs
        kpis = KPIs(
            total_balance=snapshot.get("total_assets") or 0,
            monthly_income=monthly_income,
            monthly_expenses=abs(snapshot.get("total_expenses") or 0),
            savings_rate=snapshot.get("savings_rate") or 0,
            dti_ratio=snapshot.get("dti_ratio") or 0,
            emergency_fund_months=snapshot.get("emergency_fund_months") or 0,
            net_worth=snapshot.get("net_worth") or 0,
            total_debt=snapshot.get("total_debt") or 0,
        )

        # Get health score
        health_data = calculate_financial_health_score()

        # Determine financial phase
        phase = "Debt Payoff" if kpis.total_debt > 0 else "Wealth Building"

        health_score = HealthScore(
            total_score=int(health_data.get("total_score") or 0),
            grade=health_data.get("grade") or "F",
            savings_score=int(health_data.get("components", {}).get("savings_rate", {}).get("score") or 0),
            dti_score=int(health_data.get("components", {}).get("dti_ratio", {}).get("score") or 0),
            emergency_fund_score=int(health_data.get("components", {}).get("emergency_fund", {}).get("score") or 0),
            net_worth_trend_score=int(health_data.get("components", {}).get("net_worth_trend", {}).get("score") or 0),
            phase=phase,
        )

        # Build month summary with baseline comparison
        expenses = abs(snapshot.get("total_expenses") or 0)
        savings = monthly_income - expenses

        # Calculate baseline comparison
        vs_baseline_savings = 0.0
        on_track = savings >= 0

        try:
            baseline_calc = BaselineCalculator()
            comparison = baseline_calc.compare_to_baseline(current_month)
            vs_baseline_savings = comparison.savings_percent_change
            # On track if savings are improving or at least not declining
            on_track = comparison.status != "worse"
        except Exception:
            # Fallback if baseline calculation fails
            pass

        month_summary = MonthSummary(
            month=current_month,
            income=monthly_income,
            expenses=expenses,
            savings=savings,
            vs_baseline_savings=round(vs_baseline_savings, 1),
            on_track=on_track,
        )

        # Get scenario comparison if there are debts
        scenario_comparison = None
        if kpis.total_debt > 0:
            try:
                strategies = compare_payoff_strategies(extra_payment=0)
                avalanche = strategies.get("avalanche", {})
                scenario_comparison = ScenarioComparison(
                    current_payoff_date=None,
                    current_payoff_months=avalanche.get("total_months"),
                    moneymind_payoff_date=avalanche.get("last_payoff_date"),
                    moneymind_payoff_months=avalanche.get("total_months"),
                    months_saved=strategies.get("avalanche_months_saved"),
                    interest_saved=strategies.get("avalanche_interest_saved"),
                )
            except Exception:
                pass

        # Get action and insight counts
        pending_actions = get_pending_action_count()
        unread_insights = get_unread_insight_count()

        return DashboardResponse(
            kpis=kpis,
            health_score=health_score,
            month_summary=month_summary,
            scenario_comparison=scenario_comparison,
            pending_actions_count=pending_actions,
            unread_insights_count=unread_insights,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dashboard: {str(e)}")
