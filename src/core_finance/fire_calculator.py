"""
FIRE (Financial Independence, Retire Early) Calculator.

Provides projections and milestones for financial independence journey.
"""

from dataclasses import dataclass
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional, Any
import math


@dataclass
class FIREProjection:
    """Represents a FIRE projection result."""
    fire_number: float
    years_to_fire: float
    months_to_fire: int
    fire_date: date
    current_net_worth: float
    monthly_investment: float
    expected_return: float
    withdrawal_rate: float
    annual_expenses: float


@dataclass
class FIREMilestone:
    """Represents a FIRE milestone."""
    name: str
    target_amount: float
    target_percent: float  # Percent of FIRE number
    years_to_reach: float
    projected_date: date
    description: str


@dataclass
class MonthlyProjection:
    """Monthly projection data point for charting."""
    month: date
    months_from_now: int
    net_worth: float
    contributions: float
    investment_gains: float
    fire_percent: float


class FIRECalculator:
    """
    Financial Independence, Retire Early projections.

    Uses compound growth formulas to project wealth accumulation
    and calculate time to financial independence.
    """

    DEFAULT_WITHDRAWAL_RATE = 0.04  # 4% rule
    DEFAULT_EXPECTED_RETURN = 0.07  # 7% real return
    DEFAULT_INFLATION_RATE = 0.02  # 2% inflation

    def __init__(
        self,
        current_net_worth: float = 0,
        monthly_investment: float = 0,
        annual_expenses: float = 0,
        expected_return: float = None,
        inflation_rate: float = None,
        withdrawal_rate: float = None
    ):
        """
        Initialize FIRE calculator.

        Args:
            current_net_worth: Current total net worth
            monthly_investment: Monthly investment amount
            annual_expenses: Annual living expenses
            expected_return: Expected annual return rate (default 7%)
            inflation_rate: Expected annual inflation rate (default 2%)
            withdrawal_rate: Safe withdrawal rate (default 4%)
        """
        self.current_net_worth = current_net_worth
        self.monthly_investment = monthly_investment
        self.annual_expenses = annual_expenses
        self.expected_return = expected_return or self.DEFAULT_EXPECTED_RETURN
        self.inflation_rate = inflation_rate or self.DEFAULT_INFLATION_RATE
        self.withdrawal_rate = withdrawal_rate or self.DEFAULT_WITHDRAWAL_RATE

        # Calculate real return (adjusted for inflation)
        self.real_return = self.expected_return - self.inflation_rate

    def calculate_fire_number(
        self,
        annual_expenses: float = None,
        withdrawal_rate: float = None
    ) -> float:
        """
        Calculate FIRE number based on annual expenses and withdrawal rate.

        Uses the formula: FIRE Number = Annual Expenses / Withdrawal Rate
        (e.g., 4% rule means 25x annual expenses)

        Args:
            annual_expenses: Annual living expenses (uses instance default if None)
            withdrawal_rate: Safe withdrawal rate (uses instance default if None)

        Returns:
            FIRE number (target net worth for financial independence)
        """
        expenses = annual_expenses or self.annual_expenses
        swr = withdrawal_rate or self.withdrawal_rate

        if swr <= 0:
            return 0

        return expenses / swr

    def project_to_fire(
        self,
        current_nw: float = None,
        monthly_investment: float = None,
        expected_return: float = None,
        fire_number: float = None
    ) -> FIREProjection:
        """
        Project time to reach FIRE.

        Uses compound growth formula with monthly contributions:
        FV = PV * (1 + r)^n + PMT * ((1 + r)^n - 1) / r

        Solves for n (months to FIRE).

        Args:
            current_nw: Starting net worth
            monthly_investment: Monthly contribution
            expected_return: Annual return rate
            fire_number: Target FIRE number

        Returns:
            FIREProjection with timeline and details
        """
        nw = current_nw if current_nw is not None else self.current_net_worth
        monthly = monthly_investment if monthly_investment is not None else self.monthly_investment
        annual_return = expected_return if expected_return is not None else self.expected_return
        target = fire_number if fire_number is not None else self.calculate_fire_number()

        if target <= 0:
            # No valid target
            return FIREProjection(
                fire_number=0,
                years_to_fire=0,
                months_to_fire=0,
                fire_date=date.today(),
                current_net_worth=nw,
                monthly_investment=monthly,
                expected_return=annual_return,
                withdrawal_rate=self.withdrawal_rate,
                annual_expenses=self.annual_expenses
            )

        if nw >= target:
            # Already FIRE!
            return FIREProjection(
                fire_number=target,
                years_to_fire=0,
                months_to_fire=0,
                fire_date=date.today(),
                current_net_worth=nw,
                monthly_investment=monthly,
                expected_return=annual_return,
                withdrawal_rate=self.withdrawal_rate,
                annual_expenses=self.annual_expenses
            )

        # Monthly rate
        r = annual_return / 12

        if monthly <= 0 and r <= 0:
            # No growth possible
            years = 999
            months = 999 * 12
        elif r <= 0:
            # No returns, just contributions
            months = int((target - nw) / monthly)
            years = months / 12
        else:
            # Solve for months using formula
            # FV = PV * (1+r)^n + PMT * ((1+r)^n - 1) / r = target
            # This requires numerical solving
            months = self._calculate_months_to_target(nw, monthly, r, target)
            years = months / 12

        fire_date = date.today() + relativedelta(months=months)

        return FIREProjection(
            fire_number=target,
            years_to_fire=round(years, 1),
            months_to_fire=months,
            fire_date=fire_date,
            current_net_worth=nw,
            monthly_investment=monthly,
            expected_return=annual_return,
            withdrawal_rate=self.withdrawal_rate,
            annual_expenses=self.annual_expenses
        )

    def _calculate_months_to_target(
        self,
        pv: float,
        pmt: float,
        r: float,
        target: float
    ) -> int:
        """
        Calculate months needed to reach target using binary search.

        Args:
            pv: Present value (starting amount)
            pmt: Monthly payment (contribution)
            r: Monthly interest rate
            target: Target amount

        Returns:
            Number of months to reach target
        """
        if pv >= target:
            return 0

        # Binary search for the number of months
        low, high = 0, 1200  # Max 100 years

        while low < high:
            mid = (low + high) // 2
            fv = self._calculate_future_value(pv, pmt, r, mid)

            if fv >= target:
                high = mid
            else:
                low = mid + 1

        return low

    def _calculate_future_value(
        self,
        pv: float,
        pmt: float,
        r: float,
        n: int
    ) -> float:
        """
        Calculate future value with compound interest and contributions.

        FV = PV * (1+r)^n + PMT * ((1+r)^n - 1) / r

        Args:
            pv: Present value
            pmt: Monthly payment
            r: Monthly interest rate
            n: Number of months

        Returns:
            Future value
        """
        if n == 0:
            return pv

        if r == 0:
            return pv + pmt * n

        compound = (1 + r) ** n
        return pv * compound + pmt * (compound - 1) / r

    def calculate_milestones(
        self,
        fire_number: float = None
    ) -> List[FIREMilestone]:
        """
        Calculate FIRE milestones.

        Milestones:
        - Coast FI (25%): Enough to coast to traditional retirement without saving
        - Barista FI (50%): Can work part-time and cover basic expenses
        - Lean FI (75%): FI with minimal expenses
        - Full FI (100%): Complete financial independence

        Args:
            fire_number: Target FIRE number

        Returns:
            List of FIREMilestone objects
        """
        target = fire_number if fire_number is not None else self.calculate_fire_number()

        milestones_config = [
            {
                "name": "Coast FI",
                "percent": 0.25,
                "description": "Puoi smettere di risparmiare e raggiungerai FI alla pensione"
            },
            {
                "name": "Barista FI",
                "percent": 0.50,
                "description": "Lavoro part-time può coprire le spese di base"
            },
            {
                "name": "Lean FI",
                "percent": 0.75,
                "description": "FI con stile di vita minimalista"
            },
            {
                "name": "Full FI",
                "percent": 1.0,
                "description": "Indipendenza finanziaria completa"
            },
        ]

        milestones = []

        for config in milestones_config:
            milestone_target = target * config["percent"]
            projection = self.project_to_fire(fire_number=milestone_target)

            milestones.append(FIREMilestone(
                name=config["name"],
                target_amount=milestone_target,
                target_percent=config["percent"] * 100,
                years_to_reach=projection.years_to_fire,
                projected_date=projection.fire_date,
                description=config["description"]
            ))

        return milestones

    def sensitivity_analysis(
        self,
        base_projection: FIREProjection = None,
        return_variations: List[float] = None,
        expense_variations: List[float] = None
    ) -> Dict[str, Any]:
        """
        Perform sensitivity analysis on FIRE projections.

        Tests how changes in return rates or expenses affect time to FIRE.

        Args:
            base_projection: Base case projection
            return_variations: Return rate variations to test (e.g., [-0.02, 0, 0.02])
            expense_variations: Expense variations to test (e.g., [-0.10, 0, 0.10])

        Returns:
            Dictionary with sensitivity results
        """
        if base_projection is None:
            base_projection = self.project_to_fire()

        if return_variations is None:
            return_variations = [-0.02, -0.01, 0, 0.01, 0.02]

        if expense_variations is None:
            expense_variations = [-0.20, -0.10, 0, 0.10, 0.20]

        results = {
            "base_case": {
                "years_to_fire": base_projection.years_to_fire,
                "fire_date": base_projection.fire_date.isoformat(),
                "fire_number": base_projection.fire_number,
            },
            "return_sensitivity": [],
            "expense_sensitivity": [],
            "scenarios": {
                "conservative": None,
                "expected": None,
                "optimistic": None,
            }
        }

        # Return sensitivity
        for delta in return_variations:
            new_return = self.expected_return + delta
            if new_return > 0:
                projection = self.project_to_fire(expected_return=new_return)
                results["return_sensitivity"].append({
                    "return_rate": new_return,
                    "delta": delta,
                    "years_to_fire": projection.years_to_fire,
                    "fire_date": projection.fire_date.isoformat(),
                })

        # Expense sensitivity
        for delta in expense_variations:
            new_expenses = self.annual_expenses * (1 + delta)
            new_fire_number = self.calculate_fire_number(annual_expenses=new_expenses)
            projection = self.project_to_fire(fire_number=new_fire_number)
            results["expense_sensitivity"].append({
                "expenses_change": delta,
                "new_expenses": new_expenses,
                "new_fire_number": new_fire_number,
                "years_to_fire": projection.years_to_fire,
                "fire_date": projection.fire_date.isoformat(),
            })

        # Generate three main scenarios
        # Conservative: Lower returns (5%), higher expenses (+10%)
        conservative_return = 0.05
        conservative_expenses = self.annual_expenses * 1.10
        conservative_fire = self.calculate_fire_number(annual_expenses=conservative_expenses)
        conservative_proj = self.project_to_fire(
            expected_return=conservative_return,
            fire_number=conservative_fire
        )
        results["scenarios"]["conservative"] = {
            "return_rate": conservative_return,
            "expenses": conservative_expenses,
            "fire_number": conservative_fire,
            "years_to_fire": conservative_proj.years_to_fire,
            "fire_date": conservative_proj.fire_date.isoformat(),
        }

        # Expected (base case)
        results["scenarios"]["expected"] = {
            "return_rate": self.expected_return,
            "expenses": self.annual_expenses,
            "fire_number": base_projection.fire_number,
            "years_to_fire": base_projection.years_to_fire,
            "fire_date": base_projection.fire_date.isoformat(),
        }

        # Optimistic: Higher returns (9%), lower expenses (-10%)
        optimistic_return = 0.09
        optimistic_expenses = self.annual_expenses * 0.90
        optimistic_fire = self.calculate_fire_number(annual_expenses=optimistic_expenses)
        optimistic_proj = self.project_to_fire(
            expected_return=optimistic_return,
            fire_number=optimistic_fire
        )
        results["scenarios"]["optimistic"] = {
            "return_rate": optimistic_return,
            "expenses": optimistic_expenses,
            "fire_number": optimistic_fire,
            "years_to_fire": optimistic_proj.years_to_fire,
            "fire_date": optimistic_proj.fire_date.isoformat(),
        }

        return results

    def generate_monthly_projections(
        self,
        years: int = 30,
        fire_number: float = None
    ) -> List[MonthlyProjection]:
        """
        Generate month-by-month projections for charting.

        Args:
            years: Number of years to project
            fire_number: Target FIRE number for percentage calculation

        Returns:
            List of MonthlyProjection objects
        """
        target = fire_number if fire_number is not None else self.calculate_fire_number()
        monthly_rate = self.expected_return / 12

        projections = []
        current_value = self.current_net_worth
        total_contributions = self.current_net_worth

        for month in range(years * 12 + 1):
            month_date = date.today() + relativedelta(months=month)

            # Calculate gains for this period
            if month == 0:
                gains = 0
            else:
                gains = current_value * monthly_rate
                current_value += gains + self.monthly_investment
                total_contributions += self.monthly_investment

            fire_percent = (current_value / target * 100) if target > 0 else 0

            projections.append(MonthlyProjection(
                month=month_date,
                months_from_now=month,
                net_worth=round(current_value, 2),
                contributions=round(total_contributions, 2),
                investment_gains=round(current_value - total_contributions, 2),
                fire_percent=round(fire_percent, 2)
            ))

            # Stop if we've reached FIRE
            if current_value >= target and month > 0:
                break

        return projections

    def get_fire_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive FIRE summary for display.

        Returns:
            Dictionary with all FIRE calculations
        """
        fire_number = self.calculate_fire_number()
        projection = self.project_to_fire()
        milestones = self.calculate_milestones()
        sensitivity = self.sensitivity_analysis(projection)

        # Calculate current progress
        progress_percent = (
            (self.current_net_worth / fire_number * 100)
            if fire_number > 0 else 0
        )

        # Monthly savings rate
        monthly_income = (self.annual_expenses + self.monthly_investment * 12) / 12
        savings_rate = (
            (self.monthly_investment / monthly_income * 100)
            if monthly_income > 0 else 0
        )

        return {
            "fire_number": fire_number,
            "current_net_worth": self.current_net_worth,
            "progress_percent": round(progress_percent, 1),
            "years_to_fire": projection.years_to_fire,
            "months_to_fire": projection.months_to_fire,
            "fire_date": projection.fire_date.isoformat(),
            "monthly_investment": self.monthly_investment,
            "annual_expenses": self.annual_expenses,
            "expected_return": self.expected_return,
            "withdrawal_rate": self.withdrawal_rate,
            "savings_rate": round(savings_rate, 1),
            "milestones": [
                {
                    "name": m.name,
                    "target_amount": m.target_amount,
                    "target_percent": m.target_percent,
                    "years_to_reach": m.years_to_reach,
                    "projected_date": m.projected_date.isoformat(),
                    "description": m.description,
                    "is_achieved": self.current_net_worth >= m.target_amount,
                }
                for m in milestones
            ],
            "scenarios": sensitivity["scenarios"],
        }


def calculate_fire_from_profile(
    monthly_income: float,
    monthly_expenses: float,
    current_net_worth: float = 0,
    expected_return: float = 0.07,
    withdrawal_rate: float = 0.04
) -> Dict[str, Any]:
    """
    Convenience function to calculate FIRE from user profile data.

    Args:
        monthly_income: Monthly net income
        monthly_expenses: Monthly expenses
        current_net_worth: Current net worth
        expected_return: Expected annual return
        withdrawal_rate: Safe withdrawal rate

    Returns:
        FIRE summary dictionary
    """
    monthly_savings = monthly_income - monthly_expenses
    annual_expenses = monthly_expenses * 12

    calculator = FIRECalculator(
        current_net_worth=current_net_worth,
        monthly_investment=max(0, monthly_savings),
        annual_expenses=annual_expenses,
        expected_return=expected_return,
        withdrawal_rate=withdrawal_rate
    )

    return calculator.get_fire_summary()
