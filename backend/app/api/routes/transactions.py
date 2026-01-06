"""Transaction API routes."""
import sys
from pathlib import Path

# Add project root to path for importing src modules
ROUTES_DIR = Path(__file__).parent  # routes/
API_DIR = ROUTES_DIR.parent  # api/
APP_DIR = API_DIR.parent  # app/
BACKEND_DIR = APP_DIR.parent  # backend/
PROJECT_DIR = BACKEND_DIR.parent  # MoneyMind/
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime
from collections import defaultdict

from app.schemas.transactions import (
    TransactionResponse,
    TransactionGroup,
    TransactionsResponse,
)
from app.api.deps import get_db
from src.repositories.transaction_repository import TransactionRepository


router = APIRouter()


@router.get("/transactions/test")
async def test_transactions():
    """Test endpoint."""
    from src.repositories.transaction_repository import TransactionRepository
    repo = TransactionRepository()
    txs = repo.get_for_month("2026-01")
    return {
        "count": len(txs),
        "first_id": str(txs[0].id) if txs else None,
        "first_date": str(txs[0].date) if txs else None,
    }


@router.get("/transactions")
async def get_transactions_endpoint(
    month: Optional[str] = Query(None, description="Month in YYYY-MM format"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
):
    """Get transactions for a month, grouped by date."""
    try:
        # Default to current month
        if not month:
            month = datetime.now().strftime("%Y-%m")

        repo = TransactionRepository()

        # Get transactions
        if category_id:
            transactions = repo.get_by_category(category_id, month)
        else:
            transactions = repo.get_for_month(month)

        # Group by date
        grouped = defaultdict(list)
        for tx in transactions:
            grouped[tx.date].append(tx)

        # Build response
        transaction_groups = []
        total_income = 0.0
        total_expenses = 0.0

        for date_key in sorted(grouped.keys(), reverse=True):
            txs = grouped[date_key]
            daily_total = sum(tx.amount for tx in txs)

            transaction_groups.append(TransactionGroup(
                date=date_key,
                transactions=[
                    TransactionResponse(
                        id=str(tx.id) if tx.id else "",
                        date=tx.date,
                        description=tx.description or "",
                        amount=tx.amount,
                        category_id=tx.category_id,
                        category_name=tx.category_name,
                        category_icon=tx.category_icon,
                        bank=tx.bank,
                        account_type=tx.account_type,
                        type=tx.type,
                        is_recurring=tx.is_recurring or False,
                    )
                    for tx in sorted(txs, key=lambda x: x.amount)
                ],
                daily_total=daily_total
            ))

            for tx in txs:
                if tx.amount > 0:
                    total_income += tx.amount
                else:
                    total_expenses += abs(tx.amount)

        return TransactionsResponse(
            transactions=transaction_groups,
            total_count=len(transactions),
            total_income=total_income,
            total_expenses=total_expenses,
            month=month
        )
    except Exception as e:
        import traceback
        print(f"Error in get_transactions: {e}")
        traceback.print_exc()
        raise
