"""
Scenario Engine for MoneyMind v6.0

What-If scenario simulation for financial decisions:
- Expense changes (increase/decrease categories)
- Income changes (raise, bonus, job loss)
- Extra debt payments
- Lump sum allocations (windfall)

Returns impact on:
- Monthly savings
- Debt payoff timeline
- FIRE date
- Financial health score
"""

from dataclasses import dataclass
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from typing import Optional, List, Dict, Any
from enum import Enum

from src.database import (
    get_debts,
    get_spending_by_category,
    get_user_profile,
    get_transactions,
    get_db_context,
)


class ScenarioType(str, Enum):
    EXPENSE_CHANGE = "expense_change"
    INCOME_CHANGE = "income_change"
    EXTRA_PAYMENT = "extra_payment"
    LUMP_SUM = "lump_sum"
    CUSTOM = "custom"


@dataclass
class FinancialState:
    """Snapshot of financial state."""
    monthly_income: float
    monthly_expenses: float
    monthly_savings: float
    savings_rate: float
    total_debt: float
    monthly_debt_payment: float
    debt_payoff_date: Optional[date]
    debt_payoff_months: int
    emergency_fund_months: float
    fire_number: float
    fire_date: Optional[date]
    fire_years: float


@dataclass
class ScenarioImpact:
    """Impact of a scenario change."""
    # Deltas
    monthly_savings_delta: float
    annual_savings_delta: float
    debt_payoff_months_delta: int
    debt_payoff_days_delta: int
    fire_years_delta: float
    total_interest_saved: float

    # Percentages
    savings_rate_delta: float
    dti_ratio_delta: float

    # Summary text
    summary: str
    highlights: List[str]


@dataclass
class ScenarioResult:
    """Complete scenario simulation result."""
    scenario_name: str
    scenario_type: ScenarioType
    description: str

    # States
    current_state: FinancialState
    simulated_state: FinancialState

    # Impact
    impact: ScenarioImpact

    # Metadata
    confidence: float
    assumptions: List[str]
    warnings: List[str]


class ScenarioEngine:
    """
    What-If scenario simulation engine.

    Usage:
        engine = ScenarioEngine()

        # Simulate expense reduction
        result = engine.simulate_expense_change("Ristoranti", -50)

        # Simulate income change
        result = engine.simulate_income_change(500)

        # Compare scenarios
        comparison = engine.compare_scenarios([result1, result2, result3])
    """

    # Default assumptions
    DEFAULTS = {
        "annual_return": 0.07,  # 7% annual investment return
        "inflation": 0.02,  # 2% inflation
        "safe_withdrawal_rate": 0.04,  # 4% SWR for FIRE
        "average_debt_rate": 0.10,  # 10% average interest
    }

    def __init__(self, user_profile: Optional[Dict] = None):
        """Initialize with optional user profile override."""
        self.user_profile = user_profile or self._load_user_profile()
        self.current_state = self._calculate_current_state()

    def _load_user_profile(self) -> Dict:
        """Load user profile from database."""
        try:
            profile = get_user_profile()
            return profile or {
                "monthly_net_income": 3200,
                "emergency_fund": 2000,
            }
        except Exception:
            return {"monthly_net_income": 3200, "emergency_fund": 2000}

    def _calculate_current_state(self) -> FinancialState:
        """Calculate current financial state."""
        income = self.user_profile.get("monthly_net_income", 3200)

        # Get current month spending
        today = date.today()
        current_month = today.strftime("%Y-%m")

        total_expenses = 0
        total_debt_payment = 0

        try:
            spending = get_spending_by_category(current_month)
            for cat in spending:
                total_expenses += abs(cat.get("total", 0))
        except Exception:
            total_expenses = income * 0.8  # Default assumption

        # Get debts
        total_debt = 0
        monthly_debt = 0
        try:
            debts = get_debts(active_only=True)
            for debt in debts:
                total_debt += debt.get("current_balance", 0)
                monthly_debt += debt.get("monthly_payment", 0)
        except Exception:
            pass

        # Calculate metrics
        monthly_savings = income - total_expenses
        savings_rate = monthly_savings / income if income > 0 else 0

        # Debt payoff calculation
        if total_debt > 0 and monthly_debt > 0:
            # Simple payoff calculation (ignoring interest for simplicity)
            payoff_months = int(total_debt / monthly_debt)
            payoff_date = today + relativedelta(months=payoff_months)
        else:
            payoff_months = 0
            payoff_date = None

        # Emergency fund months
        emergency_fund = self.user_profile.get("emergency_fund", 0)
        monthly_essential = total_expenses * 0.6  # Estimate 60% essential
        ef_months = emergency_fund / monthly_essential if monthly_essential > 0 else 0

        # FIRE calculation
        annual_expenses = total_expenses * 12
        fire_number = annual_expenses / self.DEFAULTS["safe_withdrawal_rate"]

        # Years to FIRE (simplified)
        if monthly_savings > 0:
            current_invested = emergency_fund  # Start from current savings
            annual_savings = monthly_savings * 12
            fire_years = self._calculate_fire_years(current_invested, annual_savings, fire_number)
            fire_date = today + relativedelta(years=int(fire_years))
        else:
            fire_years = 99
            fire_date = None

        return FinancialState(
            monthly_income=income,
            monthly_expenses=total_expenses,
            monthly_savings=monthly_savings,
            savings_rate=savings_rate,
            total_debt=total_debt,
            monthly_debt_payment=monthly_debt,
            debt_payoff_date=payoff_date,
            debt_payoff_months=payoff_months,
            emergency_fund_months=ef_months,
            fire_number=fire_number,
            fire_date=fire_date,
            fire_years=fire_years,
        )

    def _calculate_fire_years(self, current: float, annual_savings: float, target: float) -> float:
        """Calculate years to reach FIRE number with compound growth."""
        if annual_savings <= 0:
            return 99

        r = self.DEFAULTS["annual_return"]
        years = 0
        balance = current

        while balance < target and years < 60:
            balance = balance * (1 + r) + annual_savings
            years += 1

        return years

    def simulate_expense_change(
        self,
        category: str,
        change_percent: Optional[float] = None,
        change_amount: Optional[float] = None
    ) -> ScenarioResult:
        """
        Simulate expense change in a category.

        Args:
            category: Category name (e.g., "Ristoranti")
            change_percent: Percentage change (-50 = 50% reduction)
            change_amount: Absolute change in euros

        Returns:
            ScenarioResult with current vs simulated states
        """
        # Get current spending in category
        current_month = date.today().strftime("%Y-%m")
        category_spending = 0

        try:
            spending = get_spending_by_category(current_month)
            for cat in spending:
                if cat.get("category", "").lower() == category.lower():
                    category_spending = abs(cat.get("total", 0))
                    break
        except Exception:
            category_spending = 100  # Default

        # Calculate change
        if change_percent is not None:
            change = category_spending * (change_percent / 100)
        elif change_amount is not None:
            change = change_amount
        else:
            change = 0

        # Simulate new state
        new_expenses = self.current_state.monthly_expenses + change
        new_savings = self.current_state.monthly_income - new_expenses
        new_savings_rate = new_savings / self.current_state.monthly_income

        # Recalculate debt payoff
        extra_for_debt = max(0, -change)  # Savings go to debt
        new_monthly_debt = self.current_state.monthly_debt_payment + extra_for_debt
        if self.current_state.total_debt > 0 and new_monthly_debt > 0:
            new_payoff_months = int(self.current_state.total_debt / new_monthly_debt)
        else:
            new_payoff_months = 0

        # Recalculate FIRE
        new_annual_expenses = new_expenses * 12
        new_fire_number = new_annual_expenses / self.DEFAULTS["safe_withdrawal_rate"]
        new_annual_savings = new_savings * 12
        new_fire_years = self._calculate_fire_years(0, new_annual_savings, new_fire_number)

        # Create simulated state
        simulated = FinancialState(
            monthly_income=self.current_state.monthly_income,
            monthly_expenses=new_expenses,
            monthly_savings=new_savings,
            savings_rate=new_savings_rate,
            total_debt=self.current_state.total_debt,
            monthly_debt_payment=new_monthly_debt,
            debt_payoff_date=(
                date.today() + relativedelta(months=new_payoff_months)
                if new_payoff_months > 0 else None
            ),
            debt_payoff_months=new_payoff_months,
            emergency_fund_months=self.current_state.emergency_fund_months,
            fire_number=new_fire_number,
            fire_date=(
                date.today() + relativedelta(years=int(new_fire_years))
                if new_fire_years < 60 else None
            ),
            fire_years=new_fire_years,
        )

        # Calculate impact
        impact = self._calculate_impact(self.current_state, simulated)

        # Create description
        if change < 0:
            desc = f"Riduzione spesa {category} di €{abs(change):.0f}/mese"
        else:
            desc = f"Aumento spesa {category} di €{change:.0f}/mese"

        return ScenarioResult(
            scenario_name=f"Modifica {category}",
            scenario_type=ScenarioType.EXPENSE_CHANGE,
            description=desc,
            current_state=self.current_state,
            simulated_state=simulated,
            impact=impact,
            confidence=0.85,
            assumptions=[
                "Risparmi extra vanno verso il debito",
                "Spesa rimane costante nei mesi successivi"
            ],
            warnings=[],
        )

    def simulate_income_change(self, change_amount: float) -> ScenarioResult:
        """
        Simulate income change (raise, bonus, job loss).

        Args:
            change_amount: Monthly income change (positive or negative)

        Returns:
            ScenarioResult with impact
        """
        new_income = self.current_state.monthly_income + change_amount
        new_savings = new_income - self.current_state.monthly_expenses
        new_savings_rate = new_savings / new_income if new_income > 0 else 0

        # Extra income goes to debt
        extra_for_debt = max(0, change_amount)
        new_monthly_debt = self.current_state.monthly_debt_payment + extra_for_debt
        if self.current_state.total_debt > 0 and new_monthly_debt > 0:
            new_payoff_months = int(self.current_state.total_debt / new_monthly_debt)
        else:
            new_payoff_months = 0

        # Recalculate FIRE
        new_annual_savings = new_savings * 12
        new_fire_years = self._calculate_fire_years(
            0, new_annual_savings, self.current_state.fire_number
        )

        simulated = FinancialState(
            monthly_income=new_income,
            monthly_expenses=self.current_state.monthly_expenses,
            monthly_savings=new_savings,
            savings_rate=new_savings_rate,
            total_debt=self.current_state.total_debt,
            monthly_debt_payment=new_monthly_debt,
            debt_payoff_date=(
                date.today() + relativedelta(months=new_payoff_months)
                if new_payoff_months > 0 else None
            ),
            debt_payoff_months=new_payoff_months,
            emergency_fund_months=self.current_state.emergency_fund_months,
            fire_number=self.current_state.fire_number,
            fire_date=(
                date.today() + relativedelta(years=int(new_fire_years))
                if new_fire_years < 60 else None
            ),
            fire_years=new_fire_years,
        )

        impact = self._calculate_impact(self.current_state, simulated)

        if change_amount > 0:
            desc = f"Aumento reddito di €{change_amount:.0f}/mese"
            name = "Aumento stipendio"
        else:
            desc = f"Riduzione reddito di €{abs(change_amount):.0f}/mese"
            name = "Riduzione reddito"

        warnings = []
        if change_amount < 0 and new_savings < 0:
            warnings.append("Attenzione: con questo reddito saresti in deficit mensile")

        return ScenarioResult(
            scenario_name=name,
            scenario_type=ScenarioType.INCOME_CHANGE,
            description=desc,
            current_state=self.current_state,
            simulated_state=simulated,
            impact=impact,
            confidence=0.90,
            assumptions=[
                "Reddito extra va verso il debito",
                "Spese rimangono invariate"
            ],
            warnings=warnings,
        )

    def simulate_extra_payment(self, debt_id: int, extra_amount: float) -> ScenarioResult:
        """
        Simulate extra debt payment.

        Args:
            debt_id: ID of the debt
            extra_amount: Extra monthly payment

        Returns:
            ScenarioResult with impact
        """
        # Get specific debt
        debt_info = None
        try:
            debts = get_debts(active_only=True)
            for d in debts:
                if d.get("id") == debt_id:
                    debt_info = d
                    break
        except Exception:
            pass

        debt_name = debt_info.get("name", "Debito") if debt_info else "Debito"
        debt_balance = debt_info.get("current_balance", 0) if debt_info else self.current_state.total_debt
        debt_rate = debt_info.get("interest_rate", 10) if debt_info else 10
        current_payment = debt_info.get("monthly_payment", 0) if debt_info else 0

        # Calculate new payoff time
        new_payment = current_payment + extra_amount

        if new_payment > 0 and debt_balance > 0:
            # Simple payoff calculation
            old_months = int(debt_balance / current_payment) if current_payment > 0 else 999
            new_months = int(debt_balance / new_payment)
            months_saved = old_months - new_months

            # Interest saved (rough estimate)
            monthly_rate = debt_rate / 100 / 12
            interest_saved = debt_balance * monthly_rate * months_saved
        else:
            months_saved = 0
            interest_saved = 0

        # Simulated state (reduced savings due to extra payment)
        new_savings = self.current_state.monthly_savings - extra_amount

        simulated = FinancialState(
            monthly_income=self.current_state.monthly_income,
            monthly_expenses=self.current_state.monthly_expenses + extra_amount,
            monthly_savings=new_savings,
            savings_rate=new_savings / self.current_state.monthly_income,
            total_debt=self.current_state.total_debt,
            monthly_debt_payment=self.current_state.monthly_debt_payment + extra_amount,
            debt_payoff_date=(
                date.today() + relativedelta(months=(self.current_state.debt_payoff_months - months_saved))
            ),
            debt_payoff_months=self.current_state.debt_payoff_months - months_saved,
            emergency_fund_months=self.current_state.emergency_fund_months,
            fire_number=self.current_state.fire_number,
            fire_date=self.current_state.fire_date,
            fire_years=self.current_state.fire_years,
        )

        impact = ScenarioImpact(
            monthly_savings_delta=-extra_amount,
            annual_savings_delta=-extra_amount * 12,
            debt_payoff_months_delta=-months_saved,
            debt_payoff_days_delta=-months_saved * 30,
            fire_years_delta=0,
            total_interest_saved=interest_saved,
            savings_rate_delta=(simulated.savings_rate - self.current_state.savings_rate) * 100,
            dti_ratio_delta=0,
            summary=f"Pagamento extra di €{extra_amount}/mese su {debt_name}",
            highlights=[
                f"🎯 {months_saved} mesi prima debt-free",
                f"💰 €{interest_saved:.0f} risparmiati in interessi",
            ],
        )

        return ScenarioResult(
            scenario_name=f"Extra su {debt_name}",
            scenario_type=ScenarioType.EXTRA_PAYMENT,
            description=f"Pagamento extra di €{extra_amount}/mese verso {debt_name}",
            current_state=self.current_state,
            simulated_state=simulated,
            impact=impact,
            confidence=0.95,
            assumptions=["Pagamento extra costante ogni mese"],
            warnings=[],
        )

    def simulate_lump_sum(
        self,
        amount: float,
        allocation: Dict[str, float]
    ) -> ScenarioResult:
        """
        Simulate lump sum allocation (windfall, bonus).

        Args:
            amount: Total amount
            allocation: Dict with percentages, e.g., {"debt": 50, "savings": 30, "invest": 20}

        Returns:
            ScenarioResult with impact
        """
        debt_portion = amount * allocation.get("debt", 0) / 100
        savings_portion = amount * allocation.get("savings", 0) / 100
        invest_portion = amount * allocation.get("invest", 0) / 100

        # Impact on debt
        new_total_debt = self.current_state.total_debt - debt_portion
        if new_total_debt > 0 and self.current_state.monthly_debt_payment > 0:
            new_payoff_months = int(new_total_debt / self.current_state.monthly_debt_payment)
        else:
            new_payoff_months = 0

        months_saved = self.current_state.debt_payoff_months - new_payoff_months

        # Impact on emergency fund
        new_ef = (
            self.current_state.emergency_fund_months *
            self.current_state.monthly_expenses * 0.6 + savings_portion
        ) / (self.current_state.monthly_expenses * 0.6)

        simulated = FinancialState(
            monthly_income=self.current_state.monthly_income,
            monthly_expenses=self.current_state.monthly_expenses,
            monthly_savings=self.current_state.monthly_savings,
            savings_rate=self.current_state.savings_rate,
            total_debt=new_total_debt,
            monthly_debt_payment=self.current_state.monthly_debt_payment,
            debt_payoff_date=(
                date.today() + relativedelta(months=new_payoff_months)
                if new_payoff_months > 0 else None
            ),
            debt_payoff_months=new_payoff_months,
            emergency_fund_months=new_ef,
            fire_number=self.current_state.fire_number,
            fire_date=self.current_state.fire_date,
            fire_years=self.current_state.fire_years,
        )

        highlights = []
        if debt_portion > 0:
            highlights.append(f"💳 Debito ridotto di €{debt_portion:.0f}")
        if savings_portion > 0:
            highlights.append(f"🏦 Fondo emergenza +€{savings_portion:.0f}")
        if invest_portion > 0:
            highlights.append(f"📈 Investimenti +€{invest_portion:.0f}")

        impact = ScenarioImpact(
            monthly_savings_delta=0,
            annual_savings_delta=0,
            debt_payoff_months_delta=-months_saved,
            debt_payoff_days_delta=-months_saved * 30,
            fire_years_delta=0,
            total_interest_saved=debt_portion * 0.10,  # Rough 10% interest
            savings_rate_delta=0,
            dti_ratio_delta=0,
            summary=f"Allocazione di €{amount:.0f}",
            highlights=highlights,
        )

        return ScenarioResult(
            scenario_name="Allocazione somma",
            scenario_type=ScenarioType.LUMP_SUM,
            description=f"Allocazione di €{amount:.0f}: {allocation}",
            current_state=self.current_state,
            simulated_state=simulated,
            impact=impact,
            confidence=0.90,
            assumptions=["Interessi medi debito al 10%"],
            warnings=[],
        )

    def _calculate_impact(
        self,
        current: FinancialState,
        simulated: FinancialState
    ) -> ScenarioImpact:
        """Calculate impact between two states."""
        savings_delta = simulated.monthly_savings - current.monthly_savings
        months_delta = current.debt_payoff_months - simulated.debt_payoff_months
        fire_delta = current.fire_years - simulated.fire_years

        # Estimate interest saved
        if months_delta > 0:
            avg_rate = 0.10  # 10% average
            interest_saved = current.total_debt * (avg_rate / 12) * months_delta
        else:
            interest_saved = 0

        highlights = []
        if savings_delta > 0:
            highlights.append(f"💰 +€{savings_delta:.0f}/mese risparmiati")
        elif savings_delta < 0:
            highlights.append(f"⚠️ €{abs(savings_delta):.0f}/mese in meno")

        if months_delta > 0:
            highlights.append(f"🎯 {months_delta} mesi prima debt-free")
        elif months_delta < 0:
            highlights.append(f"⚠️ {abs(months_delta)} mesi in più di debito")

        if fire_delta > 0:
            highlights.append(f"🔥 FIRE {fire_delta:.1f} anni prima")

        if savings_delta > 0:
            summary = f"Risparmio +€{savings_delta:.0f}/mese, debt-free {months_delta} mesi prima"
        else:
            summary = "Scenario simulato"

        return ScenarioImpact(
            monthly_savings_delta=round(savings_delta, 2),
            annual_savings_delta=round(savings_delta * 12, 2),
            debt_payoff_months_delta=months_delta,
            debt_payoff_days_delta=months_delta * 30,
            fire_years_delta=round(fire_delta, 1),
            total_interest_saved=round(interest_saved, 2),
            savings_rate_delta=round((simulated.savings_rate - current.savings_rate) * 100, 1),
            dti_ratio_delta=0,
            summary=summary,
            highlights=highlights,
        )

    def compare_scenarios(self, scenarios: List[ScenarioResult]) -> Dict[str, Any]:
        """
        Compare multiple scenarios side by side.

        Args:
            scenarios: List of ScenarioResult objects

        Returns:
            Comparison dictionary
        """
        comparison = {
            "scenarios": [],
            "best_for_savings": None,
            "best_for_debt": None,
            "best_for_fire": None,
            "recommendation": None,
        }

        best_savings = (None, -9999)
        best_debt = (None, -9999)
        best_fire = (None, -9999)

        for scenario in scenarios:
            summary = {
                "name": scenario.scenario_name,
                "description": scenario.description,
                "monthly_savings_delta": scenario.impact.monthly_savings_delta,
                "debt_months_saved": -scenario.impact.debt_payoff_months_delta,
                "fire_years_saved": scenario.impact.fire_years_delta,
                "highlights": scenario.impact.highlights,
            }
            comparison["scenarios"].append(summary)

            if scenario.impact.monthly_savings_delta > best_savings[1]:
                best_savings = (scenario.scenario_name, scenario.impact.monthly_savings_delta)

            debt_saved = -scenario.impact.debt_payoff_months_delta
            if debt_saved > best_debt[1]:
                best_debt = (scenario.scenario_name, debt_saved)

            if scenario.impact.fire_years_delta > best_fire[1]:
                best_fire = (scenario.scenario_name, scenario.impact.fire_years_delta)

        comparison["best_for_savings"] = best_savings[0]
        comparison["best_for_debt"] = best_debt[0]
        comparison["best_for_fire"] = best_fire[0]

        # Simple recommendation
        if best_debt[0] == best_savings[0]:
            comparison["recommendation"] = best_debt[0]
        else:
            comparison["recommendation"] = best_debt[0]  # Prioritize debt payoff

        return comparison

    def to_dict(self, result: ScenarioResult) -> Dict[str, Any]:
        """Convert ScenarioResult to dictionary for API."""
        def state_to_dict(state: FinancialState) -> Dict:
            return {
                "monthly_income": state.monthly_income,
                "monthly_expenses": state.monthly_expenses,
                "monthly_savings": state.monthly_savings,
                "savings_rate": round(state.savings_rate * 100, 1),
                "total_debt": state.total_debt,
                "monthly_debt_payment": state.monthly_debt_payment,
                "debt_payoff_date": state.debt_payoff_date.isoformat() if state.debt_payoff_date else None,
                "debt_payoff_months": state.debt_payoff_months,
                "emergency_fund_months": round(state.emergency_fund_months, 1),
                "fire_number": round(state.fire_number, 0),
                "fire_date": state.fire_date.isoformat() if state.fire_date else None,
                "fire_years": round(state.fire_years, 1),
            }

        return {
            "scenario_name": result.scenario_name,
            "scenario_type": result.scenario_type.value,
            "description": result.description,
            "current_state": state_to_dict(result.current_state),
            "simulated_state": state_to_dict(result.simulated_state),
            "impact": {
                "monthly_savings_delta": result.impact.monthly_savings_delta,
                "annual_savings_delta": result.impact.annual_savings_delta,
                "debt_payoff_months_delta": result.impact.debt_payoff_months_delta,
                "debt_payoff_days_delta": result.impact.debt_payoff_days_delta,
                "fire_years_delta": result.impact.fire_years_delta,
                "total_interest_saved": result.impact.total_interest_saved,
                "savings_rate_delta": result.impact.savings_rate_delta,
                "summary": result.impact.summary,
                "highlights": result.impact.highlights,
            },
            "confidence": result.confidence,
            "assumptions": result.assumptions,
            "warnings": result.warnings,
        }
