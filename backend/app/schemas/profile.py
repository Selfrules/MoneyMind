"""Profile schemas for API responses."""
from pydantic import BaseModel
from typing import Optional
from datetime import date


class UserProfileResponse(BaseModel):
    """User profile information."""
    id: int
    income_type: Optional[str] = None
    monthly_net_income: float
    risk_tolerance: Optional[str] = None
    financial_knowledge: Optional[str] = None
    coaching_style: Optional[str] = None
    emergency_fund_target_months: int = 6
    created_at: Optional[str] = None


class UpdateProfileRequest(BaseModel):
    """Request to update user profile."""
    income_type: Optional[str] = None
    monthly_net_income: Optional[float] = None
    risk_tolerance: Optional[str] = None
    financial_knowledge: Optional[str] = None
    coaching_style: Optional[str] = None
    emergency_fund_target_months: Optional[int] = None


class KPIHistoryEntry(BaseModel):
    """Single KPI history entry."""
    month: str
    net_worth: float
    total_debt: float
    savings_rate: float
    dti_ratio: float
    emergency_fund_months: float


class KPIHistoryResponse(BaseModel):
    """KPI history response."""
    entries: list[KPIHistoryEntry]
    months_count: int
    trend_direction: str  # improving, stable, declining


class MonthlyReportResponse(BaseModel):
    """Monthly financial report."""
    month: str
    income: float
    expenses: float
    savings: float
    savings_rate: float
    vs_previous_month_savings: Optional[float] = None
    top_expense_categories: list[dict]
    budget_performance: float  # percent of budgets kept
    debt_payments_made: float
    debt_balance_reduction: float
    insights_generated: int
    actions_completed: int
    actions_total: int


class ImportResultResponse(BaseModel):
    """Result of transaction import."""
    success: bool
    imported_count: int
    skipped_count: int
    errors: list[str]
    categories_assigned: dict[str, int]
