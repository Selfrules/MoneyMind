"""Trend schemas for API responses."""
from pydantic import BaseModel
from typing import List, Dict, Optional


class MonthlyTrend(BaseModel):
    """Monthly spending data."""
    month: str
    income: float
    expenses: float
    savings: float


class CategoryTrend(BaseModel):
    """Category spending over time."""
    category_name: str
    category_icon: Optional[str] = None
    monthly_data: List[float]  # Spending per month
    average: float
    trend_percent: Optional[float] = None  # Change vs previous period


class TrendsResponse(BaseModel):
    """Spending trends response."""
    months: List[str]
    monthly_totals: List[MonthlyTrend]
    top_categories: List[CategoryTrend]
    average_monthly_spending: float
    spending_trend_percent: Optional[float] = None
