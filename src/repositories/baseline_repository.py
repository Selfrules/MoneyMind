"""
Baseline Repository for MoneyMind v4.0

Handles baseline snapshot management for comparison including:
- 3-month rolling averages
- Metric-based snapshots
- Baseline vs current comparisons
- Payoff projections
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from .base import BaseRepository, Entity

from src.database import (
    save_baseline_snapshot,
    get_baseline_for_month,
    compare_to_baseline,
    get_db_context,
)


@dataclass
class BaselineSnapshot(Entity):
    """Baseline snapshot entity for metric comparison."""
    snapshot_month: Optional[str] = None  # YYYY-MM
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    metric_type: Optional[str] = None  # spending, income, savings, payoff_projection
    avg_value_3mo: float = 0.0
    calculation_start_month: Optional[str] = None
    calculation_end_month: Optional[str] = None
    projected_payoff_date: Optional[date] = None
    projected_payoff_months: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class BaselineComparison:
    """Comparison result between current and baseline."""
    metric_type: str
    baseline_value: float
    current_value: float
    difference: float
    percent_change: float
    is_improvement: bool
    category_id: Optional[int] = None
    category_name: Optional[str] = None


class BaselineRepository(BaseRepository[BaselineSnapshot]):
    """Repository for baseline snapshot operations."""

    def get_by_id(self, entity_id: int) -> Optional[BaselineSnapshot]:
        """Get baseline by ID - not typically used."""
        return None

    def get_all(self, **filters) -> List[BaselineSnapshot]:
        """
        Get baselines with optional filters.

        Filters:
            month: str (YYYY-MM)
            metric_type: str
        """
        month = filters.get("month")
        metric_type = filters.get("metric_type")

        if not month:
            return []

        baselines = get_baseline_for_month(month, metric_type)
        return [self._entity_from_dict(b) for b in baselines]

    def get_for_month(self, month: str, metric_type: str = None) -> List[BaselineSnapshot]:
        """Get all baselines for a specific month."""
        return self.get_all(month=month, metric_type=metric_type)

    def get_spending_baseline(self, month: str) -> Optional[BaselineSnapshot]:
        """Get spending baseline for a month."""
        baselines = self.get_for_month(month, metric_type="spending")
        # Return aggregate baseline (category_id is None)
        for b in baselines:
            if b.category_id is None:
                return b
        return baselines[0] if baselines else None

    def get_savings_baseline(self, month: str) -> Optional[BaselineSnapshot]:
        """Get savings baseline for a month."""
        baselines = self.get_for_month(month, metric_type="savings")
        for b in baselines:
            if b.category_id is None:
                return b
        return baselines[0] if baselines else None

    def get_payoff_projection(self, month: str) -> Optional[BaselineSnapshot]:
        """Get payoff projection baseline for a month."""
        baselines = self.get_for_month(month, metric_type="payoff_projection")
        return baselines[0] if baselines else None

    def add(self, entity: BaselineSnapshot) -> int:
        """Add a new baseline snapshot."""
        data = self._entity_to_dict(entity)
        return save_baseline_snapshot(data)

    def save(self, snapshot_month: str, metric_type: str, avg_value: float,
             category_id: int = None, start_month: str = None,
             end_month: str = None, notes: str = None) -> int:
        """Convenience method to save a baseline snapshot."""
        snapshot = BaselineSnapshot(
            snapshot_month=snapshot_month,
            category_id=category_id,
            metric_type=metric_type,
            avg_value_3mo=avg_value,
            calculation_start_month=start_month,
            calculation_end_month=end_month,
            notes=notes,
        )
        return self.add(snapshot)

    def save_payoff_projection(self, snapshot_month: str,
                                projected_date: date,
                                projected_months: int,
                                notes: str = None) -> int:
        """Save a payoff projection baseline."""
        data = {
            "snapshot_month": snapshot_month,
            "metric_type": "payoff_projection",
            "projected_payoff_date": projected_date.isoformat(),
            "projected_payoff_months": projected_months,
            "notes": notes,
        }
        return save_baseline_snapshot(data)

    def update(self, entity_id: int, updates: Dict[str, Any]) -> bool:
        """Update baseline - typically create new instead."""
        return False

    def delete(self, entity_id: int) -> bool:
        """Delete baseline - typically not done."""
        return False

    def compare(self, current_month: str, baseline_month: str) -> Dict[str, BaselineComparison]:
        """Compare current month to baseline month."""
        result = compare_to_baseline(current_month, baseline_month)
        comparisons = {}

        for metric_type, data in result.items():
            baseline_val = data.get("baseline", 0)
            current_val = data.get("current", 0)
            diff = current_val - baseline_val

            # Determine if change is improvement based on metric type
            if metric_type in ("spending",):
                is_improvement = diff < 0  # Lower spending is better
            else:
                is_improvement = diff > 0  # Higher savings/income is better

            percent = (diff / baseline_val * 100) if baseline_val != 0 else 0

            comparisons[metric_type] = BaselineComparison(
                metric_type=metric_type,
                baseline_value=baseline_val,
                current_value=current_val,
                difference=diff,
                percent_change=percent,
                is_improvement=is_improvement,
            )

        return comparisons

    def get_trend(self, months: int = 6, metric_type: str = "spending") -> List[Dict[str, Any]]:
        """Get baseline trend over multiple months."""
        from datetime import datetime
        from dateutil.relativedelta import relativedelta

        result = []
        current = datetime.now()

        for i in range(months):
            month_date = current - relativedelta(months=i)
            month_str = month_date.strftime("%Y-%m")
            baselines = get_baseline_for_month(month_str, metric_type)

            if baselines:
                # Get aggregate baseline (category_id is None)
                for b in baselines:
                    if b.get("category_id") is None:
                        result.append({
                            "month": month_str,
                            "value": b.get("avg_value_3mo", 0),
                            "metric_type": metric_type
                        })
                        break

        return list(reversed(result))

    def get_improvement_summary(self, current_month: str,
                                 baseline_month: str) -> Dict[str, Any]:
        """Get a summary of improvements vs baseline."""
        comparisons = self.compare(current_month, baseline_month)

        improvements = []
        declines = []

        for metric, comp in comparisons.items():
            if comp.is_improvement:
                improvements.append({
                    "metric": metric,
                    "change": comp.difference,
                    "percent": comp.percent_change
                })
            else:
                declines.append({
                    "metric": metric,
                    "change": comp.difference,
                    "percent": comp.percent_change
                })

        return {
            "improvements": improvements,
            "declines": declines,
            "net_positive": len(improvements) > len(declines),
            "total_savings_delta": comparisons.get("spending", BaselineComparison(
                metric_type="spending", baseline_value=0, current_value=0,
                difference=0, percent_change=0, is_improvement=False
            )).difference * -1  # Negative spending change = positive savings
        }

    def _entity_from_dict(self, data: Dict[str, Any]) -> BaselineSnapshot:
        """Convert database dict to BaselineSnapshot entity."""
        return BaselineSnapshot(
            id=data.get("id"),
            snapshot_month=data.get("snapshot_month"),
            category_id=data.get("category_id"),
            category_name=data.get("category_name"),
            metric_type=data.get("metric_type"),
            avg_value_3mo=data.get("avg_value_3mo", 0),
            calculation_start_month=data.get("calculation_start_month"),
            calculation_end_month=data.get("calculation_end_month"),
            projected_payoff_date=self._parse_date(data.get("projected_payoff_date")),
            projected_payoff_months=data.get("projected_payoff_months"),
            notes=data.get("notes"),
            created_at=self._parse_datetime(data.get("created_at")),
        )

    def _entity_to_dict(self, entity: BaselineSnapshot) -> Dict[str, Any]:
        """Convert BaselineSnapshot entity to dict for storage."""
        return {
            "snapshot_month": entity.snapshot_month,
            "category_id": entity.category_id,
            "metric_type": entity.metric_type,
            "avg_value_3mo": entity.avg_value_3mo,
            "calculation_start_month": entity.calculation_start_month,
            "calculation_end_month": entity.calculation_end_month,
            "projected_payoff_date": entity.projected_payoff_date.isoformat()
                if entity.projected_payoff_date else None,
            "projected_payoff_months": entity.projected_payoff_months,
            "notes": entity.notes,
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
