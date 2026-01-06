"""
Financial X-Ray Analyzer for MoneyMind v6.0

Provides comprehensive financial health analysis in a single view.
This is the "radiografia finanziaria" that allows Mattia to understand
his financial situation in 30 seconds or less.

Key Components:
- Cash Flow Breakdown: Essential / Debt / Discretionary / Available
- Debt Composition Analysis: Interest vs Principal, total cost
- Savings Potential: Top opportunities for optimization
- Risk Indicators: DTI, emergency fund, savings rate
- Phase Determination: Which of 4 phases user is in
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, List, Any, Tuple
from dateutil.relativedelta import relativedelta
from enum import Enum

from src.database import (
    get_db_context,
    get_monthly_summary,
    get_debts,
    get_user_profile,
    get_latest_balances,
    get_spending_by_category,
    get_transactions,
    get_recurring_expenses,
    get_categories,
    get_onboarding_profile,
)


class FinancialPhase(Enum):
    """The 4 phases of the financial freedom journey."""
    DIAGNOSI = "diagnosi"           # Initial - Understanding situation
    OTTIMIZZAZIONE = "ottimizzazione"  # 0-90 days - Quick wins
    SICUREZZA = "sicurezza"         # 3-24 months - Stability
    CRESCITA = "crescita"           # 2+ years - Wealth building


class RiskLevel(Enum):
    """Overall risk assessment levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CashFlowBreakdown:
    """Monthly cash flow breakdown by type."""
    income: float
    essential_expenses: float  # Housing, utilities, food, transport
    debt_payments: float       # All debt payments
    discretionary: float       # Non-essential spending
    available_for_savings: float  # What's left

    @property
    def total_expenses(self) -> float:
        return self.essential_expenses + self.debt_payments + self.discretionary

    @property
    def savings_rate(self) -> float:
        if self.income <= 0:
            return 0.0
        return (self.available_for_savings / self.income) * 100


@dataclass
class DebtInfo:
    """Information about a single debt."""
    id: int
    name: str
    current_balance: float
    interest_rate: float
    monthly_payment: float
    total_interest_remaining: float
    burden_percent: float  # % of monthly income


@dataclass
class DebtAnalysis:
    """Analysis of all debts."""
    total_debt: float
    total_monthly_payments: float
    total_interest_paid_ytd: float
    total_interest_remaining: float
    debt_burden_percent: float  # DTI ratio
    highest_rate_debt: Optional[DebtInfo]
    debts: List[DebtInfo]
    months_to_freedom: Optional[int]
    freedom_date: Optional[date]


@dataclass
class SavingOpportunity:
    """A potential area for savings."""
    category: str
    current_spending: float
    baseline_spending: float
    potential_savings: float
    impact_monthly: float
    impact_annual: float
    recommendation: str
    priority: int  # 1 = highest


@dataclass
class RiskIndicators:
    """Financial risk assessment indicators."""
    dti_ratio: float           # Debt-to-Income ratio (%)
    emergency_fund_months: float  # Months of expenses covered
    savings_rate: float        # % of income saved
    expense_volatility: float  # Standard deviation of monthly expenses
    status: RiskLevel
    issues: List[str]


@dataclass
class PhaseInfo:
    """Current phase in the financial freedom journey."""
    current_phase: FinancialPhase
    progress_percent: float
    next_milestone: str
    days_in_phase: int
    phase_started: Optional[date]


@dataclass
class FinancialXRay:
    """Complete financial X-Ray analysis."""
    analysis_date: date
    month: str
    cash_flow: CashFlowBreakdown
    debt_analysis: DebtAnalysis
    savings_potential: List[SavingOpportunity]
    risk_indicators: RiskIndicators
    phase_info: PhaseInfo
    health_score: int  # 0-100
    health_grade: str  # A, B, C, D, F
    summary: str


class XRayAnalyzer:
    """
    Comprehensive financial health analysis engine.

    Usage:
        analyzer = XRayAnalyzer()
        xray = analyzer.generate_xray("2026-01")
        print(f"Health Score: {xray.health_score} ({xray.health_grade})")
    """

    # Categories considered "essential" for cash flow breakdown
    ESSENTIAL_CATEGORIES = [
        "Affitto", "Utenze", "Spesa", "Trasporti", "Salute", "Assicurazioni"
    ]

    # Categories that are debt payments
    DEBT_CATEGORIES = ["Finanziamenti"]

    def __init__(self):
        self.categories = {c["name"]: c for c in get_categories()}

    def generate_xray(self, month: str = None) -> FinancialXRay:
        """
        Generate a complete financial X-Ray for a month.

        Args:
            month: Month to analyze (YYYY-MM). Defaults to current month.

        Returns:
            Complete FinancialXRay analysis
        """
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        # Gather all data
        cash_flow = self.calculate_cash_flow_breakdown(month)
        debt_analysis = self.analyze_debt_composition(month)
        savings_potential = self.identify_savings_potential(month)
        risk_indicators = self.calculate_risk_indicators(cash_flow, debt_analysis)
        phase_info = self.determine_current_phase(debt_analysis, risk_indicators)

        # Calculate health score
        health_score, health_grade = self._calculate_health_score(
            cash_flow, debt_analysis, risk_indicators
        )

        # Generate summary
        summary = self._generate_summary(
            phase_info, health_score, risk_indicators, debt_analysis
        )

        return FinancialXRay(
            analysis_date=date.today(),
            month=month,
            cash_flow=cash_flow,
            debt_analysis=debt_analysis,
            savings_potential=savings_potential,
            risk_indicators=risk_indicators,
            phase_info=phase_info,
            health_score=health_score,
            health_grade=health_grade,
            summary=summary
        )

    def calculate_cash_flow_breakdown(self, month: str) -> CashFlowBreakdown:
        """
        Calculate cash flow breakdown by expense type.

        Categories spending into:
        - Essential: Housing, utilities, food, transport, health
        - Debt: All debt/financing payments
        - Discretionary: Everything else (wants)
        """
        monthly_summary = get_monthly_summary(month)
        spending_by_cat = get_spending_by_category(month)

        income = monthly_summary.get("total_income", 0) or 0

        # Use user profile income if transaction income seems too low
        profile = get_user_profile()
        if profile and profile.get("monthly_net_income"):
            if income < profile["monthly_net_income"] * 0.5:
                income = profile["monthly_net_income"]

        essential = 0.0
        debt_payments = 0.0
        discretionary = 0.0

        for cat_spending in spending_by_cat:
            cat_name = cat_spending.get("category_name", "")
            amount = cat_spending.get("total_spent", 0) or 0

            if cat_name in self.ESSENTIAL_CATEGORIES:
                essential += amount
            elif cat_name in self.DEBT_CATEGORIES:
                debt_payments += amount
            elif cat_name not in ["Stipendio", "Trasferimenti", "Risparmi Automatici"]:
                # Skip income-like categories
                discretionary += amount

        # Also add debt payments from debts table if not captured in transactions
        debts = get_debts(active_only=True)
        debt_from_table = sum(d.get("monthly_payment", 0) or 0 for d in debts)
        if debt_payments < debt_from_table * 0.5:
            debt_payments = debt_from_table

        total_expenses = essential + debt_payments + discretionary
        available = max(0, income - total_expenses)

        return CashFlowBreakdown(
            income=income,
            essential_expenses=essential,
            debt_payments=debt_payments,
            discretionary=discretionary,
            available_for_savings=available
        )

    def analyze_debt_composition(self, month: str) -> DebtAnalysis:
        """
        Analyze debt composition and costs.

        For each debt, calculates:
        - Current balance
        - Monthly payment vs interest portion
        - Total remaining interest
        - Burden on monthly income
        """
        debts = get_debts(active_only=True)
        profile = get_user_profile()
        monthly_income = profile.get("monthly_net_income", 3000) if profile else 3000

        debt_infos = []
        total_debt = 0.0
        total_monthly = 0.0
        total_interest_remaining = 0.0
        highest_rate_debt = None

        for debt in debts:
            balance = debt.get("current_balance", 0) or 0
            rate = debt.get("interest_rate", 0) or 0
            payment = debt.get("monthly_payment", 0) or 0

            # Estimate remaining interest (simplified)
            if rate > 0 and payment > 0:
                # Monthly interest portion
                monthly_interest = balance * (rate / 100 / 12)
                # Rough estimate of remaining payments
                if payment > monthly_interest:
                    months_remaining = balance / (payment - monthly_interest)
                    interest_remaining = monthly_interest * months_remaining * 0.5  # Declining balance
                else:
                    interest_remaining = balance * 0.2  # Fallback estimate
            else:
                interest_remaining = 0

            burden_pct = (payment / monthly_income * 100) if monthly_income > 0 else 0

            debt_info = DebtInfo(
                id=debt["id"],
                name=debt["name"],
                current_balance=balance,
                interest_rate=rate,
                monthly_payment=payment,
                total_interest_remaining=interest_remaining,
                burden_percent=burden_pct
            )
            debt_infos.append(debt_info)

            total_debt += balance
            total_monthly += payment
            total_interest_remaining += interest_remaining

            if highest_rate_debt is None or rate > highest_rate_debt.interest_rate:
                highest_rate_debt = debt_info

        # Calculate months to freedom
        months_to_freedom = None
        freedom_date = None
        if total_monthly > 0 and total_debt > 0:
            # Simple calculation without considering interest
            months_to_freedom = int(total_debt / total_monthly)
            freedom_date = date.today() + relativedelta(months=months_to_freedom)

        dti = (total_monthly / monthly_income * 100) if monthly_income > 0 else 0

        # Estimate YTD interest paid (rough estimate based on current balances)
        ytd_months = datetime.now().month
        ytd_interest = total_interest_remaining * (ytd_months / 12) * 0.3  # Rough estimate

        return DebtAnalysis(
            total_debt=total_debt,
            total_monthly_payments=total_monthly,
            total_interest_paid_ytd=ytd_interest,
            total_interest_remaining=total_interest_remaining,
            debt_burden_percent=dti,
            highest_rate_debt=highest_rate_debt,
            debts=debt_infos,
            months_to_freedom=months_to_freedom,
            freedom_date=freedom_date
        )

    def identify_savings_potential(self, month: str, limit: int = 10) -> List[SavingOpportunity]:
        """
        Identify top opportunities for reducing expenses.

        Compares current spending to 3-month baseline and
        flags categories with significant overspending.
        """
        opportunities = []

        # Get current month spending
        current_spending = get_spending_by_category(month)

        # Get baseline (3-month average before this month)
        ref_date = datetime.strptime(month + "-01", "%Y-%m-%d")
        baseline_spending = {}

        for i in range(1, 4):
            past_month = (ref_date - relativedelta(months=i)).strftime("%Y-%m")
            past_spending = get_spending_by_category(past_month)
            for cat in past_spending:
                cat_name = cat.get("category_name", "")
                if cat_name not in baseline_spending:
                    baseline_spending[cat_name] = []
                baseline_spending[cat_name].append(cat.get("total_spent", 0) or 0)

        # Calculate averages and compare
        for cat in current_spending:
            cat_name = cat.get("category_name", "")
            current = cat.get("total_spent", 0) or 0

            # Skip income and transfer categories
            if cat_name in ["Stipendio", "Trasferimenti", "Risparmi Automatici"]:
                continue

            # Calculate baseline average
            if cat_name in baseline_spending and baseline_spending[cat_name]:
                baseline_avg = sum(baseline_spending[cat_name]) / len(baseline_spending[cat_name])
            else:
                baseline_avg = current * 0.8  # Assume 20% potential savings if no baseline

            # Calculate potential savings
            if current > baseline_avg and current > 50:  # Only significant amounts
                potential = current - baseline_avg
                if potential > 20:  # Only if meaningful
                    opportunities.append(SavingOpportunity(
                        category=cat_name,
                        current_spending=current,
                        baseline_spending=baseline_avg,
                        potential_savings=potential,
                        impact_monthly=potential,
                        impact_annual=potential * 12,
                        recommendation=self._get_recommendation(cat_name, current, baseline_avg),
                        priority=1 if potential > 100 else 2 if potential > 50 else 3
                    ))

        # Also check recurring expenses for optimization
        recurring = get_recurring_expenses(active_only=True)
        for rec in recurring:
            if rec.get("optimization_status") == "not_reviewed":
                avg_amount = rec.get("avg_amount", 0) or 0
                if avg_amount > 10:
                    estimated_savings = avg_amount * 0.15  # Assume 15% possible savings
                    opportunities.append(SavingOpportunity(
                        category=rec.get("category_name", "Abbonamenti"),
                        current_spending=avg_amount,
                        baseline_spending=avg_amount * 0.85,
                        potential_savings=estimated_savings,
                        impact_monthly=estimated_savings,
                        impact_annual=estimated_savings * 12,
                        recommendation=f"Rivedi abbonamento {rec.get('pattern_name', '')}",
                        priority=2
                    ))

        # Sort by priority and potential
        opportunities.sort(key=lambda x: (x.priority, -x.potential_savings))
        return opportunities[:limit]

    def calculate_risk_indicators(
        self, cash_flow: CashFlowBreakdown, debt_analysis: DebtAnalysis
    ) -> RiskIndicators:
        """
        Calculate financial risk indicators.

        Indicators:
        - DTI Ratio: Debt-to-Income (should be < 36%)
        - Emergency Fund: Months of expenses covered (target: 3-6)
        - Savings Rate: % of income saved (target: > 20%)
        """
        issues = []

        # DTI Ratio
        dti = debt_analysis.debt_burden_percent
        if dti > 50:
            issues.append("DTI critico > 50%")
        elif dti > 36:
            issues.append("DTI alto > 36%")

        # Emergency Fund
        balances = get_latest_balances()
        total_balance = sum(b.get("balance", 0) or 0 for b in balances)
        monthly_expenses = cash_flow.total_expenses
        emergency_months = total_balance / monthly_expenses if monthly_expenses > 0 else 0

        if emergency_months < 1:
            issues.append("Fondo emergenza < 1 mese")
        elif emergency_months < 3:
            issues.append("Fondo emergenza < 3 mesi")

        # Savings Rate
        savings_rate = cash_flow.savings_rate
        if savings_rate < 0:
            issues.append("Spendi più di quanto guadagni")
        elif savings_rate < 10:
            issues.append("Savings rate basso < 10%")

        # Determine overall status
        if len(issues) >= 3 or dti > 50 or savings_rate < 0:
            status = RiskLevel.CRITICAL
        elif len(issues) >= 2 or dti > 36:
            status = RiskLevel.HIGH
        elif len(issues) >= 1:
            status = RiskLevel.MODERATE
        else:
            status = RiskLevel.LOW

        return RiskIndicators(
            dti_ratio=dti,
            emergency_fund_months=emergency_months,
            savings_rate=savings_rate,
            expense_volatility=0.0,  # TODO: Calculate from historical data
            status=status,
            issues=issues
        )

    def determine_current_phase(
        self, debt_analysis: DebtAnalysis, risk_indicators: RiskIndicators
    ) -> PhaseInfo:
        """
        Determine which of the 4 financial phases user is in.

        Phases:
        1. Diagnosi: Initial - Just started, understanding situation
        2. Ottimizzazione: 0-90 days - Finding quick wins
        3. Sicurezza: 3-24 months - Building stability, paying off debt
        4. Crescita: 2+ years - Wealth building
        """
        profile = get_onboarding_profile()

        # Check if onboarding is complete
        if not profile or not profile.get("onboarding_completed_at"):
            return PhaseInfo(
                current_phase=FinancialPhase.DIAGNOSI,
                progress_percent=0,
                next_milestone="Completa il questionario di onboarding",
                days_in_phase=0,
                phase_started=None
            )

        # Check debt status
        has_debt = debt_analysis.total_debt > 0
        emergency_months = risk_indicators.emergency_fund_months
        savings_rate = risk_indicators.savings_rate
        dti = risk_indicators.dti_ratio

        # Determine phase based on financial metrics
        if has_debt and dti > 20:
            # Still paying off significant debt
            if dti > 36:
                phase = FinancialPhase.OTTIMIZZAZIONE
                progress = min(100, (36 / dti) * 100)
                next_milestone = f"Riduci DTI da {dti:.1f}% a < 36%"
            else:
                phase = FinancialPhase.SICUREZZA
                progress = min(100, ((36 - dti) / 16) * 50 + 50)  # 50-100% range
                next_milestone = "Estingui i debiti di consumo"
        elif emergency_months < 3:
            phase = FinancialPhase.SICUREZZA
            progress = min(100, (emergency_months / 3) * 100)
            next_milestone = f"Costruisci fondo emergenza: {emergency_months:.1f}/3 mesi"
        elif savings_rate < 20:
            phase = FinancialPhase.SICUREZZA
            progress = min(100, 50 + (savings_rate / 20) * 50)
            next_milestone = f"Aumenta savings rate: {savings_rate:.1f}% → 20%"
        else:
            phase = FinancialPhase.CRESCITA
            progress = min(100, savings_rate * 2)  # 50% at 25% savings rate
            next_milestone = "Investi per la libertà finanziaria"

        # Calculate days in phase
        phase_started = None
        days_in_phase = 0
        if profile.get("onboarding_completed_at"):
            try:
                phase_started = datetime.fromisoformat(
                    profile["onboarding_completed_at"].replace("Z", "+00:00")
                ).date()
                days_in_phase = (date.today() - phase_started).days
            except (ValueError, TypeError):
                pass

        return PhaseInfo(
            current_phase=phase,
            progress_percent=progress,
            next_milestone=next_milestone,
            days_in_phase=days_in_phase,
            phase_started=phase_started
        )

    def _calculate_health_score(
        self,
        cash_flow: CashFlowBreakdown,
        debt_analysis: DebtAnalysis,
        risk_indicators: RiskIndicators
    ) -> Tuple[int, str]:
        """
        Calculate overall financial health score (0-100).

        Components (25 points each):
        - Savings Rate: 20%+ = 25, 10% = 15, 0% = 0
        - DTI Ratio: <20% = 25, <36% = 15, >50% = 0
        - Emergency Fund: 6+ months = 25, 3 = 15, 0 = 0
        - Net Worth Trend: Positive = 25, Flat = 10, Negative = 0
        """
        score = 0

        # Savings Rate (25 pts)
        sr = risk_indicators.savings_rate
        if sr >= 20:
            score += 25
        elif sr >= 10:
            score += 15
        elif sr > 0:
            score += 5

        # DTI Ratio (25 pts)
        dti = risk_indicators.dti_ratio
        if dti < 20:
            score += 25
        elif dti < 36:
            score += 15
        elif dti < 50:
            score += 5

        # Emergency Fund (25 pts)
        ef = risk_indicators.emergency_fund_months
        if ef >= 6:
            score += 25
        elif ef >= 3:
            score += 15
        elif ef >= 1:
            score += 5

        # Cash Flow Health (25 pts)
        if cash_flow.available_for_savings > 500:
            score += 25
        elif cash_flow.available_for_savings > 200:
            score += 15
        elif cash_flow.available_for_savings > 0:
            score += 5

        # Determine grade
        if score >= 80:
            grade = "A"
        elif score >= 65:
            grade = "B"
        elif score >= 50:
            grade = "C"
        elif score >= 35:
            grade = "D"
        else:
            grade = "F"

        return score, grade

    def _generate_summary(
        self,
        phase_info: PhaseInfo,
        health_score: int,
        risk_indicators: RiskIndicators,
        debt_analysis: DebtAnalysis
    ) -> str:
        """Generate a human-readable summary of the X-Ray."""
        phase_names = {
            FinancialPhase.DIAGNOSI: "Diagnosi",
            FinancialPhase.OTTIMIZZAZIONE: "Ottimizzazione",
            FinancialPhase.SICUREZZA: "Sicurezza",
            FinancialPhase.CRESCITA: "Crescita"
        }

        phase_name = phase_names[phase_info.current_phase]

        if debt_analysis.total_debt > 0:
            debt_msg = f"Debito totale: €{debt_analysis.total_debt:,.0f}"
            if debt_analysis.freedom_date:
                debt_msg += f" - Libertà prevista: {debt_analysis.freedom_date.strftime('%B %Y')}"
        else:
            debt_msg = "Nessun debito attivo"

        issues_msg = ""
        if risk_indicators.issues:
            issues_msg = f" Attenzione: {', '.join(risk_indicators.issues[:2])}."

        return (
            f"Fase attuale: {phase_name} ({phase_info.progress_percent:.0f}% completato). "
            f"{debt_msg}. "
            f"Prossimo obiettivo: {phase_info.next_milestone}.{issues_msg}"
        )

    def _get_recommendation(self, category: str, current: float, baseline: float) -> str:
        """Get a specific recommendation for reducing spending in a category."""
        excess = current - baseline
        excess_pct = (excess / baseline * 100) if baseline > 0 else 0

        recommendations = {
            "Ristoranti": f"Riduci le cene fuori di €{excess:.0f}/mese. Prova il batch cooking.",
            "Abbonamenti": f"Hai €{excess:.0f} extra in abbonamenti. Rivedi quali usi davvero.",
            "Shopping": f"Spendi €{excess:.0f} più del solito. Prova la regola delle 48 ore.",
            "Viaggi": f"Budget viaggi sopra media di €{excess:.0f}. Pianifica in anticipo.",
            "Caffe": f"€{excess:.0f} extra in bar/caffè. Porta il caffè da casa?",
        }

        return recommendations.get(
            category,
            f"Spendi €{excess:.0f} più della media ({excess_pct:.0f}% sopra baseline)."
        )

    def to_dict(self, xray: FinancialXRay) -> Dict[str, Any]:
        """Convert FinancialXRay to dictionary for API response."""
        return {
            "analysis_date": xray.analysis_date.isoformat(),
            "month": xray.month,
            "cash_flow": {
                "income": xray.cash_flow.income,
                "essential_expenses": xray.cash_flow.essential_expenses,
                "debt_payments": xray.cash_flow.debt_payments,
                "discretionary": xray.cash_flow.discretionary,
                "available_for_savings": xray.cash_flow.available_for_savings,
                "total_expenses": xray.cash_flow.total_expenses,
                "savings_rate": xray.cash_flow.savings_rate
            },
            "debt_analysis": {
                "total_debt": xray.debt_analysis.total_debt,
                "total_monthly_payments": xray.debt_analysis.total_monthly_payments,
                "total_interest_paid_ytd": xray.debt_analysis.total_interest_paid_ytd,
                "total_interest_remaining": xray.debt_analysis.total_interest_remaining,
                "debt_burden_percent": xray.debt_analysis.debt_burden_percent,
                "months_to_freedom": xray.debt_analysis.months_to_freedom,
                "freedom_date": xray.debt_analysis.freedom_date.isoformat() if xray.debt_analysis.freedom_date else None,
                "highest_rate_debt": {
                    "name": xray.debt_analysis.highest_rate_debt.name,
                    "rate": xray.debt_analysis.highest_rate_debt.interest_rate,
                    "balance": xray.debt_analysis.highest_rate_debt.current_balance
                } if xray.debt_analysis.highest_rate_debt else None,
                "debts": [
                    {
                        "id": d.id,
                        "name": d.name,
                        "balance": d.current_balance,
                        "rate": d.interest_rate,
                        "payment": d.monthly_payment,
                        "burden_percent": d.burden_percent
                    }
                    for d in xray.debt_analysis.debts
                ]
            },
            "savings_potential": [
                {
                    "category": sp.category,
                    "current": sp.current_spending,
                    "baseline": sp.baseline_spending,
                    "potential_savings": sp.potential_savings,
                    "impact_monthly": sp.impact_monthly,
                    "impact_annual": sp.impact_annual,
                    "recommendation": sp.recommendation,
                    "priority": sp.priority
                }
                for sp in xray.savings_potential
            ],
            "risk_indicators": {
                "dti_ratio": xray.risk_indicators.dti_ratio,
                "emergency_fund_months": xray.risk_indicators.emergency_fund_months,
                "savings_rate": xray.risk_indicators.savings_rate,
                "status": xray.risk_indicators.status.value,
                "issues": xray.risk_indicators.issues
            },
            "phase": xray.phase_info.current_phase.value,
            "phase_info": {
                "current_phase": xray.phase_info.current_phase.value,
                "progress_percent": xray.phase_info.progress_percent,
                "next_milestone": xray.phase_info.next_milestone,
                "days_in_phase": xray.phase_info.days_in_phase
            },
            "health_score": xray.health_score,
            "health_grade": xray.health_grade,
            "summary": xray.summary
        }
