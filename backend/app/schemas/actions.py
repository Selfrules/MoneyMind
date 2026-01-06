"""
Daily actions schemas.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from enum import Enum


class ActionStatus(str, Enum):
    """Status of a daily action."""
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    POSTPONED = "postponed"


class ActionType(str, Enum):
    """Type of action."""
    REVIEW_SUBSCRIPTION = "review_subscription"
    INCREASE_PAYMENT = "increase_payment"
    CUT_CATEGORY = "cut_category"
    CONFIRM_BUDGET = "confirm_budget"
    CHECK_SPENDING = "check_spending"


class ImpactType(str, Enum):
    """Impact type."""
    SAVINGS = "savings"
    PAYOFF_ACCELERATION = "payoff_acceleration"
    BUDGET_CONTROL = "budget_control"


class DailyAction(BaseModel):
    """A daily action task."""
    id: int
    action_date: date
    priority: int  # 1 = highest
    title: str
    description: Optional[str]
    action_type: Optional[str]
    impact_type: Optional[str]
    estimated_impact_monthly: Optional[float]
    estimated_impact_payoff_days: Optional[int]
    status: ActionStatus
    completed_at: Optional[datetime]

    # Related entities
    category_name: Optional[str]
    debt_name: Optional[str]
    recurring_expense_name: Optional[str]


class DailyActionsResponse(BaseModel):
    """Response for today's actions."""
    date: date
    actions: list[DailyAction]
    completed_count: int
    pending_count: int


class CompleteActionRequest(BaseModel):
    """Request to complete an action."""
    decision: str  # "accepted", "rejected", "postponed"
    notes: Optional[str] = None
