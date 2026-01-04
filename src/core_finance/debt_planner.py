"""
Debt Planner for MoneyMind v4.0

Generates monthly debt payment plans using Avalanche or Snowball strategy.
Calculates scenario comparisons and tracks on-track/behind/ahead status.

Strategies:
- Avalanche: Highest interest rate first (saves most money)
- Snowball: Smallest balance first (psychological wins)
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from dateutil.relativedelta import relativedelta

from src.database import (
    get_debts,
    get_debt_by_id,
    create_debt_monthly_plan,
    get_debt_plans_for_month,
    update_plan_actual_payment,
    update_plan_status,
)


@dataclass
class DebtPayment:
    """Planned payment for a single debt in a month."""
    debt_id: int
    debt_name: str
    current_balance: float
    interest_rate: float
    min_payment: float
    planned_payment: float
    extra_payment: float
    order_in_strategy: int
    projected_balance_after: float
    is_focus_debt: bool  # True if this is the debt receiving extra payment


@dataclass
class MonthlyDebtPlan:
    """Complete monthly payment plan for all debts."""
    month: str
    strategy: str
    total_available: float
    total_min_payments: float
    extra_available: float
    payments: List[DebtPayment]
    projected_payoff_date: Optional[date]
    months_remaining: int


@dataclass
class ScenarioComparison:
    """Comparison between current path and MoneyMind optimized path."""
    current_scenario: Dict[str, Any]  # "if I continue like this"
    moneymind_scenario: Dict[str, Any]  # "with MoneyMind optimization"
    months_saved: int
    interest_saved: float
    payoff_date_improvement: int  # days earlier


class DebtPlanner:
    """
    Generates optimized debt payment plans.

    Usage:
        planner = DebtPlanner()
        plan = planner.generate_monthly_plan("2026-01", strategy="avalanche", extra=100)
        planner.save_plan(plan)

        comparison = planner.calculate_scenario_comparison()
    """

    def __init__(self, strategy: str = "avalanche"):
        """
        Initialize planner with default strategy.

        Args:
            strategy: "avalanche" (highest interest first) or "snowball" (smallest balance first)
        """
        self.strategy = strategy

    def generate_monthly_plan(self, month: str, strategy: str = None,
                               extra_payment: float = 0,
                               total_available: float = None) -> MonthlyDebtPlan:
        """
        Generate a monthly payment plan for all active debts.

        Args:
            month: Target month (YYYY-MM)
            strategy: Override default strategy
            extra_payment: Additional amount available beyond min payments
            total_available: Total budget for debt payments (overrides extra_payment)

        Returns:
            MonthlyDebtPlan with all debt payments
        """
        strategy = strategy or self.strategy
        debts = get_debts(active_only=True)

        if not debts:
            return MonthlyDebtPlan(
                month=month,
                strategy=strategy,
                total_available=0,
                total_min_payments=0,
                extra_available=0,
                payments=[],
                projected_payoff_date=None,
                months_remaining=0,
            )

        # Calculate totals
        total_min = sum(d.get("monthly_payment", 0) for d in debts)

        if total_available is not None:
            extra_payment = max(0, total_available - total_min)
        else:
            total_available = total_min + extra_payment

        # Sort debts according to strategy
        sorted_debts = self._sort_debts_by_strategy(debts, strategy)

        # Generate payment plan
        payments = []
        remaining_extra = extra_payment

        for idx, debt in enumerate(sorted_debts):
            debt_id = debt["id"]
            balance = debt.get("current_balance", 0)
            min_payment = debt.get("monthly_payment", 0)
            rate = debt.get("interest_rate", 0)

            # First debt in order gets all extra payment
            if idx == 0 and remaining_extra > 0:
                extra = min(remaining_extra, balance - min_payment)
                extra = max(0, extra)  # Can't be negative
                remaining_extra -= extra
                is_focus = True
            else:
                extra = 0
                is_focus = False

            total_payment = min_payment + extra
            # Don't pay more than balance
            total_payment = min(total_payment, balance)

            # Calculate projected balance
            monthly_interest = (rate / 100 / 12) * balance
            balance_after = balance + monthly_interest - total_payment

            payments.append(DebtPayment(
                debt_id=debt_id,
                debt_name=debt.get("name", ""),
                current_balance=balance,
                interest_rate=rate,
                min_payment=min_payment,
                planned_payment=total_payment,
                extra_payment=extra,
                order_in_strategy=idx + 1,
                projected_balance_after=max(0, balance_after),
                is_focus_debt=is_focus,
            ))

        # Calculate overall projection
        total_debt = sum(d.get("current_balance", 0) for d in debts)
        monthly_paydown = total_available
        months_remaining = self._estimate_months_to_payoff(
            total_debt, monthly_paydown, self._avg_interest_rate(debts)
        )

        payoff_date = None
        if months_remaining > 0:
            payoff_date = date.today() + relativedelta(months=months_remaining)

        return MonthlyDebtPlan(
            month=month,
            strategy=strategy,
            total_available=total_available,
            total_min_payments=total_min,
            extra_available=extra_payment,
            payments=payments,
            projected_payoff_date=payoff_date,
            months_remaining=months_remaining,
        )

    def save_plan(self, plan: MonthlyDebtPlan) -> List[int]:
        """
        Save monthly plan to database.

        Args:
            plan: MonthlyDebtPlan to save

        Returns:
            List of created plan IDs
        """
        created_ids = []

        for payment in plan.payments:
            plan_id = create_debt_monthly_plan({
                "month": plan.month,
                "debt_id": payment.debt_id,
                "planned_payment": payment.planned_payment,
                "extra_payment": payment.extra_payment,
                "order_in_strategy": payment.order_in_strategy,
                "strategy_type": plan.strategy,
                "projected_payoff_date": plan.projected_payoff_date.isoformat()
                    if plan.projected_payoff_date else None,
                "status": "planned",
            })
            created_ids.append(plan_id)

        return created_ids

    def calculate_scenario_comparison(self, extra_monthly: float = 50) -> ScenarioComparison:
        """
        Compare "continue as-is" vs "with MoneyMind optimization".

        Args:
            extra_monthly: Additional monthly payment MoneyMind can help find

        Returns:
            ScenarioComparison with savings potential
        """
        debts = get_debts(active_only=True)
        if not debts:
            return ScenarioComparison(
                current_scenario={"months": 0, "interest": 0, "date": None},
                moneymind_scenario={"months": 0, "interest": 0, "date": None},
                months_saved=0,
                interest_saved=0,
                payoff_date_improvement=0,
            )

        total_debt = sum(d.get("current_balance", 0) for d in debts)
        total_min = sum(d.get("monthly_payment", 0) for d in debts)
        avg_rate = self._avg_interest_rate(debts)

        # Current scenario: just minimum payments
        current_months = self._estimate_months_to_payoff(total_debt, total_min, avg_rate)
        current_interest = self._estimate_total_interest(total_debt, total_min, avg_rate, current_months)
        current_date = date.today() + relativedelta(months=current_months) if current_months else None

        # MoneyMind scenario: optimized payments with extra
        mm_payment = total_min + extra_monthly
        mm_months = self._estimate_months_to_payoff(total_debt, mm_payment, avg_rate)
        mm_interest = self._estimate_total_interest(total_debt, mm_payment, avg_rate, mm_months)
        mm_date = date.today() + relativedelta(months=mm_months) if mm_months else None

        months_saved = current_months - mm_months if current_months and mm_months else 0
        interest_saved = current_interest - mm_interest

        days_improvement = 0
        if current_date and mm_date:
            days_improvement = (current_date - mm_date).days

        return ScenarioComparison(
            current_scenario={
                "months": current_months,
                "interest": round(current_interest, 2),
                "date": current_date.isoformat() if current_date else None,
                "monthly_payment": total_min,
            },
            moneymind_scenario={
                "months": mm_months,
                "interest": round(mm_interest, 2),
                "date": mm_date.isoformat() if mm_date else None,
                "monthly_payment": mm_payment,
            },
            months_saved=months_saved,
            interest_saved=round(interest_saved, 2),
            payoff_date_improvement=days_improvement,
        )

    def get_on_track_status(self, month: str) -> Dict[str, Any]:
        """
        Calculate if we're on track, behind, or ahead of plan.

        Args:
            month: Month to check (YYYY-MM)

        Returns:
            Dict with status and details
        """
        plans = get_debt_plans_for_month(month)

        if not plans:
            return {
                "status": "no_plan",
                "message": "No plan for this month",
                "behind_count": 0,
                "on_track_count": 0,
                "ahead_count": 0,
            }

        behind = on_track = ahead = planned = 0

        for plan in plans:
            actual = plan.get("actual_payment")
            planned_total = plan.get("planned_payment", 0) + plan.get("extra_payment", 0)

            if actual is None:
                planned += 1
            elif actual >= planned_total * 1.05:
                ahead += 1
            elif actual >= planned_total * 0.95:
                on_track += 1
            else:
                behind += 1

        # Overall status
        if planned == len(plans):
            status = "planned"
            message = "Payments not yet recorded"
        elif behind > 0:
            status = "behind"
            message = f"{behind} debt(s) behind schedule"
        elif ahead > 0 and on_track >= 0:
            status = "ahead"
            message = f"Ahead of schedule on {ahead} debt(s)"
        else:
            status = "on_track"
            message = "All payments on track"

        return {
            "status": status,
            "message": message,
            "behind_count": behind,
            "on_track_count": on_track,
            "ahead_count": ahead,
            "planned_count": planned,
        }

    def replan_month(self, month: str, actual_available: float) -> MonthlyDebtPlan:
        """
        Re-generate plan based on actual available funds.

        Useful when income or expenses differ from expected.

        Args:
            month: Month to replan
            actual_available: Actual amount available for debt payments

        Returns:
            New MonthlyDebtPlan based on actual budget
        """
        return self.generate_monthly_plan(
            month=month,
            strategy=self.strategy,
            total_available=actual_available,
        )

    def _sort_debts_by_strategy(self, debts: List[dict], strategy: str) -> List[dict]:
        """Sort debts according to strategy."""
        if strategy == "avalanche":
            # Highest interest rate first
            return sorted(debts, key=lambda d: d.get("interest_rate", 0), reverse=True)
        elif strategy == "snowball":
            # Smallest balance first
            return sorted(debts, key=lambda d: d.get("current_balance", 0))
        else:
            # Default: avalanche
            return sorted(debts, key=lambda d: d.get("interest_rate", 0), reverse=True)

    def _avg_interest_rate(self, debts: List[dict]) -> float:
        """Calculate weighted average interest rate."""
        if not debts:
            return 0
        total_balance = sum(d.get("current_balance", 0) for d in debts)
        if total_balance == 0:
            return 0
        weighted_rate = sum(
            d.get("current_balance", 0) * d.get("interest_rate", 0)
            for d in debts
        ) / total_balance
        return weighted_rate

    def _estimate_months_to_payoff(self, principal: float, monthly_payment: float,
                                    annual_rate: float) -> int:
        """
        Estimate months to pay off debt with compound interest.

        Uses the formula for loan amortization.
        """
        if monthly_payment <= 0 or principal <= 0:
            return 0

        monthly_rate = annual_rate / 100 / 12

        if monthly_rate == 0:
            # No interest, simple division
            return int(principal / monthly_payment) + 1

        # Check if payment covers interest
        monthly_interest = principal * monthly_rate
        if monthly_payment <= monthly_interest:
            # Payment doesn't cover interest, can't pay off
            return 999  # Effectively infinite

        # Loan amortization formula
        import math
        try:
            months = math.log(monthly_payment / (monthly_payment - principal * monthly_rate)) / math.log(1 + monthly_rate)
            return int(math.ceil(months))
        except (ValueError, ZeroDivisionError):
            return 999

    def _estimate_total_interest(self, principal: float, monthly_payment: float,
                                  annual_rate: float, months: int) -> float:
        """Estimate total interest paid over the loan term."""
        if months <= 0 or months >= 999:
            return 0
        total_paid = monthly_payment * months
        return max(0, total_paid - principal)

    def get_debt_priority_order(self, strategy: str = None) -> List[Dict[str, Any]]:
        """
        Get debts in priority order for the given strategy.

        Useful for UI display of focus debt.
        """
        strategy = strategy or self.strategy
        debts = get_debts(active_only=True)
        sorted_debts = self._sort_debts_by_strategy(debts, strategy)

        return [
            {
                "order": idx + 1,
                "debt_id": d["id"],
                "name": d.get("name", ""),
                "balance": d.get("current_balance", 0),
                "interest_rate": d.get("interest_rate", 0),
                "is_focus": idx == 0,
            }
            for idx, d in enumerate(sorted_debts)
        ]
