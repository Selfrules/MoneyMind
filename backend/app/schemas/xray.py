"""
Financial X-Ray schemas for API responses.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class CashFlowBreakdown(BaseModel):
    """Monthly cash flow breakdown by type."""
    income: float
    essential_expenses: float
    debt_payments: float
    discretionary: float
    available_for_savings: float
    total_expenses: float
    savings_rate: float


class DebtDetail(BaseModel):
    """Information about a single debt."""
    id: int
    name: str
    balance: float
    rate: float
    payment: float
    burden_percent: float


class HighestRateDebt(BaseModel):
    """The debt with highest interest rate."""
    name: str
    rate: float
    balance: float


class DebtAnalysis(BaseModel):
    """Analysis of all debts."""
    total_debt: float
    total_monthly_payments: float
    total_interest_paid_ytd: float
    total_interest_remaining: float
    debt_burden_percent: float
    months_to_freedom: Optional[int]
    freedom_date: Optional[str]  # ISO date string
    highest_rate_debt: Optional[HighestRateDebt]
    debts: List[DebtDetail]


class SavingOpportunity(BaseModel):
    """A potential area for savings."""
    category: str
    current: float
    baseline: float
    potential_savings: float
    impact_monthly: float
    impact_annual: float
    recommendation: str
    priority: int


class RiskIndicators(BaseModel):
    """Financial risk assessment indicators."""
    dti_ratio: float
    emergency_fund_months: float
    savings_rate: float
    status: str  # "low", "moderate", "high", "critical"
    issues: List[str]


class PhaseInfo(BaseModel):
    """Current phase in the financial freedom journey."""
    current_phase: str  # "diagnosi", "ottimizzazione", "sicurezza", "crescita"
    progress_percent: float
    next_milestone: str
    days_in_phase: int


class XRayResponse(BaseModel):
    """Complete Financial X-Ray response."""
    analysis_date: str  # ISO date string
    month: str
    cash_flow: CashFlowBreakdown
    debt_analysis: DebtAnalysis
    savings_potential: List[SavingOpportunity]
    risk_indicators: RiskIndicators
    phase: str
    phase_info: PhaseInfo
    health_score: int
    health_grade: str
    summary: str
