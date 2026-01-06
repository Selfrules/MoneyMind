"""Goals API routes."""
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
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from app.schemas.goals import (
    GoalResponse,
    GoalsSummaryResponse,
    CreateGoalRequest,
    UpdateGoalRequest,
    MilestoneResponse,
    MilestoneListResponse,
    CreateMilestoneRequest,
    CelebrationResponse,
    CelebrationsListResponse,
)
from app.api.deps import get_db
from src.database import (
    get_goals,
    get_goal_by_id,
    add_goal,
    update_goal,
    delete_goal,
    add_milestone,
    get_milestones_for_goal,
    achieve_milestone,
    mark_milestone_celebration_shown,
    get_pending_celebrations,
)

router = APIRouter()


def calculate_goal_info(goal: dict) -> dict:
    """Calculate progress and contribution info for a goal."""
    target = goal.get("target_amount", 0)
    current = goal.get("current_amount", 0)

    if target <= 0:
        return {
            "progress_percent": 0,
            "monthly_contribution_needed": None,
            "months_remaining": None
        }

    progress = (current / target) * 100 if target > 0 else 0

    # Calculate months remaining based on target date
    target_date = goal.get("target_date")
    if target_date and isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

    if target_date and target_date > datetime.now().date():
        months_remaining = (target_date.year - datetime.now().year) * 12 + \
                          (target_date.month - datetime.now().month)
        remaining_amount = target - current
        monthly_needed = remaining_amount / months_remaining if months_remaining > 0 else remaining_amount
    else:
        months_remaining = None
        monthly_needed = None

    return {
        "progress_percent": round(progress, 1),
        "monthly_contribution_needed": round(monthly_needed, 2) if monthly_needed else None,
        "months_remaining": months_remaining
    }


@router.get("/goals", response_model=GoalsSummaryResponse)
async def get_goals_summary(
    status: Optional[str] = Query(None, description="Filter by status: active, completed, paused"),
    db=Depends(get_db)
):
    """Get summary of all goals."""
    goals = get_goals(status=status)

    goal_responses = []
    for goal in goals:
        info = calculate_goal_info(goal)

        # Parse target_date if string
        target_date = goal.get("target_date")
        if target_date and isinstance(target_date, str):
            target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

        goal_responses.append(GoalResponse(
            id=goal["id"],
            name=goal["name"],
            type=goal.get("type", "custom"),
            target_amount=goal["target_amount"],
            current_amount=goal.get("current_amount", 0),
            priority=goal.get("priority", 1),
            status=goal.get("status", "active"),
            target_date=target_date,
            progress_percent=info["progress_percent"],
            monthly_contribution_needed=info["monthly_contribution_needed"],
            months_remaining=info["months_remaining"]
        ))

    total_target = sum(g.target_amount for g in goal_responses)
    total_current = sum(g.current_amount for g in goal_responses)
    overall_progress = (total_current / total_target * 100) if total_target > 0 else 0

    active_count = len([g for g in goal_responses if g.status == "active"])
    completed_count = len([g for g in goal_responses if g.status == "completed"])

    return GoalsSummaryResponse(
        goals=goal_responses,
        total_target=total_target,
        total_current=total_current,
        overall_progress=round(overall_progress, 1),
        active_count=active_count,
        completed_count=completed_count
    )


@router.get("/goals/{goal_id}", response_model=GoalResponse)
async def get_goal(goal_id: int, db=Depends(get_db)):
    """Get a specific goal by ID."""
    goal = get_goal_by_id(goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    info = calculate_goal_info(goal)

    target_date = goal.get("target_date")
    if target_date and isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

    return GoalResponse(
        id=goal["id"],
        name=goal["name"],
        type=goal.get("type", "custom"),
        target_amount=goal["target_amount"],
        current_amount=goal.get("current_amount", 0),
        priority=goal.get("priority", 1),
        status=goal.get("status", "active"),
        target_date=target_date,
        progress_percent=info["progress_percent"],
        monthly_contribution_needed=info["monthly_contribution_needed"],
        months_remaining=info["months_remaining"]
    )


@router.post("/goals", response_model=GoalResponse)
async def create_goal(request: CreateGoalRequest, db=Depends(get_db)):
    """Create a new goal."""
    goal_data = {
        "name": request.name,
        "type": request.type,
        "target_amount": request.target_amount,
        "current_amount": request.current_amount,
        "priority": request.priority,
        "status": "active",
        "target_date": request.target_date.isoformat() if request.target_date else None
    }

    goal_id = add_goal(goal_data)
    if not goal_id:
        raise HTTPException(status_code=500, detail="Failed to create goal")

    goal = get_goal_by_id(goal_id)
    info = calculate_goal_info(goal)

    return GoalResponse(
        id=goal["id"],
        name=goal["name"],
        type=goal.get("type", "custom"),
        target_amount=goal["target_amount"],
        current_amount=goal.get("current_amount", 0),
        priority=goal.get("priority", 1),
        status=goal.get("status", "active"),
        target_date=request.target_date,
        progress_percent=info["progress_percent"],
        monthly_contribution_needed=info["monthly_contribution_needed"],
        months_remaining=info["months_remaining"]
    )


@router.put("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal_endpoint(goal_id: int, request: UpdateGoalRequest, db=Depends(get_db)):
    """Update an existing goal."""
    existing = get_goal_by_id(goal_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Goal not found")

    updates = {}
    if request.name is not None:
        updates["name"] = request.name
    if request.target_amount is not None:
        updates["target_amount"] = request.target_amount
    if request.current_amount is not None:
        updates["current_amount"] = request.current_amount
    if request.priority is not None:
        updates["priority"] = request.priority
    if request.status is not None:
        updates["status"] = request.status
    if request.target_date is not None:
        updates["target_date"] = request.target_date.isoformat()

    if updates:
        success = update_goal(goal_id, updates)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update goal")

    goal = get_goal_by_id(goal_id)
    info = calculate_goal_info(goal)

    target_date = goal.get("target_date")
    if target_date and isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

    return GoalResponse(
        id=goal["id"],
        name=goal["name"],
        type=goal.get("type", "custom"),
        target_amount=goal["target_amount"],
        current_amount=goal.get("current_amount", 0),
        priority=goal.get("priority", 1),
        status=goal.get("status", "active"),
        target_date=target_date,
        progress_percent=info["progress_percent"],
        monthly_contribution_needed=info["monthly_contribution_needed"],
        months_remaining=info["months_remaining"]
    )


@router.delete("/goals/{goal_id}")
async def delete_goal_endpoint(goal_id: int, db=Depends(get_db)):
    """Delete a goal."""
    existing = get_goal_by_id(goal_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Goal not found")

    success = delete_goal(goal_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete goal")

    return {"status": "deleted", "goal_id": goal_id}


# ============================================================================
# Milestone Endpoints
# ============================================================================

@router.get("/goals/{goal_id}/milestones", response_model=MilestoneListResponse)
async def get_goal_milestones(goal_id: int, db=Depends(get_db)):
    """Get all milestones for a specific goal."""
    goal = get_goal_by_id(goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    milestones = get_milestones_for_goal(goal_id)

    milestone_responses = []
    for m in milestones:
        target_date = m.get("target_date")
        if target_date and isinstance(target_date, str):
            target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

        milestone_responses.append(MilestoneResponse(
            id=m["id"],
            goal_id=m["goal_id"],
            milestone_number=m.get("milestone_number", 1),
            title=m["title"],
            description=m.get("description"),
            target_amount=m.get("target_amount"),
            target_date=target_date,
            status=m.get("status", "pending"),
            achieved_at=m.get("achieved_at"),
            actual_amount=m.get("actual_amount"),
            celebration_shown=bool(m.get("celebration_shown", 0)),
            goal_name=goal["name"]
        ))

    achieved_count = len([m for m in milestone_responses if m.status == "achieved"])
    pending_count = len([m for m in milestone_responses if m.status == "pending"])

    return MilestoneListResponse(
        milestones=milestone_responses,
        total_count=len(milestone_responses),
        achieved_count=achieved_count,
        pending_count=pending_count
    )


@router.post("/goals/{goal_id}/milestones", response_model=MilestoneResponse)
async def create_milestone(goal_id: int, request: CreateMilestoneRequest, db=Depends(get_db)):
    """Create a new milestone for a goal."""
    goal = get_goal_by_id(goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    milestone_data = {
        "goal_id": goal_id,
        "milestone_number": request.milestone_number,
        "title": request.title,
        "description": request.description,
        "target_amount": request.target_amount,
        "target_date": request.target_date.isoformat() if request.target_date else None,
        "status": "pending"
    }

    milestone_id = add_milestone(milestone_data)
    if not milestone_id:
        raise HTTPException(status_code=500, detail="Failed to create milestone")

    return MilestoneResponse(
        id=milestone_id,
        goal_id=goal_id,
        milestone_number=request.milestone_number,
        title=request.title,
        description=request.description,
        target_amount=request.target_amount,
        target_date=request.target_date,
        status="pending",
        celebration_shown=False,
        goal_name=goal["name"]
    )


@router.post("/milestones/{milestone_id}/achieve")
async def achieve_milestone_endpoint(
    milestone_id: int,
    actual_amount: Optional[float] = None,
    db=Depends(get_db)
):
    """Mark a milestone as achieved."""
    success = achieve_milestone(milestone_id, actual_amount)
    if not success:
        raise HTTPException(status_code=404, detail="Milestone not found")

    return {"status": "achieved", "milestone_id": milestone_id}


@router.post("/milestones/{milestone_id}/celebration-shown")
async def mark_celebration_shown(milestone_id: int, db=Depends(get_db)):
    """Mark that the celebration was shown for a milestone."""
    success = mark_milestone_celebration_shown(milestone_id)
    if not success:
        raise HTTPException(status_code=404, detail="Milestone not found")

    return {"status": "celebration_shown", "milestone_id": milestone_id}


@router.get("/celebrations/pending", response_model=CelebrationsListResponse)
async def get_pending_celebrations_endpoint(db=Depends(get_db)):
    """Get all pending celebrations (achieved milestones not yet celebrated)."""
    celebrations = get_pending_celebrations()

    celebration_responses = [
        CelebrationResponse(
            id=c["id"],
            goal_id=c["goal_id"],
            goal_name=c.get("goal_name", "Goal"),
            milestone_number=c.get("milestone_number", 1),
            title=c["title"],
            description=c.get("description"),
            target_amount=c.get("target_amount"),
            actual_amount=c.get("actual_amount"),
            achieved_at=c.get("achieved_at", "")
        )
        for c in celebrations
    ]

    return CelebrationsListResponse(
        celebrations=celebration_responses,
        total_count=len(celebration_responses)
    )
