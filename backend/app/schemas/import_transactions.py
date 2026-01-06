"""Import transactions schemas for API."""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date


class ImportedTransaction(BaseModel):
    """Single imported transaction preview."""
    id: str
    date: date
    description: str
    amount: float
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    bank: str
    type: Optional[str] = None


class ImportResponse(BaseModel):
    """Response after importing transactions."""
    success: bool
    total_parsed: int
    categorized_count: int
    imported_count: int
    duplicates_skipped: int
    categories_breakdown: Dict[str, int]
    sample_transactions: List[ImportedTransaction]
    message: str


class ImportPreviewResponse(BaseModel):
    """Preview response before confirming import."""
    total_transactions: int
    date_range: str
    income_total: float
    expenses_total: float
    categories_breakdown: Dict[str, int]
    sample_transactions: List[ImportedTransaction]
