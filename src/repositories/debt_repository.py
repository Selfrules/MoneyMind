"""
Debt Repository for MoneyMind v4.0

Handles debt management and monthly payment plans including:
- Debt CRUD operations
- Monthly payment plan generation
- Strategy-based ordering (Avalanche/Snowball)
- Payoff projections
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .base import BaseRepository, Entity, EntityNotFoundError

from src.database import (
    get_debts,
    get_debt_by_id,
    add_debt,
    update_debt,
    delete_debt,
    get_total_debt,
    create_debt_monthly_plan,
    get_debt_plans_for_month,
    update_plan_actual_payment,
    update_plan_status,
    get_debt_plan_history,
    get_db_context,
)


@dataclass
class Debt(Entity):
    """Debt entity."""
    name: Optional[str] = None
    type: Optional[str] = None  # personal_loan, credit_card, mortgage, etc.
    original_amount: float = 0.0
    current_balance: float = 0.0
    interest_rate: float = 0.0
    monthly_payment: float = 0.0
    payment_day: int = 1
    is_active: bool = True
    start_date: Optional[date] = None
    expected_payoff_date: Optional[date] = None


@dataclass
class DebtMonthlyPlan(Entity):
    """Monthly payment plan for a debt."""
    month: Optional[str] = None
    debt_id: Optional[int] = None
    debt_name: Optional[str] = None
    planned_payment: float = 0.0
    extra_payment: float = 0.0
    actual_payment: Optional[float] = None
    order_in_strategy: int = 0
    strategy_type: str = "avalanche"
    projected_payoff_date: Optional[date] = None
    status: str = "planned"
    notes: Optional[str] = None


class DebtRepository(BaseRepository[Debt]):
    """Repository for debt and monthly plan operations."""

    def get_by_id(self, entity_id: int) -> Optional[Debt]:
        """Get debt by ID."""
        data = get_debt_by_id(entity_id)
        if data:
            return self._entity_from_dict(data)
        return None

    def get_all(self, **filters) -> List[Debt]:
        """
        Get debts with optional filters.

        Filters:
            active_only: bool (default True)
        """
        active_only = filters.get("active_only", True)
        debts = get_debts(active_only=active_only)
        return [self._entity_from_dict(d) for d in debts]

    def get_active(self) -> List[Debt]:
        """Get only active debts."""
        return self.get_all(active_only=True)

    def add(self, entity: Debt) -> int:
        """Add a new debt."""
        data = self._entity_to_dict(entity)
        return add_debt(data)

    def update(self, entity_id: int, updates: Dict[str, Any]) -> bool:
        """Update debt."""
        return update_debt(entity_id, updates)

    def delete(self, entity_id: int) -> bool:
        """Delete debt."""
        return delete_debt(entity_id)

    def get_total_balance(self) -> float:
        """Get total balance across all active debts."""
        return get_total_debt()

    def update_balance(self, entity_id: int, new_balance: float) -> bool:
        """Update debt balance after payment."""
        return self.update(entity_id, {"current_balance": new_balance})

    # Monthly Plan Operations

    def create_monthly_plan(self, plan: DebtMonthlyPlan) -> int:
        """Create a monthly payment plan for a debt."""
        data = self._plan_to_dict(plan)
        return create_debt_monthly_plan(data)

    def get_plans_for_month(self, month: str) -> List[DebtMonthlyPlan]:
        """Get all debt plans for a given month."""
        plans = get_debt_plans_for_month(month)
        return [self._plan_from_dict(p) for p in plans]

    def get_plans_with_details(self, month: str) -> List[Dict[str, Any]]:
        """Get plans with full debt details for a month."""
        with get_db_context() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    p.*,
                    d.name as debt_name,
                    d.type as debt_type,
                    d.current_balance,
                    d.interest_rate,
                    d.monthly_payment as min_payment
                FROM debt_monthly_plans p
                JOIN debts d ON p.debt_id = d.id
                WHERE p.month = ?
                ORDER BY p.order_in_strategy
                """,
                (month,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_actual_payment(self, month: str, debt_id: int,
                               actual_payment: float) -> bool:
        """Record actual payment made for a month."""
        return update_plan_actual_payment(month, debt_id, actual_payment)

    def update_plan_status(self, month: str, debt_id: int, status: str) -> bool:
        """Update plan status (planned, on_track, behind, ahead, completed)."""
        return update_plan_status(month, debt_id, status)

    def get_plan_history(self, debt_id: int, months: int = 12) -> List[DebtMonthlyPlan]:
        """Get payment plan history for a debt."""
        history = get_debt_plan_history(debt_id, months)
        return [self._plan_from_dict(p) for p in history]

    def calculate_plan_status(self, plan: DebtMonthlyPlan) -> str:
        """Calculate status based on planned vs actual payments."""
        if plan.actual_payment is None:
            return "planned"
        total_planned = plan.planned_payment + plan.extra_payment
        if plan.actual_payment >= total_planned * 1.05:
            return "ahead"
        elif plan.actual_payment >= total_planned * 0.95:
            return "on_track"
        else:
            return "behind"

    def _entity_from_dict(self, data: Dict[str, Any]) -> Debt:
        """Convert database dict to Debt entity."""
        return Debt(
            id=data.get("id"),
            name=data.get("name"),
            type=data.get("type"),
            original_amount=data.get("original_amount", 0),
            current_balance=data.get("current_balance", 0),
            interest_rate=data.get("interest_rate", 0),
            monthly_payment=data.get("monthly_payment", 0),
            payment_day=data.get("payment_day", 1),
            is_active=bool(data.get("is_active", 1)),
            start_date=self._parse_date(data.get("start_date")),
            expected_payoff_date=self._parse_date(data.get("expected_payoff_date")),
            created_at=self._parse_datetime(data.get("created_at")),
            updated_at=self._parse_datetime(data.get("updated_at")),
        )

    def _entity_to_dict(self, entity: Debt) -> Dict[str, Any]:
        """Convert Debt entity to dict for storage."""
        return {
            "name": entity.name,
            "type": entity.type,
            "original_amount": entity.original_amount,
            "current_balance": entity.current_balance,
            "interest_rate": entity.interest_rate,
            "monthly_payment": entity.monthly_payment,
            "payment_day": entity.payment_day,
            "is_active": 1 if entity.is_active else 0,
        }

    def _plan_from_dict(self, data: Dict[str, Any]) -> DebtMonthlyPlan:
        """Convert database dict to DebtMonthlyPlan entity."""
        return DebtMonthlyPlan(
            id=data.get("id"),
            month=data.get("month"),
            debt_id=data.get("debt_id"),
            debt_name=data.get("debt_name"),
            planned_payment=data.get("planned_payment", 0),
            extra_payment=data.get("extra_payment", 0),
            actual_payment=data.get("actual_payment"),
            order_in_strategy=data.get("order_in_strategy", 0),
            strategy_type=data.get("strategy_type", "avalanche"),
            projected_payoff_date=self._parse_date(data.get("projected_payoff_date")),
            status=data.get("status", "planned"),
            notes=data.get("notes"),
            created_at=self._parse_datetime(data.get("created_at")),
            updated_at=self._parse_datetime(data.get("updated_at")),
        )

    def _plan_to_dict(self, plan: DebtMonthlyPlan) -> Dict[str, Any]:
        """Convert DebtMonthlyPlan to dict for storage."""
        return {
            "month": plan.month,
            "debt_id": plan.debt_id,
            "planned_payment": plan.planned_payment,
            "extra_payment": plan.extra_payment,
            "order_in_strategy": plan.order_in_strategy,
            "strategy_type": plan.strategy_type,
            "projected_payoff_date": plan.projected_payoff_date.isoformat()
                if plan.projected_payoff_date else None,
            "status": plan.status,
            "notes": plan.notes,
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
