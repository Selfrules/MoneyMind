"""Debt schemas for API responses."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class PaymentHistoryEntry(BaseModel):
    """Single payment record."""
    date: date
    amount: float
    description: str


class DebtResponse(BaseModel):
    """Single debt item."""
    id: int
    name: str
    type: str
    original_amount: float
    current_balance: float
    interest_rate: float
    monthly_payment: float
    payment_day: int
    start_date: Optional[date] = None
    is_active: bool
    payoff_date: Optional[date] = None
    months_remaining: Optional[int] = None
    total_interest: Optional[float] = None
    # Payment tracking
    payments_made: int = 0
    payments_remaining: int = 0
    total_paid: float = 0.0
    payment_progress_percent: float = 0.0
    payment_history: List[PaymentHistoryEntry] = []
    # Strategy info
    priority_rank: Optional[int] = None
    recommended_strategy: Optional[str] = None


class DebtSummaryResponse(BaseModel):
    """Summary of all debts."""
    total_debt: float
    total_monthly_payment: float
    debts: List[DebtResponse]
    active_count: int
    projected_debt_free_date: Optional[date] = None
    months_to_freedom: Optional[int] = None


class DebtTimelineEntry(BaseModel):
    """Single entry in debt timeline."""
    month: str
    debt_id: int
    debt_name: str
    planned_payment: float
    extra_payment: float
    balance_after: float
    is_payoff_month: bool


class DebtTimelineResponse(BaseModel):
    """Debt payoff timeline."""
    strategy: str  # avalanche or snowball
    timeline: List[DebtTimelineEntry]
    total_months: int
    total_interest_paid: float
    debt_free_date: Optional[date] = None
    monthly_extra_available: float


class MonthlyPlanEntry(BaseModel):
    """Monthly debt payment plan."""
    debt_id: int
    debt_name: str
    planned_payment: float
    extra_payment: float
    actual_payment: Optional[float] = None
    status: str  # pending, completed, partial
    order_in_strategy: int


class MonthlyDebtPlanResponse(BaseModel):
    """Debt payment plan for a specific month."""
    month: str
    strategy_type: str
    total_planned: float
    total_extra: float
    total_actual: float
    entries: List[MonthlyPlanEntry]
