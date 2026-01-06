"""Goals schemas for API responses."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class GoalResponse(BaseModel):
    """Single goal item."""
    id: int
    name: str
    type: str  # emergency_fund, savings, custom
    target_amount: float
    current_amount: float
    priority: int
    status: str  # active, completed, paused
    target_date: Optional[date] = None
    progress_percent: float
    monthly_contribution_needed: Optional[float] = None
    months_remaining: Optional[int] = None


class GoalsSummaryResponse(BaseModel):
    """Summary of all goals."""
    goals: List[GoalResponse]
    total_target: float
    total_current: float
    overall_progress: float
    active_count: int
    completed_count: int


class CreateGoalRequest(BaseModel):
    """Request to create a new goal."""
    name: str
    type: str
    target_amount: float
    current_amount: float = 0
    priority: int = 1
    target_date: Optional[date] = None


class UpdateGoalRequest(BaseModel):
    """Request to update a goal."""
    name: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    target_date: Optional[date] = None


# ============================================================================
# Milestone Schemas
# ============================================================================

class MilestoneResponse(BaseModel):
    """Single milestone item."""
    id: int
    goal_id: int
    milestone_number: int
    title: str
    description: Optional[str] = None
    target_amount: Optional[float] = None
    target_date: Optional[date] = None
    status: str  # pending, achieved, missed
    achieved_at: Optional[str] = None
    actual_amount: Optional[float] = None
    celebration_shown: bool = False
    goal_name: Optional[str] = None


class CreateMilestoneRequest(BaseModel):
    """Request to create a milestone."""
    goal_id: int
    milestone_number: int = 1
    title: str
    description: Optional[str] = None
    target_amount: Optional[float] = None
    target_date: Optional[date] = None


class MilestoneListResponse(BaseModel):
    """List of milestones for a goal."""
    milestones: List[MilestoneResponse]
    total_count: int
    achieved_count: int
    pending_count: int


class CelebrationResponse(BaseModel):
    """Pending celebration item."""
    id: int
    goal_id: int
    goal_name: str
    milestone_number: int
    title: str
    description: Optional[str] = None
    target_amount: Optional[float] = None
    actual_amount: Optional[float] = None
    achieved_at: str


class CelebrationsListResponse(BaseModel):
    """List of pending celebrations."""
    celebrations: List[CelebrationResponse]
    total_count: int
