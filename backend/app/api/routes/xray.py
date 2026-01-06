"""
Financial X-Ray API endpoints.

Provides comprehensive financial health analysis in a single view.
This is the "radiografia finanziaria" that allows the user to understand
their financial situation in 30 seconds or less.
"""
import sys
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
import sqlite3

# Add project root and src directory to path
BACKEND_DIR = Path(__file__).parent.parent.parent.parent
PROJECT_DIR = BACKEND_DIR.parent
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(PROJECT_DIR))  # For 'src.xxx' imports
sys.path.insert(0, str(SRC_DIR))       # For 'xxx' imports

from app.api.deps import get_db
from app.schemas.xray import XRayResponse

# Import X-Ray analyzer
from core_finance.xray_analyzer import XRayAnalyzer

router = APIRouter()


@router.get("/xray", response_model=XRayResponse)
async def get_financial_xray(
    month: str = Query(
        default=None,
        description="Month to analyze in YYYY-MM format. Defaults to current month."
    ),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Get comprehensive financial X-Ray analysis.

    Returns:
    - Cash flow breakdown (essential/debt/discretionary/available)
    - Debt composition analysis
    - Savings potential opportunities
    - Risk indicators (DTI, emergency fund, savings rate)
    - Current phase in financial freedom journey
    - Overall health score and grade
    """
    try:
        # Default to current month if not specified
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        # Validate month format
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid month format. Use YYYY-MM (e.g., 2026-01)"
            )

        # Generate X-Ray analysis
        analyzer = XRayAnalyzer()
        xray = analyzer.generate_xray(month)

        # Convert to API response format
        response_data = analyzer.to_dict(xray)

        return XRayResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating financial X-Ray: {str(e)}"
        )


@router.get("/xray/cash-flow")
async def get_cash_flow_breakdown(
    month: str = Query(default=None),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Get just the cash flow breakdown.

    Useful for widgets that only need cash flow data.
    """
    try:
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        analyzer = XRayAnalyzer()
        cash_flow = analyzer.calculate_cash_flow_breakdown(month)

        return {
            "month": month,
            "income": cash_flow.income,
            "essential_expenses": cash_flow.essential_expenses,
            "debt_payments": cash_flow.debt_payments,
            "discretionary": cash_flow.discretionary,
            "available_for_savings": cash_flow.available_for_savings,
            "total_expenses": cash_flow.total_expenses,
            "savings_rate": cash_flow.savings_rate
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating cash flow: {str(e)}"
        )


@router.get("/xray/debt-analysis")
async def get_debt_analysis(
    month: str = Query(default=None),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Get detailed debt analysis.

    Shows debt composition, interest costs, and freedom timeline.
    """
    try:
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        analyzer = XRayAnalyzer()
        debt_analysis = analyzer.analyze_debt_composition(month)

        return {
            "month": month,
            "total_debt": debt_analysis.total_debt,
            "total_monthly_payments": debt_analysis.total_monthly_payments,
            "total_interest_paid_ytd": debt_analysis.total_interest_paid_ytd,
            "total_interest_remaining": debt_analysis.total_interest_remaining,
            "debt_burden_percent": debt_analysis.debt_burden_percent,
            "months_to_freedom": debt_analysis.months_to_freedom,
            "freedom_date": debt_analysis.freedom_date.isoformat() if debt_analysis.freedom_date else None,
            "highest_rate_debt": {
                "name": debt_analysis.highest_rate_debt.name,
                "rate": debt_analysis.highest_rate_debt.interest_rate,
                "balance": debt_analysis.highest_rate_debt.current_balance
            } if debt_analysis.highest_rate_debt else None,
            "debts": [
                {
                    "id": d.id,
                    "name": d.name,
                    "balance": d.current_balance,
                    "rate": d.interest_rate,
                    "payment": d.monthly_payment,
                    "burden_percent": d.burden_percent
                }
                for d in debt_analysis.debts
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing debt: {str(e)}"
        )


@router.get("/xray/savings-potential")
async def get_savings_potential(
    month: str = Query(default=None),
    limit: int = Query(default=10, ge=1, le=20),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Get savings potential opportunities.

    Identifies areas where spending can be reduced.
    """
    try:
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        analyzer = XRayAnalyzer()
        opportunities = analyzer.identify_savings_potential(month, limit=limit)

        return {
            "month": month,
            "opportunities": [
                {
                    "category": sp.category,
                    "current": sp.current_spending,
                    "baseline": sp.baseline_spending,
                    "potential_savings": sp.potential_savings,
                    "impact_monthly": sp.impact_monthly,
                    "impact_annual": sp.impact_annual,
                    "recommendation": sp.recommendation,
                    "priority": sp.priority
                }
                for sp in opportunities
            ],
            "total_potential_monthly": sum(sp.potential_savings for sp in opportunities),
            "total_potential_annual": sum(sp.impact_annual for sp in opportunities)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error identifying savings potential: {str(e)}"
        )


@router.get("/xray/risk")
async def get_risk_indicators(
    month: str = Query(default=None),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Get financial risk indicators.

    Shows DTI ratio, emergency fund status, and overall risk level.
    """
    try:
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        analyzer = XRayAnalyzer()
        cash_flow = analyzer.calculate_cash_flow_breakdown(month)
        debt_analysis = analyzer.analyze_debt_composition(month)
        risk = analyzer.calculate_risk_indicators(cash_flow, debt_analysis)

        return {
            "month": month,
            "dti_ratio": risk.dti_ratio,
            "emergency_fund_months": risk.emergency_fund_months,
            "savings_rate": risk.savings_rate,
            "expense_volatility": risk.expense_volatility,
            "status": risk.status.value,
            "issues": risk.issues,
            "is_healthy": risk.status.value in ["low", "moderate"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating risk indicators: {str(e)}"
        )


@router.get("/xray/phase")
async def get_current_phase(
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Get current phase in financial freedom journey.

    Returns which of the 4 phases (Diagnosi, Ottimizzazione, Sicurezza, Crescita)
    the user is currently in, along with progress and next milestone.
    """
    try:
        month = datetime.now().strftime("%Y-%m")
        analyzer = XRayAnalyzer()

        debt_analysis = analyzer.analyze_debt_composition(month)
        cash_flow = analyzer.calculate_cash_flow_breakdown(month)
        risk = analyzer.calculate_risk_indicators(cash_flow, debt_analysis)
        phase_info = analyzer.determine_current_phase(debt_analysis, risk)

        return {
            "current_phase": phase_info.current_phase.value,
            "phase_name": {
                "diagnosi": "Diagnosi",
                "ottimizzazione": "Ottimizzazione",
                "sicurezza": "Sicurezza",
                "crescita": "Crescita"
            }.get(phase_info.current_phase.value, phase_info.current_phase.value),
            "progress_percent": phase_info.progress_percent,
            "next_milestone": phase_info.next_milestone,
            "days_in_phase": phase_info.days_in_phase,
            "phase_started": phase_info.phase_started.isoformat() if phase_info.phase_started else None
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error determining phase: {str(e)}"
        )
