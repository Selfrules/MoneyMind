"""
Decision Repository for MoneyMind v4.0

Handles user financial decision lifecycle including:
- Decision creation and tracking
- Impact verification
- Status management
- Decision history analytics
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .base import BaseRepository, Entity

from src.database import (
    add_decision,
    update_decision,
    get_decisions,
    get_decision_by_id,
    get_pending_decisions,
    verify_decision_impact,
)


@dataclass
class Decision(Entity):
    """User financial decision entity."""
    decision_date: Optional[date] = None
    type: Optional[str] = None  # taglio_spesa, aumento_rata, cambio_fornitore, cancella_abbonamento, nuovo_budget
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    debt_id: Optional[int] = None
    debt_name: Optional[str] = None
    recurring_expense_id: Optional[int] = None
    recurring_name: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    status: str = "pending"  # pending, accepted, rejected, postponed, completed
    expected_impact_monthly: Optional[float] = None
    expected_impact_payoff_days: Optional[int] = None
    actual_impact_monthly: Optional[float] = None
    actual_impact_verified: bool = False
    verification_date: Optional[date] = None
    verification_notes: Optional[str] = None
    insight_id: Optional[int] = None


class DecisionRepository(BaseRepository[Decision]):
    """Repository for decision operations."""

    def get_by_id(self, entity_id: int) -> Optional[Decision]:
        """Get decision by ID."""
        data = get_decision_by_id(entity_id)
        if data:
            return self._entity_from_dict(data)
        return None

    def get_all(self, **filters) -> List[Decision]:
        """
        Get decisions with optional filters.

        Filters:
            status: str
            limit: int (default 50)
        """
        status = filters.get("status")
        limit = filters.get("limit", 50)
        decisions = get_decisions(status=status, limit=limit)
        return [self._entity_from_dict(d) for d in decisions]

    def get_pending(self) -> List[Decision]:
        """Get all pending decisions."""
        decisions = get_pending_decisions()
        return [self._entity_from_dict(d) for d in decisions]

    def get_by_status(self, status: str) -> List[Decision]:
        """Get decisions by status."""
        return self.get_all(status=status)

    def get_completed(self, limit: int = 50) -> List[Decision]:
        """Get completed decisions."""
        return self.get_all(status="completed", limit=limit)

    def get_verified(self, limit: int = 50) -> List[Decision]:
        """Get decisions that have been impact-verified."""
        all_completed = self.get_completed(limit=limit)
        return [d for d in all_completed if d.actual_impact_verified]

    def add(self, entity: Decision) -> int:
        """Add a new decision."""
        data = self._entity_to_dict(entity)
        return add_decision(data)

    def update(self, entity_id: int, updates: Dict[str, Any]) -> bool:
        """Update decision."""
        return update_decision(entity_id, updates)

    def delete(self, entity_id: int) -> bool:
        """Delete decision (typically not used - status change preferred)."""
        return self.update(entity_id, {"status": "deleted"})

    def accept(self, entity_id: int) -> bool:
        """Accept a pending decision."""
        return self.update(entity_id, {"status": "accepted"})

    def reject(self, entity_id: int) -> bool:
        """Reject a pending decision."""
        return self.update(entity_id, {"status": "rejected"})

    def postpone(self, entity_id: int) -> bool:
        """Postpone a pending decision."""
        return self.update(entity_id, {"status": "postponed"})

    def complete(self, entity_id: int) -> bool:
        """Mark decision as completed."""
        return self.update(entity_id, {"status": "completed"})

    def verify_impact(self, entity_id: int, actual_impact: float,
                      notes: str = None) -> bool:
        """Verify actual impact of a completed decision."""
        return verify_decision_impact(entity_id, actual_impact, notes)

    def get_total_expected_impact(self) -> Dict[str, float]:
        """Get total expected impact from accepted decisions."""
        decisions = self.get_by_status("accepted")
        return {
            "monthly_savings": sum(d.expected_impact_monthly or 0 for d in decisions),
            "payoff_days_reduced": sum(d.expected_impact_payoff_days or 0 for d in decisions)
        }

    def get_total_verified_impact(self) -> Dict[str, float]:
        """Get total verified impact from completed decisions."""
        verified = self.get_verified()
        return {
            "monthly_savings": sum(d.actual_impact_monthly or 0 for d in verified),
            "decisions_count": len(verified)
        }

    def get_by_type(self, decision_type: str) -> List[Decision]:
        """Get decisions by type."""
        all_decisions = self.get_all(limit=200)
        return [d for d in all_decisions if d.type == decision_type]

    def get_for_category(self, category_id: int) -> List[Decision]:
        """Get decisions related to a category."""
        all_decisions = self.get_all(limit=200)
        return [d for d in all_decisions if d.category_id == category_id]

    def get_for_debt(self, debt_id: int) -> List[Decision]:
        """Get decisions related to a debt."""
        all_decisions = self.get_all(limit=200)
        return [d for d in all_decisions if d.debt_id == debt_id]

    def get_recent(self, days: int = 30) -> List[Decision]:
        """Get decisions from the last N days."""
        from datetime import timedelta
        cutoff = date.today() - timedelta(days=days)
        all_decisions = self.get_all(limit=200)
        return [d for d in all_decisions
                if d.decision_date and d.decision_date >= cutoff]

    def _entity_from_dict(self, data: Dict[str, Any]) -> Decision:
        """Convert database dict to Decision entity."""
        return Decision(
            id=data.get("id"),
            decision_date=self._parse_date(data.get("decision_date")),
            type=data.get("type"),
            category_id=data.get("category_id"),
            category_name=data.get("category_name"),
            debt_id=data.get("debt_id"),
            debt_name=data.get("debt_name"),
            recurring_expense_id=data.get("recurring_expense_id"),
            recurring_name=data.get("recurring_name"),
            amount=data.get("amount"),
            description=data.get("description"),
            status=data.get("status", "pending"),
            expected_impact_monthly=data.get("expected_impact_monthly"),
            expected_impact_payoff_days=data.get("expected_impact_payoff_days"),
            actual_impact_monthly=data.get("actual_impact_monthly"),
            actual_impact_verified=bool(data.get("actual_impact_verified", 0)),
            verification_date=self._parse_date(data.get("verification_date")),
            verification_notes=data.get("verification_notes"),
            insight_id=data.get("insight_id"),
            created_at=self._parse_datetime(data.get("created_at")),
            updated_at=self._parse_datetime(data.get("updated_at")),
        )

    def _entity_to_dict(self, entity: Decision) -> Dict[str, Any]:
        """Convert Decision entity to dict for storage."""
        return {
            "decision_date": entity.decision_date.isoformat()
                if entity.decision_date else date.today().isoformat(),
            "type": entity.type,
            "category_id": entity.category_id,
            "debt_id": entity.debt_id,
            "recurring_expense_id": entity.recurring_expense_id,
            "amount": entity.amount,
            "description": entity.description,
            "status": entity.status,
            "expected_impact_monthly": entity.expected_impact_monthly,
            "expected_impact_payoff_days": entity.expected_impact_payoff_days,
            "insight_id": entity.insight_id,
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
