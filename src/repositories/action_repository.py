"""
Action Repository for MoneyMind v4.0

Handles daily action task management including:
- Full Auto action generation tracking
- Status management
- Impact estimation
- Priority ordering
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .base import BaseRepository, Entity

from src.database import (
    create_daily_action,
    get_today_actions,
    get_pending_action_count,
    complete_daily_action,
    snooze_daily_action,
    get_action_history,
)


@dataclass
class DailyAction(Entity):
    """Daily action task entity."""
    action_date: Optional[date] = None
    priority: int = 1  # 1 = highest
    title: Optional[str] = None
    description: Optional[str] = None
    action_type: Optional[str] = None  # review_subscription, increase_payment, cut_category, confirm_budget
    impact_type: Optional[str] = None  # savings, payoff_acceleration, budget_control
    estimated_impact_monthly: Optional[float] = None
    estimated_impact_payoff_days: Optional[int] = None
    status: str = "pending"  # pending, completed, snoozed, dismissed
    completed_at: Optional[datetime] = None
    snoozed_until: Optional[date] = None
    decision_id: Optional[int] = None
    insight_id: Optional[int] = None
    recurring_expense_id: Optional[int] = None
    recurring_name: Optional[str] = None
    debt_id: Optional[int] = None
    debt_name: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None


class ActionRepository(BaseRepository[DailyAction]):
    """Repository for daily action operations."""

    def get_by_id(self, entity_id: int) -> Optional[DailyAction]:
        """Get action by ID."""
        # Query from history
        history = get_action_history(days=30)
        for action in history:
            if action.get("id") == entity_id:
                return self._entity_from_dict(action)
        return None

    def get_all(self, **filters) -> List[DailyAction]:
        """
        Get actions with optional filters.

        Filters:
            date: str (YYYY-MM-DD)
            days: int (for history)
        """
        action_date = filters.get("date")
        days = filters.get("days")

        if days:
            actions = get_action_history(days=days)
        else:
            actions = get_today_actions(date=action_date)

        return [self._entity_from_dict(a) for a in actions]

    def get_today(self, action_date: str = None) -> List[DailyAction]:
        """Get pending actions for today."""
        actions = get_today_actions(date=action_date)
        return [self._entity_from_dict(a) for a in actions]

    def get_pending_count(self, action_date: str = None) -> int:
        """Get count of pending actions for today."""
        return get_pending_action_count(date=action_date)

    def get_history(self, days: int = 30) -> List[DailyAction]:
        """Get action history for the last N days."""
        actions = get_action_history(days=days)
        return [self._entity_from_dict(a) for a in actions]

    def add(self, entity: DailyAction) -> int:
        """Add a new daily action."""
        data = self._entity_to_dict(entity)
        return create_daily_action(data)

    def create(self, title: str, action_type: str, impact_type: str,
               priority: int = 1, description: str = None,
               estimated_impact_monthly: float = None,
               estimated_impact_payoff_days: int = None,
               action_date: date = None,
               category_id: int = None, debt_id: int = None,
               recurring_expense_id: int = None,
               insight_id: int = None) -> int:
        """Convenience method to create an action with parameters."""
        action = DailyAction(
            action_date=action_date or date.today(),
            priority=priority,
            title=title,
            description=description,
            action_type=action_type,
            impact_type=impact_type,
            estimated_impact_monthly=estimated_impact_monthly,
            estimated_impact_payoff_days=estimated_impact_payoff_days,
            category_id=category_id,
            debt_id=debt_id,
            recurring_expense_id=recurring_expense_id,
            insight_id=insight_id,
        )
        return self.add(action)

    def update(self, entity_id: int, updates: Dict[str, Any]) -> bool:
        """Update action."""
        # Daily actions don't have a generic update function
        # Use specific methods like complete or snooze
        return False

    def delete(self, entity_id: int) -> bool:
        """Delete action (dismiss it)."""
        # For daily actions, we dismiss rather than delete
        return self.dismiss(entity_id)

    def complete(self, entity_id: int, decision_id: int = None) -> bool:
        """Complete a daily action, optionally linking to a decision."""
        return complete_daily_action(entity_id, decision_id)

    def snooze(self, entity_id: int, until_date: date) -> bool:
        """Snooze an action until a future date."""
        return snooze_daily_action(entity_id, until_date.isoformat())

    def dismiss(self, entity_id: int) -> bool:
        """Dismiss an action without completing it."""
        # Snooze to far future essentially dismisses it
        far_future = date(2099, 12, 31)
        return self.snooze(entity_id, far_future)

    def get_by_type(self, action_type: str, days: int = 7) -> List[DailyAction]:
        """Get actions by type from recent history."""
        history = self.get_history(days=days)
        return [a for a in history if a.action_type == action_type]

    def get_completed_today(self, action_date: str = None) -> List[DailyAction]:
        """Get completed actions for today."""
        if action_date is None:
            action_date = date.today().isoformat()
        history = self.get_history(days=1)
        return [a for a in history
                if a.status == "completed"
                and a.action_date and a.action_date.isoformat() == action_date]

    def get_total_impact_completed(self, days: int = 30) -> Dict[str, float]:
        """Get total estimated impact from completed actions."""
        history = self.get_history(days=days)
        completed = [a for a in history if a.status == "completed"]
        return {
            "monthly_savings": sum(a.estimated_impact_monthly or 0 for a in completed),
            "payoff_days_reduced": sum(a.estimated_impact_payoff_days or 0 for a in completed),
            "actions_count": len(completed)
        }

    def get_by_priority(self, max_priority: int = 3) -> List[DailyAction]:
        """Get today's high-priority actions."""
        today = self.get_today()
        return [a for a in today if a.priority <= max_priority]

    def _entity_from_dict(self, data: Dict[str, Any]) -> DailyAction:
        """Convert database dict to DailyAction entity."""
        return DailyAction(
            id=data.get("id"),
            action_date=self._parse_date(data.get("action_date")),
            priority=data.get("priority", 1),
            title=data.get("title"),
            description=data.get("description"),
            action_type=data.get("action_type"),
            impact_type=data.get("impact_type"),
            estimated_impact_monthly=data.get("estimated_impact_monthly"),
            estimated_impact_payoff_days=data.get("estimated_impact_payoff_days"),
            status=data.get("status", "pending"),
            completed_at=self._parse_datetime(data.get("completed_at")),
            snoozed_until=self._parse_date(data.get("snoozed_until")),
            decision_id=data.get("decision_id"),
            insight_id=data.get("insight_id"),
            recurring_expense_id=data.get("recurring_expense_id"),
            recurring_name=data.get("recurring_name"),
            debt_id=data.get("debt_id"),
            debt_name=data.get("debt_name"),
            category_id=data.get("category_id"),
            category_name=data.get("category_name"),
            created_at=self._parse_datetime(data.get("created_at")),
        )

    def _entity_to_dict(self, entity: DailyAction) -> Dict[str, Any]:
        """Convert DailyAction entity to dict for storage."""
        return {
            "action_date": entity.action_date.isoformat()
                if entity.action_date else date.today().isoformat(),
            "priority": entity.priority,
            "title": entity.title,
            "description": entity.description,
            "action_type": entity.action_type,
            "impact_type": entity.impact_type,
            "estimated_impact_monthly": entity.estimated_impact_monthly,
            "estimated_impact_payoff_days": entity.estimated_impact_payoff_days,
            "status": entity.status,
            "decision_id": entity.decision_id,
            "insight_id": entity.insight_id,
            "recurring_expense_id": entity.recurring_expense_id,
            "debt_id": entity.debt_id,
            "category_id": entity.category_id,
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
