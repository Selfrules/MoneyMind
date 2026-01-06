"""Budget schemas for API responses."""
from pydantic import BaseModel
from typing import Optional, List


class BudgetStatusResponse(BaseModel):
    """Budget status for a category."""
    category_id: int
    category_name: str
    category_icon: Optional[str] = None
    budget_amount: float
    spent_amount: float
    remaining: float
    percent_used: float
    status: str  # ok, warning, exceeded


class BudgetSummaryResponse(BaseModel):
    """Budget summary for a month."""
    month: str
    total_budget: float
    total_spent: float
    total_remaining: float
    categories: List[BudgetStatusResponse]
    over_budget_count: int
    warning_count: int


# ============================================================================
# Fixed vs Discretionary Budget Schemas (v7.0)
# ============================================================================

class CategoryBudgetResponse(BaseModel):
    """Budget status for a single category in fixed/discretionary breakdown."""
    category: str
    budget_type: str  # 'fixed' or 'discretionary'
    monthly_budget: float
    spent_this_month: float
    remaining: float
    days_left_in_month: int
    daily_budget_remaining: float
    percent_used: float
    status: str  # 'on_track', 'warning', 'over_budget'


class FixedDiscretionaryResponse(BaseModel):
    """Fixed vs Discretionary budget breakdown."""
    month: str
    total_income: float
    total_fixed: float
    total_discretionary_budget: float
    total_discretionary_spent: float
    discretionary_remaining: float
    savings_potential: float
    fixed_breakdown: List[CategoryBudgetResponse]
    discretionary_breakdown: List[CategoryBudgetResponse]
