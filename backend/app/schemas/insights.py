"""
Insights schemas.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class InsightSeverity(str, Enum):
    """Severity level of an insight."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class InsightType(str, Enum):
    """Type of insight."""
    SPENDING_ANOMALY = "spending_anomaly"
    BUDGET_OVERRUN = "budget_overrun"
    RECURRING_OPPORTUNITY = "recurring_opportunity"
    DEBT_ACCELERATION = "debt_acceleration"
    SAVINGS_INCREASE = "savings_increase"


class Insight(BaseModel):
    """A financial insight."""
    id: int
    type: str
    category: Optional[str]
    severity: InsightSeverity
    title: str
    message: str
    action_text: Optional[str]
    is_read: bool
    is_dismissed: bool
    created_at: datetime

    # Related category info
    category_name: Optional[str]
    category_icon: Optional[str]


class InsightsResponse(BaseModel):
    """Response for insights list."""
    insights: list[Insight]
    unread_count: int
    total_count: int
