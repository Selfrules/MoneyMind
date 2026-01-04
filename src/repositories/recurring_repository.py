"""
Recurring Expense Repository for MoneyMind v4.0

Handles recurring expense pattern management including:
- Pattern detection and storage
- Optimization tracking
- Provider identification
- Trend analysis
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .base import BaseRepository, Entity

from src.database import (
    add_recurring_expense,
    update_recurring_expense,
    get_recurring_expenses,
    get_recurring_expense_by_id,
    set_recurring_optimization,
    get_recurring_summary,
    get_db_context,
)


@dataclass
class RecurringExpense(Entity):
    """Recurring expense pattern entity."""
    pattern_name: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    frequency: str = "monthly"  # monthly, quarterly, annual
    avg_amount: float = 0.0
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    last_amount: Optional[float] = None
    trend_percent: Optional[float] = None  # % change over 6 months
    first_occurrence: Optional[date] = None
    last_occurrence: Optional[date] = None
    occurrence_count: int = 0
    provider: Optional[str] = None
    is_essential: bool = False
    is_active: bool = True
    optimization_status: str = "not_reviewed"  # not_reviewed, optimized, no_action, reviewing
    optimization_suggestion: Optional[str] = None
    estimated_savings_monthly: Optional[float] = None
    confidence_score: float = 0.0


class RecurringRepository(BaseRepository[RecurringExpense]):
    """Repository for recurring expense operations."""

    def get_by_id(self, entity_id: int) -> Optional[RecurringExpense]:
        """Get recurring expense by ID."""
        data = get_recurring_expense_by_id(entity_id)
        if data:
            return self._entity_from_dict(data)
        return None

    def get_all(self, **filters) -> List[RecurringExpense]:
        """
        Get recurring expenses with optional filters.

        Filters:
            active_only: bool (default True)
            category_id: int
        """
        active_only = filters.get("active_only", True)
        category_id = filters.get("category_id")
        recurring = get_recurring_expenses(
            active_only=active_only,
            category_id=category_id
        )
        return [self._entity_from_dict(r) for r in recurring]

    def get_active(self) -> List[RecurringExpense]:
        """Get only active recurring expenses."""
        return self.get_all(active_only=True)

    def get_by_category(self, category_id: int) -> List[RecurringExpense]:
        """Get recurring expenses for a category."""
        return self.get_all(category_id=category_id)

    def get_optimizable(self) -> List[RecurringExpense]:
        """Get recurring expenses that can be optimized (non-essential, not reviewed)."""
        all_recurring = self.get_active()
        return [r for r in all_recurring
                if not r.is_essential and r.optimization_status == "not_reviewed"]

    def add(self, entity: RecurringExpense) -> int:
        """Add a new recurring expense pattern."""
        data = self._entity_to_dict(entity)
        return add_recurring_expense(data)

    def update(self, entity_id: int, updates: Dict[str, Any]) -> bool:
        """Update recurring expense."""
        return update_recurring_expense(entity_id, updates)

    def delete(self, entity_id: int) -> bool:
        """Delete recurring expense."""
        with get_db_context() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM recurring_expenses WHERE id = ?", (entity_id,))
            return cursor.rowcount > 0

    def deactivate(self, entity_id: int) -> bool:
        """Mark recurring expense as inactive (soft delete)."""
        return self.update(entity_id, {"is_active": 0})

    def set_optimization(self, entity_id: int, status: str,
                         suggestion: str = None, savings: float = None) -> bool:
        """Set optimization status and suggestion."""
        return set_recurring_optimization(entity_id, status, suggestion, savings)

    def mark_as_essential(self, entity_id: int, is_essential: bool = True) -> bool:
        """Mark recurring expense as essential/non-essential."""
        return self.update(entity_id, {"is_essential": 1 if is_essential else 0})

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of recurring expenses."""
        return get_recurring_summary()

    def get_total_monthly(self) -> float:
        """Get total monthly recurring expenses."""
        summary = get_recurring_summary()
        return summary.get("total_monthly", 0)

    def get_potential_savings(self) -> float:
        """Get total potential monthly savings from optimization suggestions."""
        all_recurring = self.get_active()
        return sum(r.estimated_savings_monthly or 0 for r in all_recurring
                   if r.optimization_status == "not_reviewed")

    def get_by_provider(self, provider: str) -> List[RecurringExpense]:
        """Get recurring expenses by provider name."""
        all_recurring = self.get_active()
        provider_lower = provider.lower()
        return [r for r in all_recurring
                if r.provider and provider_lower in r.provider.lower()]

    def update_occurrence(self, entity_id: int, amount: float,
                          occurrence_date: date) -> bool:
        """Update recurring expense with new occurrence data."""
        recurring = self.get_by_id(entity_id)
        if not recurring:
            return False

        new_count = recurring.occurrence_count + 1
        # Calculate new average
        if recurring.avg_amount and recurring.occurrence_count > 0:
            new_avg = ((recurring.avg_amount * recurring.occurrence_count) + amount) / new_count
        else:
            new_avg = amount

        updates = {
            "last_amount": amount,
            "avg_amount": new_avg,
            "occurrence_count": new_count,
            "last_occurrence": occurrence_date.isoformat(),
        }

        # Update min/max
        if recurring.min_amount is None or amount < recurring.min_amount:
            updates["min_amount"] = amount
        if recurring.max_amount is None or amount > recurring.max_amount:
            updates["max_amount"] = amount

        return self.update(entity_id, updates)

    def _entity_from_dict(self, data: Dict[str, Any]) -> RecurringExpense:
        """Convert database dict to RecurringExpense entity."""
        return RecurringExpense(
            id=data.get("id"),
            pattern_name=data.get("pattern_name"),
            category_id=data.get("category_id"),
            category_name=data.get("category_name"),
            category_icon=data.get("category_icon"),
            frequency=data.get("frequency", "monthly"),
            avg_amount=data.get("avg_amount", 0),
            min_amount=data.get("min_amount"),
            max_amount=data.get("max_amount"),
            last_amount=data.get("last_amount"),
            trend_percent=data.get("trend_percent"),
            first_occurrence=self._parse_date(data.get("first_occurrence")),
            last_occurrence=self._parse_date(data.get("last_occurrence")),
            occurrence_count=data.get("occurrence_count", 0),
            provider=data.get("provider"),
            is_essential=bool(data.get("is_essential", 0)),
            is_active=bool(data.get("is_active", 1)),
            optimization_status=data.get("optimization_status", "not_reviewed"),
            optimization_suggestion=data.get("optimization_suggestion"),
            estimated_savings_monthly=data.get("estimated_savings_monthly"),
            confidence_score=data.get("confidence_score", 0),
            created_at=self._parse_datetime(data.get("created_at")),
            updated_at=self._parse_datetime(data.get("updated_at")),
        )

    def _entity_to_dict(self, entity: RecurringExpense) -> Dict[str, Any]:
        """Convert RecurringExpense entity to dict for storage."""
        return {
            "pattern_name": entity.pattern_name,
            "category_id": entity.category_id,
            "frequency": entity.frequency,
            "avg_amount": entity.avg_amount,
            "min_amount": entity.min_amount,
            "max_amount": entity.max_amount,
            "last_amount": entity.last_amount,
            "trend_percent": entity.trend_percent,
            "first_occurrence": entity.first_occurrence.isoformat()
                if entity.first_occurrence else None,
            "last_occurrence": entity.last_occurrence.isoformat()
                if entity.last_occurrence else None,
            "occurrence_count": entity.occurrence_count,
            "provider": entity.provider,
            "is_essential": 1 if entity.is_essential else 0,
            "is_active": 1 if entity.is_active else 0,
            "optimization_status": entity.optimization_status,
            "optimization_suggestion": entity.optimization_suggestion,
            "estimated_savings_monthly": entity.estimated_savings_monthly,
            "confidence_score": entity.confidence_score,
        }

    @staticmethod
    def _parse_date(value) -> Optional[date]:
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
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None
