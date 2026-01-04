"""
Budget Repository for MoneyMind v4.0

Handles budget management including:
- CRUD operations for budgets
- Budget vs actual comparisons
- Category-level budget operations
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import BaseRepository, Entity

from src.database import (
    get_budgets,
    set_budget,
    get_spending_by_category,
    get_db_context,
)


@dataclass
class Budget(Entity):
    """Budget entity."""
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    amount: float = 0.0
    month: Optional[str] = None  # YYYY-MM format


@dataclass
class BudgetStatus(Entity):
    """Budget status with spending comparison."""
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    budget_amount: float = 0.0
    spent_amount: float = 0.0
    remaining: float = 0.0
    percent_used: float = 0.0
    status: str = "ok"  # ok, warning, exceeded


class BudgetRepository(BaseRepository[Budget]):
    """Repository for budget operations."""

    def get_by_id(self, entity_id: int) -> Optional[Budget]:
        """Get budget by ID."""
        with get_db_context() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT b.*, c.name as category_name, c.icon as category_icon
                FROM budgets b
                JOIN categories c ON b.category_id = c.id
                WHERE b.id = ?
                """,
                (entity_id,)
            )
            row = cursor.fetchone()
            return self._entity_from_dict(dict(row)) if row else None

    def get_all(self, **filters) -> List[Budget]:
        """
        Get budgets with optional filters.

        Filters:
            month: str (YYYY-MM format)
        """
        month = filters.get("month")
        budgets = get_budgets(month=month)
        return [self._entity_from_dict(b) for b in budgets]

    def get_for_month(self, month: str) -> List[Budget]:
        """Get all budgets for a specific month."""
        return self.get_all(month=month)

    def get_for_category(self, category_id: int, month: str) -> Optional[Budget]:
        """Get budget for a specific category and month."""
        with get_db_context() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT b.*, c.name as category_name, c.icon as category_icon
                FROM budgets b
                JOIN categories c ON b.category_id = c.id
                WHERE b.category_id = ? AND b.month = ?
                """,
                (category_id, month)
            )
            row = cursor.fetchone()
            return self._entity_from_dict(dict(row)) if row else None

    def add(self, entity: Budget) -> int:
        """Add or update a budget (upsert behavior)."""
        return set_budget(
            category_id=entity.category_id,
            amount=entity.amount,
            month=entity.month
        )

    def set(self, category_id: int, amount: float, month: str) -> int:
        """Set budget for a category (convenience method)."""
        return set_budget(
            category_id=category_id,
            amount=amount,
            month=month
        )

    def update(self, entity_id: int, updates: Dict[str, Any]) -> bool:
        """Update budget amount."""
        budget = self.get_by_id(entity_id)
        if not budget:
            return False
        new_amount = updates.get("amount", budget.amount)
        self.set(budget.category_id, new_amount, budget.month)
        return True

    def delete(self, entity_id: int) -> bool:
        """Delete budget by ID."""
        with get_db_context() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM budgets WHERE id = ?", (entity_id,))
            return cursor.rowcount > 0

    def delete_for_category(self, category_id: int, month: str) -> bool:
        """Delete budget for a specific category and month."""
        with get_db_context() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM budgets WHERE category_id = ? AND month = ?",
                (category_id, month)
            )
            return cursor.rowcount > 0

    def get_summary(self, month: str) -> Dict[str, Any]:
        """Get budget summary with spending comparison."""
        budgets = get_budgets(month=month)
        spending = get_spending_by_category(month)

        # Create spending lookup
        spending_map = {s["category_id"]: abs(s.get("total", 0)) for s in spending}

        total_budget = sum(b.get("amount", 0) for b in budgets)
        total_spent = sum(spending_map.values())

        by_category = []
        for b in budgets:
            cat_id = b["category_id"]
            spent = spending_map.get(cat_id, 0)
            by_category.append({
                "category_id": cat_id,
                "category_name": b.get("category_name", ""),
                "category_icon": b.get("category_icon", ""),
                "budget": b.get("amount", 0),
                "spent": spent,
                "remaining": b.get("amount", 0) - spent,
            })

        return {
            "total_budget": total_budget,
            "total_spent": total_spent,
            "remaining": total_budget - total_spent,
            "by_category": by_category
        }

    def get_status_list(self, month: str) -> List[BudgetStatus]:
        """Get budget status for all categories with spending."""
        summary = self.get_summary(month)
        result = []

        for item in summary.get("by_category", []):
            budget_amount = item.get("budget", 0)
            spent = item.get("spent", 0)
            remaining = budget_amount - spent
            percent = (spent / budget_amount * 100) if budget_amount > 0 else 0

            # Determine status
            if percent >= 100:
                status = "exceeded"
            elif percent >= 80:
                status = "warning"
            else:
                status = "ok"

            result.append(BudgetStatus(
                category_id=item.get("category_id"),
                category_name=item.get("category_name"),
                category_icon=item.get("category_icon"),
                budget_amount=budget_amount,
                spent_amount=spent,
                remaining=remaining,
                percent_used=percent,
                status=status
            ))

        return result

    def get_over_budget_categories(self, month: str) -> List[BudgetStatus]:
        """Get categories that are over budget."""
        statuses = self.get_status_list(month)
        return [s for s in statuses if s.status == "exceeded"]

    def get_warning_categories(self, month: str) -> List[BudgetStatus]:
        """Get categories approaching budget limit (80%+)."""
        statuses = self.get_status_list(month)
        return [s for s in statuses if s.status in ("warning", "exceeded")]

    def copy_budgets_to_month(self, from_month: str, to_month: str) -> int:
        """Copy budgets from one month to another."""
        budgets = self.get_for_month(from_month)
        count = 0
        for budget in budgets:
            self.set(budget.category_id, budget.amount, to_month)
            count += 1
        return count

    def _entity_from_dict(self, data: Dict[str, Any]) -> Budget:
        """Convert database dict to Budget entity."""
        return Budget(
            id=data.get("id"),
            category_id=data.get("category_id"),
            category_name=data.get("category_name"),
            category_icon=data.get("category_icon"),
            amount=data.get("amount", 0),
            month=data.get("month"),
            created_at=self._parse_datetime(data.get("created_at")),
            updated_at=self._parse_datetime(data.get("updated_at")),
        )

    def _entity_to_dict(self, entity: Budget) -> Dict[str, Any]:
        """Convert Budget entity to dict for storage."""
        return {
            "category_id": entity.category_id,
            "amount": entity.amount,
            "month": entity.month,
        }

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
