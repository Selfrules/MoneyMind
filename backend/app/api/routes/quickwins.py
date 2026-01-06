"""
Quick Wins API endpoints.

Provides prioritized quick win opportunities for financial optimization.
Quick wins are easy-to-implement, high-impact actions that can be done today.
"""
import sys
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

# Add project root and src directory to path
BACKEND_DIR = Path(__file__).parent.parent.parent.parent
PROJECT_DIR = BACKEND_DIR.parent
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(SRC_DIR))

from app.api.deps import get_db

# Import Quick Wins engine
from core_finance.quick_wins_engine import QuickWinsEngine


router = APIRouter()


# Response models
class QuickWinResponse(BaseModel):
    id: str
    type: str
    title: str
    description: str
    estimated_savings_monthly: float
    estimated_savings_annual: float
    payoff_impact_days: int
    effort_level: str
    time_to_complete: str
    quick_win_score: float
    confidence: float
    action_steps: List[str]
    cta_text: str
    cta_url: Optional[str] = None
    category: Optional[str] = None
    provider: Optional[str] = None
    recurring_expense_id: Optional[int] = None
    debt_id: Optional[int] = None
    icon: str
    priority_badge: str


class QuickWinsListResponse(BaseModel):
    wins: List[QuickWinResponse]
    total_monthly_savings: float
    total_annual_savings: float
    total_payoff_days_saved: int
    easy_wins_count: int
    medium_wins_count: int
    execution_order: List[str]


@router.get("/quickwins", response_model=QuickWinsListResponse)
async def get_quick_wins(
    limit: int = Query(default=10, ge=1, le=20, description="Maximum number of quick wins to return"),
    effort_filter: Optional[str] = Query(
        default=None,
        description="Filter by effort level: trivial, easy, medium, hard"
    ),
    type_filter: Optional[str] = Query(
        default=None,
        description="Filter by type: subscription_cancel, subscription_downgrade, provider_switch, negotiate_rate, spending_cut, debt_optimization"
    ),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Get prioritized quick win opportunities.

    Quick wins are scored by:
    - Implementation effort (easier = higher score)
    - Savings impact (higher = better)
    - Confidence level (higher = better)
    - Time to realization (faster = better)

    Returns opportunities sorted by quick_win_score in descending order.
    """
    try:
        # Get debt total for impact calculation
        cursor = db.cursor()
        cursor.execute("SELECT SUM(current_balance) FROM debts WHERE is_active = 1")
        result = cursor.fetchone()
        debt_total = result[0] if result and result[0] else 0

        cursor.execute("SELECT monthly_net_income FROM user_profile LIMIT 1")
        result = cursor.fetchone()
        monthly_income = result[0] if result and result[0] else 3200

        # Generate quick wins
        engine = QuickWinsEngine(debt_total=debt_total, monthly_income=monthly_income)
        report = engine.analyze()

        # Apply filters
        wins = report.wins
        if effort_filter:
            wins = [w for w in wins if w.effort_level == effort_filter]
        if type_filter:
            wins = [w for w in wins if w.type.value == type_filter]

        # Limit results
        wins = wins[:limit]

        # Convert to response
        return QuickWinsListResponse(
            wins=[
                QuickWinResponse(**engine.to_dict(w))
                for w in wins
            ],
            total_monthly_savings=sum(w.estimated_savings_monthly for w in wins),
            total_annual_savings=sum(w.estimated_savings_annual for w in wins),
            total_payoff_days_saved=sum(w.payoff_impact_days for w in wins),
            easy_wins_count=len([w for w in wins if w.effort_level in ("trivial", "easy")]),
            medium_wins_count=len([w for w in wins if w.effort_level == "medium"]),
            execution_order=[w.id for w in wins],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating quick wins: {str(e)}"
        )


@router.get("/quickwins/top")
async def get_top_quick_wins(
    limit: int = Query(default=3, ge=1, le=5),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Get top quick wins for dashboard display.

    Returns only the most impactful, easy-to-implement quick wins
    suitable for dashboard cards or notifications.
    """
    try:
        cursor = db.cursor()
        cursor.execute("SELECT SUM(current_balance) FROM debts WHERE is_active = 1")
        result = cursor.fetchone()
        debt_total = result[0] if result and result[0] else 0

        engine = QuickWinsEngine(debt_total=debt_total)
        top_wins = engine.get_top_quick_wins(limit)

        return {
            "wins": [engine.to_dict(w) for w in top_wins],
            "total_count": len(top_wins),
            "total_monthly_savings": sum(w.estimated_savings_monthly for w in top_wins),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting top quick wins: {str(e)}"
        )


@router.get("/quickwins/{win_id}")
async def get_quick_win_detail(
    win_id: str,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Get detailed information about a specific quick win.

    Includes full implementation steps and impact calculations.
    """
    try:
        cursor = db.cursor()
        cursor.execute("SELECT SUM(current_balance) FROM debts WHERE is_active = 1")
        result = cursor.fetchone()
        debt_total = result[0] if result and result[0] else 0

        engine = QuickWinsEngine(debt_total=debt_total)
        report = engine.analyze()

        # Find the specific win
        for win in report.wins:
            if win.id == win_id:
                return engine.to_dict(win)

        raise HTTPException(
            status_code=404,
            detail=f"Quick win not found: {win_id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting quick win detail: {str(e)}"
        )


@router.post("/quickwins/{win_id}/complete")
async def complete_quick_win(
    win_id: str,
    actual_savings: Optional[float] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Mark a quick win as completed.

    Optionally provide actual savings achieved for tracking.
    """
    try:
        # For now, just return success
        # In future, this would create a decision record and update tracking
        return {
            "status": "completed",
            "win_id": win_id,
            "actual_savings": actual_savings,
            "message": "Quick win marked as completed"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error completing quick win: {str(e)}"
        )


@router.post("/quickwins/{win_id}/dismiss")
async def dismiss_quick_win(
    win_id: str,
    reason: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Dismiss a quick win (not interested).

    Optionally provide reason for dismissal.
    """
    try:
        return {
            "status": "dismissed",
            "win_id": win_id,
            "reason": reason,
            "message": "Quick win dismissed"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error dismissing quick win: {str(e)}"
        )


@router.get("/quickwins/summary")
async def get_quick_wins_summary(
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Get summary statistics for all quick wins.

    Useful for overview displays showing total potential savings.
    """
    try:
        cursor = db.cursor()
        cursor.execute("SELECT SUM(current_balance) FROM debts WHERE is_active = 1")
        result = cursor.fetchone()
        debt_total = result[0] if result and result[0] else 0

        engine = QuickWinsEngine(debt_total=debt_total)
        report = engine.analyze()

        # Group by type
        by_type = {}
        for win in report.wins:
            type_name = win.type.value
            if type_name not in by_type:
                by_type[type_name] = {"count": 0, "savings": 0}
            by_type[type_name]["count"] += 1
            by_type[type_name]["savings"] += win.estimated_savings_monthly

        return {
            "total_wins": len(report.wins),
            "easy_wins": report.easy_wins_count,
            "medium_wins": report.medium_wins_count,
            "total_monthly_savings": report.total_monthly_savings,
            "total_annual_savings": report.total_annual_savings,
            "total_payoff_days_saved": report.total_payoff_days_saved,
            "by_type": by_type,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting quick wins summary: {str(e)}"
        )
