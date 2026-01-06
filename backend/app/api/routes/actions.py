"""
Daily Actions API endpoints.
"""
import sys
from pathlib import Path
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
import sqlite3

# Add src directory to path
BACKEND_DIR = Path(__file__).parent.parent.parent.parent
PROJECT_DIR = BACKEND_DIR.parent
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from app.api.deps import get_db
from app.schemas.actions import (
    DailyAction,
    DailyActionsResponse,
    ActionStatus,
    CompleteActionRequest,
)

# Import existing database functions
from database import (
    get_today_actions,
    complete_daily_action,
    get_pending_action_count,
    get_action_history,
)

router = APIRouter()


@router.get("/actions/today", response_model=DailyActionsResponse)
async def get_todays_actions(db: sqlite3.Connection = Depends(get_db)):
    """
    Get today's pending daily actions (max 3).
    """
    try:
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")

        # Get pending actions for today
        raw_actions = get_today_actions(today_str)

        actions = []
        for a in raw_actions:
            actions.append(
                DailyAction(
                    id=a["id"],
                    action_date=datetime.strptime(a["action_date"], "%Y-%m-%d").date(),
                    priority=a["priority"],
                    title=a["title"],
                    description=a.get("description"),
                    action_type=a.get("action_type"),
                    impact_type=a.get("impact_type"),
                    estimated_impact_monthly=a.get("estimated_impact_monthly"),
                    estimated_impact_payoff_days=a.get("estimated_impact_payoff_days"),
                    status=ActionStatus(a.get("status", "pending")),
                    completed_at=datetime.fromisoformat(a["completed_at"]) if a.get("completed_at") else None,
                    category_name=a.get("category_name"),
                    debt_name=a.get("debt_name"),
                    recurring_expense_name=a.get("recurring_name"),
                )
            )

        # Count completed vs pending
        pending_count = len([a for a in actions if a.status == ActionStatus.PENDING])
        completed_count = len([a for a in actions if a.status == ActionStatus.COMPLETED])

        return DailyActionsResponse(
            date=today,
            actions=actions,
            completed_count=completed_count,
            pending_count=pending_count,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading actions: {str(e)}")


@router.post("/actions/{action_id}/complete")
async def complete_action(
    action_id: int,
    request: CompleteActionRequest,
    db: sqlite3.Connection = Depends(get_db),
):
    """
    Complete a daily action with decision tracking.
    """
    try:
        # Map decision to status
        status_map = {
            "accepted": "completed",
            "rejected": "skipped",
            "postponed": "postponed",
        }
        status = status_map.get(request.decision, "completed")

        success = complete_daily_action(action_id, status)

        if not success:
            raise HTTPException(status_code=404, detail="Action not found")

        return {"success": True, "status": status}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing action: {str(e)}")


@router.get("/actions/history")
async def get_actions_history(
    days: int = 7,
    db: sqlite3.Connection = Depends(get_db),
):
    """
    Get action history for the past N days.
    """
    try:
        history = get_action_history(days)
        return {"actions": history, "days": days}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading history: {str(e)}")
