"""Recurring expense schemas for API responses."""
from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import date


class RecurringExpenseResponse(BaseModel):
    """Single recurring expense."""
    id: int
    pattern_name: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    frequency: str  # monthly, quarterly, annual
    avg_amount: float
    last_amount: Optional[float] = None
    trend_percent: Optional[float] = None
    last_occurrence: Optional[date] = None
    occurrence_count: int
    provider: Optional[str] = None
    is_essential: bool
    optimization_status: str
    optimization_suggestion: Optional[str] = None
    estimated_savings_monthly: Optional[float] = None
    # New fields for FASE 2
    next_due_date: Optional[date] = None
    days_until_due: Optional[int] = None
    budget_impact_percent: Optional[float] = None
    ai_action: Optional[Literal["keep", "cancel", "renegotiate", "review"]] = None
    ai_reason: Optional[str] = None
    ai_priority: Optional[Literal["high", "medium", "low"]] = None


class RecurringSummaryResponse(BaseModel):
    """Summary of recurring expenses."""
    total_monthly: float
    essential_monthly: float
    non_essential_monthly: float
    potential_savings: float
    expenses: List[RecurringExpenseResponse]
    optimizable_count: int
    # New fields for FASE 2
    due_this_month_count: int = 0
    due_this_month_total: float = 0.0
    high_priority_actions: int = 0
