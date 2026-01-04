"""
Transaction Repository for MoneyMind v4.0

Handles all transaction-related data operations including:
- CRUD operations for transactions
- Monthly aggregations
- Category-based filtering
- Recurring pattern detection support
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .base import BaseRepository, Entity, EntityNotFoundError

# Import database functions
from src.database import (
    get_transactions,
    get_transaction_by_id,
    insert_transaction,
    update_transaction_category,
    delete_transaction,
    get_monthly_summary,
    link_transaction_to_recurring,
)


@dataclass
class Transaction(Entity):
    """Transaction entity."""
    date: Optional[date] = None
    description: Optional[str] = None
    amount: float = 0.0
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    bank: Optional[str] = None
    account_type: Optional[str] = None
    type: Optional[str] = None
    balance: Optional[float] = None
    is_recurring: bool = False
    recurring_expense_id: Optional[int] = None


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for transaction operations."""

    def get_by_id(self, entity_id: int) -> Optional[Transaction]:
        """Get transaction by ID."""
        # Note: get_transaction_by_id expects str id (SHA256)
        data = get_transaction_by_id(str(entity_id))
        if data:
            return self._entity_from_dict(data)
        return None

    def get_by_hash(self, hash_id: str) -> Optional[Transaction]:
        """Get transaction by SHA256 hash ID."""
        data = get_transaction_by_id(hash_id)
        if data:
            return self._entity_from_dict(data)
        return None

    def get_all(self, **filters) -> List[Transaction]:
        """
        Get transactions with optional filters.

        Filters:
            month: str (YYYY-MM format)
            category_id: int
            bank: str
            limit: int
        """
        transactions = get_transactions(
            month=filters.get("month"),
            category_id=filters.get("category_id"),
            bank=filters.get("bank"),
            limit=filters.get("limit", 500)
        )
        return [self._entity_from_dict(t) for t in transactions]

    def get_for_month(self, month: str) -> List[Transaction]:
        """Get all transactions for a specific month (YYYY-MM)."""
        return self.get_all(month=month)

    def get_by_category(self, category_id: int, month: str = None) -> List[Transaction]:
        """Get transactions for a specific category."""
        return self.get_all(category_id=category_id, month=month)

    def add(self, entity: Transaction) -> int:
        """Add a new transaction."""
        data = self._entity_to_dict(entity)
        return insert_transaction(data)

    def add_batch(self, transactions: List[Transaction]) -> int:
        """Add multiple transactions, returns count of added."""
        count = 0
        for tx in transactions:
            try:
                self.add(tx)
                count += 1
            except Exception:
                pass  # Skip duplicates
        return count

    def update(self, entity_id: int, updates: Dict[str, Any]) -> bool:
        """Update transaction (only category update supported)."""
        if "category_id" in updates:
            return update_transaction_category(str(entity_id), updates["category_id"])
        return False

    def update_category(self, entity_id: str, category_id: int) -> bool:
        """Update transaction category."""
        return update_transaction_category(entity_id, category_id)

    def delete(self, entity_id: int) -> bool:
        """Delete transaction."""
        return delete_transaction(str(entity_id))

    def get_monthly_summary(self, month: str) -> Dict[str, Any]:
        """Get summary statistics for a month."""
        return get_monthly_summary(month)

    def link_to_recurring(self, transaction_id: str, recurring_id: int,
                          confidence: float = 1.0) -> bool:
        """Link transaction to a recurring expense pattern."""
        return link_transaction_to_recurring(transaction_id, recurring_id, confidence)

    def get_income_total(self, month: str) -> float:
        """Get total income for a month."""
        summary = get_monthly_summary(month)
        return summary.get("income", 0)

    def get_expense_total(self, month: str) -> float:
        """Get total expenses for a month (positive value)."""
        summary = get_monthly_summary(month)
        return abs(summary.get("expenses", 0))

    def _entity_from_dict(self, data: Dict[str, Any]) -> Transaction:
        """Convert database dict to Transaction entity."""
        return Transaction(
            id=data.get("id"),
            date=self._parse_date(data.get("date")),
            description=data.get("description"),
            amount=data.get("amount", 0),
            category_id=data.get("category_id"),
            category_name=data.get("category_name"),
            category_icon=data.get("category_icon"),
            bank=data.get("bank"),
            account_type=data.get("account_type"),
            type=data.get("type"),
            balance=data.get("balance"),
            is_recurring=bool(data.get("is_recurring", 0)),
            recurring_expense_id=data.get("recurring_expense_id"),
            created_at=self._parse_datetime(data.get("created_at")),
        )

    def _entity_to_dict(self, entity: Transaction) -> Dict[str, Any]:
        """Convert Transaction entity to dict for storage."""
        return {
            "date": entity.date.isoformat() if entity.date else None,
            "description": entity.description,
            "amount": entity.amount,
            "category_id": entity.category_id,
            "bank": entity.bank,
            "account_type": entity.account_type,
            "type": entity.type,
            "balance": entity.balance,
            "is_recurring": 1 if entity.is_recurring else 0,
            "recurring_expense_id": entity.recurring_expense_id,
        }

    @staticmethod
    def _parse_date(value) -> Optional[date]:
        """Parse date from string or return as-is if already date."""
        if value is None:
            return None
        if isinstance(value, date):
            return value
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_datetime(value) -> Optional[datetime]:
        """Parse datetime from string or return as-is."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None
