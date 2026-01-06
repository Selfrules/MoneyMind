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
