"""Transaction schemas for API responses."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class TransactionResponse(BaseModel):
    """Single transaction."""
    id: str  # SHA256 hash
    date: date
    description: str
    amount: float
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    bank: Optional[str] = None
    account_type: Optional[str] = None
    type: Optional[str] = None
    is_recurring: bool = False


class TransactionGroup(BaseModel):
    """Transactions grouped by date."""
    date: date
    transactions: List[TransactionResponse]
    daily_total: float


class TransactionsResponse(BaseModel):
    """Paginated transactions response."""
    transactions: List[TransactionGroup]
    total_count: int
    total_income: float
    total_expenses: float
    month: str


class MonthSummaryResponse(BaseModel):
    """Monthly summary for quick overview."""
    month: str
    income: float
    expenses: float
    savings: float
    savings_rate: float
    transaction_count: int
