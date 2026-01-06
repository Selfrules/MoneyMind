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

    def get_debt_phase_progress(self) -> Dict[str, Any]:
        """
        Calculate debt payoff phase progress.

        Returns progress through the debt-free journey:
        - Phase 1: First debt eliminated (25%)
        - Phase 2: Half of debts eliminated (50%)
        - Phase 3: Only one debt remaining (75%)
        - Phase 4: Debt-free (100%)

        Returns:
            Dict with phase info, progress percentage, and next milestone
        """
        debts = get_debts(active_only=False)  # Get all debts, including paid off

        if not debts:
            return {
                "phase": "no_debts",
                "phase_number": 0,
                "progress_percent": 100,
                "next_milestone": None,
                "debts_total": 0,
                "debts_eliminated": 0,
                "debts_remaining": 0,
                "is_debt_free": True,
                "message": "Nessun debito registrato",
            }

        active_debts = [d for d in debts if d.get("is_active", True) and d.get("current_balance", 0) > 0]
        eliminated_debts = [d for d in debts if not d.get("is_active", True) or d.get("current_balance", 0) <= 0]

        total_count = len(debts)
        eliminated_count = len(eliminated_debts)
        remaining_count = len(active_debts)

        # Calculate progress
        elimination_progress = (eliminated_count / total_count * 100) if total_count > 0 else 0

        # Determine phase and next milestone
        if remaining_count == 0:
            phase = "debt_free"
            phase_number = 4
            progress = 100
            next_milestone = None
            message = "Sei debt-free! Congratulazioni!"
        elif remaining_count == 1:
            phase = "final_push"
            phase_number = 3
            progress = 75 + (25 * (1 - active_debts[0].get("current_balance", 0) / active_debts[0].get("original_amount", 1)))
            next_milestone = {
                "title": "Ultimo debito",
                "debt_name": active_debts[0].get("name", "Debito"),
                "remaining": active_debts[0].get("current_balance", 0),
            }
            message = "Ultimo debito da eliminare!"
        elif eliminated_count >= total_count / 2:
            phase = "momentum"
            phase_number = 2
            progress = 50 + (25 * ((eliminated_count - total_count / 2) / (total_count / 2)))
            next_debt = self._get_next_focus_debt(active_debts)
            next_milestone = {
                "title": "Prossimo debito",
                "debt_name": next_debt.get("name", "Debito") if next_debt else None,
                "remaining": next_debt.get("current_balance", 0) if next_debt else 0,
            }
            message = f"{eliminated_count}/{total_count} debiti eliminati"
        elif eliminated_count >= 1:
            phase = "building"
            phase_number = 1
            progress = 25 + (25 * ((eliminated_count - 1) / max(1, (total_count / 2 - 1))))
            next_debt = self._get_next_focus_debt(active_debts)
            next_milestone = {
                "title": "Prossimo debito",
                "debt_name": next_debt.get("name", "Debito") if next_debt else None,
                "remaining": next_debt.get("current_balance", 0) if next_debt else 0,
            }
            message = f"Primo debito eliminato! {remaining_count} rimanenti"
        else:
            phase = "starting"
            phase_number = 0
            progress = 0 + (25 * (1 - sum(d.get("current_balance", 0) for d in active_debts) / sum(d.get("original_amount", 1) for d in active_debts)))
            focus_debt = self._get_next_focus_debt(active_debts)
            next_milestone = {
                "title": "Primo debito",
                "debt_name": focus_debt.get("name", "Debito") if focus_debt else None,
                "remaining": focus_debt.get("current_balance", 0) if focus_debt else 0,
            }
            message = f"Focus sul primo debito: {focus_debt.get('name', 'Debito')}" if focus_debt else "Inizia il percorso"

        return {
            "phase": phase,
            "phase_number": phase_number,
            "progress_percent": min(100, max(0, progress)),
            "next_milestone": next_milestone,
            "debts_total": total_count,
            "debts_eliminated": eliminated_count,
            "debts_remaining": remaining_count,
            "is_debt_free": remaining_count == 0,
            "message": message,
        }

    def _get_next_focus_debt(self, debts: List[dict]) -> Optional[dict]:
        """Get the next debt to focus on based on strategy."""
        if not debts:
            return None
        sorted_debts = self._sort_debts_by_strategy(debts, self.strategy)
        return sorted_debts[0] if sorted_debts else None

    def get_debt_journey_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the debt-free journey.

        Returns:
            Dict with journey stats, timeline, and progress visualization data
        """
        debts = get_debts(active_only=False)
        phase_progress = self.get_debt_phase_progress()

        total_original = sum(d.get("original_amount", 0) for d in debts)
        total_current = sum(d.get("current_balance", 0) for d in debts if d.get("is_active", True))
        total_paid = total_original - total_current
        overall_progress = (total_paid / total_original * 100) if total_original > 0 else 0

        # Calculate interest paid and saved
        total_min_payments = sum(d.get("monthly_payment", 0) for d in debts if d.get("is_active", True))
        comparison = self.calculate_scenario_comparison()

        # Build timeline milestones
        milestones = []
        sorted_debts = self._sort_debts_by_strategy(
            [d for d in debts if d.get("is_active", True) and d.get("current_balance", 0) > 0],
            self.strategy
        )

        running_months = 0
        for idx, debt in enumerate(sorted_debts):
            balance = debt.get("current_balance", 0)
            payment = debt.get("monthly_payment", 0)
            rate = debt.get("interest_rate", 0)

            months_for_debt = self._estimate_months_to_payoff(balance, payment, rate)
            running_months += months_for_debt

            if running_months < 999:
                milestone_date = date.today() + relativedelta(months=running_months)
                milestones.append({
                    "order": idx + 1,
                    "debt_name": debt.get("name", "Debito"),
                    "estimated_date": milestone_date.isoformat(),
                    "estimated_months": running_months,
                })

        return {
            "phase_info": phase_progress,
            "total_original_debt": total_original,
            "total_current_debt": total_current,
            "total_paid": total_paid,
            "overall_progress_percent": round(overall_progress, 1),
            "monthly_payment": total_min_payments,
            "projected_payoff_date": comparison.moneymind_scenario.get("date"),
            "months_remaining": comparison.moneymind_scenario.get("months", 0),
            "interest_remaining": comparison.moneymind_scenario.get("interest", 0),
            "potential_interest_saved": comparison.interest_saved,
            "milestones": milestones,
        }
