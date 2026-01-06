"""
Pydantic schemas for Full Financial Report API responses.
"""

from datetime import date
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


class JudgmentEnum(str, Enum):
    excellent = "excellent"
    good = "good"
    warning = "warning"
    critical = "critical"


class SubscriptionActionEnum(str, Enum):
    cancel = "cancel"
    downgrade = "downgrade"
    review = "review"
    keep = "keep"
    negotiate = "negotiate"


class DifficultyEnum(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class ExecutiveSummary(BaseModel):
    health_score: int
    health_grade: str
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate: float
    total_debt: float
    debt_payment_monthly: float
    months_to_debt_free: Optional[int]
    overall_judgment: JudgmentEnum
    key_issues: List[str]
    key_wins: List[str]


class CategorySpendingItem(BaseModel):
    category: str
    icon: str
    amount_current: float
    amount_avg_3m: float
    benchmark: float
    judgment: JudgmentEnum
    variance_percent: float
    notes: str
    suggestion: Optional[str]


class RecurringTypeEnum(str, Enum):
    """Type of recurring expense (v7.0)."""
    subscription = "subscription"  # Netflix, Spotify - easily cancellable
    financing = "financing"        # Agos, loans - contract locked
    essential = "essential"        # Utilities, rent - necessary
    service = "service"            # Cleaning, maintenance - regular service


class CancellabilityEnum(str, Enum):
    """How easy to cancel this expense (v7.0)."""
    easy = "easy"      # Can cancel anytime (subscriptions)
    medium = "medium"  # Some friction (services)
    hard = "hard"      # Necessary expense (utilities)
    locked = "locked"  # Contract bound (financing)


class SubscriptionAuditItem(BaseModel):
    name: str
    category: str
    monthly_cost: float
    annual_cost: float
    action: SubscriptionActionEnum
    reason: str
    potential_savings: float
    value_score: int
    alternative: Optional[str]
    # v7.0 - Type classification
    recurring_type: Optional[RecurringTypeEnum] = RecurringTypeEnum.subscription
    cancellability: Optional[CancellabilityEnum] = CancellabilityEnum.easy


class DebtPriorityItem(BaseModel):
    id: int
    name: str
    balance: float
    apr: float
    monthly_payment: float
    interest_monthly: float
    principal_monthly: float
    priority_score: int
    months_remaining: int
    payoff_date: Optional[str]
    total_remaining_cost: float


class RecommendationItem(BaseModel):
    id: str
    title: str
    description: str
    impact_monthly: float
    impact_annual: float
    difficulty: DifficultyEnum
    category: str
    action_steps: List[str]
    priority: int


class MonthComparisonItem(BaseModel):
    category: str
    current_month: float
    previous_month: float
    delta: float
    delta_percent: float
    trend: str


class FullFinancialReport(BaseModel):
    report_date: str
    month: str
    executive_summary: ExecutiveSummary
    category_spending: List[CategorySpendingItem]
    subscription_audit: List[SubscriptionAuditItem]
    debt_priority: List[DebtPriorityItem]
    recommendations: List[RecommendationItem]
    month_comparison: List[MonthComparisonItem]
