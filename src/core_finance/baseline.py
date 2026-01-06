"""
Baseline Calculator for MoneyMind v4.0

Calculates 3-month rolling averages for spending, income, and savings.
Used for comparison with current month to show improvement/decline.

Key Metrics:
- Spending baseline: Average expenses over past 3 months
- Income baseline: Average income over past 3 months
- Savings baseline: Average (income - expenses) over past 3 months
- Payoff projection: "If I continue like this" scenario
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from dateutil.relativedelta import relativedelta

from src.database import (
    get_db_context,
    get_monthly_summary,
    get_debts,
    save_baseline_snapshot,
    get_baseline_for_month,
)


@dataclass
class BaselineMetrics:
    """Calculated baseline metrics for a reference month."""
    reference_month: str
    avg_spending_3mo: float
    avg_income_3mo: float
    avg_savings_3mo: float
    projected_payoff_months: Optional[int]
    projected_payoff_date: Optional[date]
    calculation_start: str
    calculation_end: str


@dataclass
class BaselineComparison:
    """Comparison of current month vs baseline."""
    current_month: str
    baseline_month: str
    spending_delta: float  # Positive = spending more (bad)
    income_delta: float    # Positive = earning more (good)
    savings_delta: float   # Positive = saving more (good)
    spending_percent_change: float
    income_percent_change: float
    savings_percent_change: float
    is_improving: bool     # Overall assessment
    status: str            # "better", "same", "worse"


class BaselineCalculator:
    """
    Calculator for 3-month baseline metrics.

    Usage:
        calc = BaselineCalculator()
        baseline = calc.calculate_3mo_baseline("2026-01")
        calc.save_baseline(baseline)

        comparison = calc.compare_to_baseline("2026-01", baseline)
    """

    def calculate_3mo_baseline(self, reference_month: str) -> BaselineMetrics:
        """
        Calculate 3-month baseline ending at the month before reference_month.

        Args:
            reference_month: The month to calculate baseline FOR (YYYY-MM)
                            Baseline uses 3 months BEFORE this month

        Returns:
            BaselineMetrics with averages and projections
        """
        ref_date = datetime.strptime(reference_month + "-01", "%Y-%m-%d")

        # Get the 3 months before reference month
        months_to_average = []
        for i in range(1, 4):  # 1, 2, 3 months before
            month_date = ref_date - relativedelta(months=i)
            months_to_average.append(month_date.strftime("%Y-%m"))

        # Calculate averages
        total_spending = 0.0
        total_income = 0.0
        months_with_data = 0

        for month in months_to_average:
            summary = get_monthly_summary(month)
            # Keys are total_income, total_expenses from database.py
            income = summary.get("total_income", 0) or summary.get("income", 0)
            expenses = summary.get("total_expenses", 0) or summary.get("expenses", 0)
            if expenses != 0 or income != 0:
                total_spending += abs(expenses)
                total_income += income
                months_with_data += 1

        if months_with_data == 0:
            # No data available
            return BaselineMetrics(
                reference_month=reference_month,
                avg_spending_3mo=0,
                avg_income_3mo=0,
                avg_savings_3mo=0,
                projected_payoff_months=None,
                projected_payoff_date=None,
                calculation_start=months_to_average[-1],
                calculation_end=months_to_average[0],
            )

        avg_spending = total_spending / months_with_data
        avg_income = total_income / months_with_data
        avg_savings = avg_income - avg_spending

        # Calculate payoff projection
        payoff_months, payoff_date = self._calculate_payoff_projection(avg_savings)

        return BaselineMetrics(
            reference_month=reference_month,
            avg_spending_3mo=round(avg_spending, 2),
            avg_income_3mo=round(avg_income, 2),
            avg_savings_3mo=round(avg_savings, 2),
            projected_payoff_months=payoff_months,
            projected_payoff_date=payoff_date,
            calculation_start=months_to_average[-1],
            calculation_end=months_to_average[0],
        )

    def _calculate_payoff_projection(self, monthly_savings: float) -> tuple:
        """
        Calculate debt payoff projection based on average monthly savings.

        Simplified model: total_debt / monthly_available_for_debt

        Returns:
            (months_to_payoff, payoff_date) or (None, None) if can't payoff
        """
        debts = get_debts(active_only=True)
        if not debts:
            return (0, date.today())

        total_debt = sum(d.get("current_balance", 0) for d in debts)
        min_payments = sum(d.get("monthly_payment", 0) for d in debts)

        # Available for debt is min(monthly_savings, min_payments) + extra from savings
        if monthly_savings <= 0:
            # Not saving anything, can only make min payments
            available_monthly = min_payments
        else:
            # Can potentially pay more than minimum
            available_monthly = max(min_payments, min(monthly_savings, min_payments * 1.5))

        if available_monthly <= 0:
            return (None, None)

        # Simple calculation (ignoring interest for quick estimate)
        months = int(total_debt / available_monthly) + 1

        payoff_date = date.today() + relativedelta(months=months)

        return (months, payoff_date)

    def save_baseline(self, baseline: BaselineMetrics) -> Dict[int, str]:
        """
        Save baseline metrics to database.

        Saves multiple snapshots:
        - Overall spending baseline
        - Overall income baseline
        - Overall savings baseline
        - Payoff projection

        Returns:
            Dict mapping metric_type to snapshot_id
        """
        saved = {}

        # Save spending baseline
        saved["spending"] = save_baseline_snapshot({
            "snapshot_month": baseline.reference_month,
            "metric_type": "spending",
            "avg_value_3mo": baseline.avg_spending_3mo,
            "calculation_start_month": baseline.calculation_start,
            "calculation_end_month": baseline.calculation_end,
        })

        # Save income baseline
        saved["income"] = save_baseline_snapshot({
            "snapshot_month": baseline.reference_month,
            "metric_type": "income",
            "avg_value_3mo": baseline.avg_income_3mo,
            "calculation_start_month": baseline.calculation_start,
            "calculation_end_month": baseline.calculation_end,
        })

        # Save savings baseline
        saved["savings"] = save_baseline_snapshot({
            "snapshot_month": baseline.reference_month,
            "metric_type": "savings",
            "avg_value_3mo": baseline.avg_savings_3mo,
            "calculation_start_month": baseline.calculation_start,
            "calculation_end_month": baseline.calculation_end,
        })

        # Save payoff projection if available
        if baseline.projected_payoff_months is not None:
            saved["payoff_projection"] = save_baseline_snapshot({
                "snapshot_month": baseline.reference_month,
                "metric_type": "payoff_projection",
                "projected_payoff_months": baseline.projected_payoff_months,
                "projected_payoff_date": baseline.projected_payoff_date.isoformat()
                    if baseline.projected_payoff_date else None,
            })

        return saved

    def compare_to_baseline(self, current_month: str,
                            baseline: BaselineMetrics = None) -> BaselineComparison:
        """
        Compare current month performance to baseline.

        Args:
            current_month: Month to compare (YYYY-MM)
            baseline: Baseline to compare against (if None, loads from DB)

        Returns:
            BaselineComparison with deltas and status
        """
        if baseline is None:
            # Load baseline from database
            baseline = self._load_baseline_from_db(current_month)
            if baseline is None:
                # Calculate fresh baseline
                baseline = self.calculate_3mo_baseline(current_month)

        # Get current month data
        current_summary = get_monthly_summary(current_month)
        current_spending = abs(current_summary.get("total_expenses", 0) or current_summary.get("expenses", 0))
        current_income = current_summary.get("total_income", 0) or current_summary.get("income", 0)
        current_savings = current_income - current_spending

        # Calculate deltas
        spending_delta = current_spending - baseline.avg_spending_3mo
        income_delta = current_income - baseline.avg_income_3mo
        savings_delta = current_savings - baseline.avg_savings_3mo

        # Calculate percent changes
        spending_pct = self._safe_percent(spending_delta, baseline.avg_spending_3mo)
        income_pct = self._safe_percent(income_delta, baseline.avg_income_3mo)
        savings_pct = self._safe_percent(savings_delta, baseline.avg_savings_3mo)

        # Determine overall status
        # Improving if: spending down OR savings up
        is_improving = spending_delta < 0 or savings_delta > 0

        if savings_delta > baseline.avg_savings_3mo * 0.1:  # >10% better
            status = "better"
        elif savings_delta < baseline.avg_savings_3mo * -0.1:  # >10% worse
            status = "worse"
        else:
            status = "same"

        return BaselineComparison(
            current_month=current_month,
            baseline_month=baseline.reference_month,
            spending_delta=round(spending_delta, 2),
            income_delta=round(income_delta, 2),
            savings_delta=round(savings_delta, 2),
            spending_percent_change=round(spending_pct, 1),
            income_percent_change=round(income_pct, 1),
            savings_percent_change=round(savings_pct, 1),
            is_improving=is_improving,
            status=status,
        )

    def _load_baseline_from_db(self, reference_month: str) -> Optional[BaselineMetrics]:
        """Load baseline from database for a given month."""
        baselines = get_baseline_for_month(reference_month)
        if not baselines:
            return None

        # Build BaselineMetrics from stored data
        spending = income = savings = 0.0
        payoff_months = None
        payoff_date = None
        start = end = ""

        for b in baselines:
            metric_type = b.get("metric_type")
            if metric_type == "spending":
                spending = b.get("avg_value_3mo", 0)
                start = b.get("calculation_start_month", "")
                end = b.get("calculation_end_month", "")
            elif metric_type == "income":
                income = b.get("avg_value_3mo", 0)
            elif metric_type == "savings":
                savings = b.get("avg_value_3mo", 0)
            elif metric_type == "payoff_projection":
                payoff_months = b.get("projected_payoff_months")
                payoff_date_str = b.get("projected_payoff_date")
                if payoff_date_str:
                    try:
                        payoff_date = datetime.strptime(payoff_date_str, "%Y-%m-%d").date()
                    except ValueError:
                        pass

        return BaselineMetrics(
            reference_month=reference_month,
            avg_spending_3mo=spending,
            avg_income_3mo=income,
            avg_savings_3mo=savings,
            projected_payoff_months=payoff_months,
            projected_payoff_date=payoff_date,
            calculation_start=start,
            calculation_end=end,
        )

    def get_current_payoff_projection(self) -> Dict[str, Any]:
        """
        Calculate "if I continue like this" projection.

        Returns:
            Dict with payoff_months, payoff_date, total_debt, monthly_available
        """
        today = date.today()
        current_month = today.strftime("%Y-%m")

        # Get 3-month baseline for current spending pattern
        baseline = self.calculate_3mo_baseline(current_month)

        debts = get_debts(active_only=True)
        total_debt = sum(d.get("current_balance", 0) for d in debts)

        return {
            "total_debt": total_debt,
            "avg_monthly_savings": baseline.avg_savings_3mo,
            "payoff_months": baseline.projected_payoff_months,
            "payoff_date": baseline.projected_payoff_date,
            "scenario_type": "continue_as_is",
        }

    @staticmethod
    def _safe_percent(delta: float, baseline: float) -> float:
        """Calculate percentage change safely handling zero baseline."""
        if baseline == 0:
            return 0.0 if delta == 0 else 100.0
        return (delta / baseline) * 100

    def calculate_category_baselines(self, reference_month: str) -> List[Dict[str, Any]]:
        """
        Calculate baselines per category for more detailed analysis.

        Returns:
            List of category baselines with avg spending
        """
        from src.database import get_spending_by_category

        ref_date = datetime.strptime(reference_month + "-01", "%Y-%m-%d")
        months = [(ref_date - relativedelta(months=i)).strftime("%Y-%m") for i in range(1, 4)]

        # Aggregate spending by category across 3 months
        category_totals = {}

        for month in months:
            spending = get_spending_by_category(month)
            for cat in spending:
                cat_id = cat.get("category_id")
                if cat_id not in category_totals:
                    category_totals[cat_id] = {
                        "category_id": cat_id,
                        "category_name": cat.get("category_name", ""),
                        "total": 0,
                        "months_count": 0,
                    }
                category_totals[cat_id]["total"] += abs(cat.get("total", 0))
                category_totals[cat_id]["months_count"] += 1

        # Calculate averages
        result = []
        for cat_id, data in category_totals.items():
            if data["months_count"] > 0:
                result.append({
                    "category_id": cat_id,
                    "category_name": data["category_name"],
                    "avg_spending_3mo": round(data["total"] / data["months_count"], 2),
                    "months_with_data": data["months_count"],
                })

        return sorted(result, key=lambda x: x["avg_spending_3mo"], reverse=True)
