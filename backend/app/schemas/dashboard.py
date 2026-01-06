"""
Dashboard schemas for API responses.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date


class KPIs(BaseModel):
    """Key Performance Indicators."""
    total_balance: float
    monthly_income: float
    monthly_expenses: float
    savings_rate: float
    dti_ratio: float  # Debt-to-Income ratio
    emergency_fund_months: float
    net_worth: float
    total_debt: float


class HealthScore(BaseModel):
    """Financial health score breakdown."""
    total_score: int  # 0-100
    grade: str  # A, B, C, D, F
    savings_score: int  # 0-25
    dti_score: int  # 0-25
    emergency_fund_score: int  # 0-25
    net_worth_trend_score: int  # 0-25
    phase: str  # "Debt Payoff" or "Wealth Building"


class ScenarioComparison(BaseModel):
    """Current vs MoneyMind scenario comparison."""
    current_payoff_date: Optional[date]
    current_payoff_months: Optional[int]
    moneymind_payoff_date: Optional[date]
    moneymind_payoff_months: Optional[int]
    months_saved: Optional[int]
    interest_saved: Optional[float]


class MonthSummary(BaseModel):
    """Current month summary."""
    month: str
    income: float
    expenses: float
    savings: float
    vs_baseline_savings: float  # positive = better than baseline
    on_track: bool


class DashboardResponse(BaseModel):
    """Complete dashboard response."""
    kpis: KPIs
    health_score: HealthScore
    month_summary: MonthSummary
    scenario_comparison: Optional[ScenarioComparison]
    pending_actions_count: int
    unread_insights_count: int
