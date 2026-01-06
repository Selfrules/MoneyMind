"""
Full Financial Report Analyzer for MoneyMind v6.0

Generates comprehensive financial reports with:
- Category spending analysis with judgments (EXCELLENT/GOOD/WARNING/CRITICAL)
- Subscription audit with action recommendations
- Debt priority matrix with APR
- Actionable recommendations
- Month-over-month comparison

This is the enhanced "radiografia finanziaria" with detailed judgments.
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
    get_spending_by_category,
    get_transactions,
    get_recurring_expenses,
    get_categories,
)
from src.core_finance.xray_analyzer import XRayAnalyzer, FinancialXRay


class Judgment(str, Enum):
    """Spending judgment levels."""
    EXCELLENT = "excellent"  # < 80% benchmark
    GOOD = "good"           # 80-100% benchmark
    WARNING = "warning"     # 100-150% benchmark
    CRITICAL = "critical"   # > 150% benchmark


class SubscriptionAction(str, Enum):
    """Recommended actions for subscriptions."""
    CANCEL = "cancel"
    DOWNGRADE = "downgrade"
    REVIEW = "review"
    KEEP = "keep"
    NEGOTIATE = "negotiate"


class Difficulty(str, Enum):
    """Implementation difficulty levels."""
    EASY = "easy"       # 5 min, no effort
    MEDIUM = "medium"   # 30 min, some effort
    HARD = "hard"       # Days, significant effort


@dataclass
class CategorySpending:
    """Spending analysis for a category."""
    category: str
    icon: str
    amount_current: float
    amount_avg_3m: float
    benchmark: float
    judgment: Judgment
    variance_percent: float
    notes: str
    suggestion: Optional[str] = None


@dataclass
class SubscriptionAudit:
    """Audit of a subscription/recurring expense."""
    name: str
    category: str
    monthly_cost: float
    annual_cost: float
    action: SubscriptionAction
    reason: str
    potential_savings: float
    value_score: int  # 1-10, higher is better value
    last_used: Optional[str] = None
    alternative: Optional[str] = None


@dataclass
class DebtPriority:
    """Debt with priority scoring."""
    id: int
    name: str
    balance: float
    apr: float
    monthly_payment: float
    interest_monthly: float
    principal_monthly: float
    priority_score: int  # Higher = pay first
    months_remaining: int
    payoff_date: Optional[date]
    total_remaining_cost: float


@dataclass
class Recommendation:
    """Actionable recommendation."""
    id: str
    title: str
    description: str
    impact_monthly: float
    impact_annual: float
    difficulty: Difficulty
    category: str  # "subscriptions", "spending", "debt", "income"
    action_steps: List[str]
    priority: int  # 1 = highest


@dataclass
class MonthComparison:
    """Month-over-month comparison."""
    category: str
    current_month: float
    previous_month: float
    delta: float
    delta_percent: float
    trend: str  # "up", "down", "stable"


@dataclass
class ExecutiveSummary:
    """High-level financial summary."""
    health_score: int
    health_grade: str
    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate: float
    total_debt: float
    debt_payment_monthly: float
    months_to_debt_free: Optional[int]
    overall_judgment: Judgment
    key_issues: List[str]
    key_wins: List[str]


@dataclass
class FullFinancialReport:
    """Complete financial report."""
    report_date: date
    month: str
    executive_summary: ExecutiveSummary
    category_spending: List[CategorySpending]
    subscription_audit: List[SubscriptionAudit]
    debt_priority: List[DebtPriority]
    recommendations: List[Recommendation]
    month_comparison: List[MonthComparison]


class ReportAnalyzer:
    """
    Comprehensive financial report generator.

    Usage:
        analyzer = ReportAnalyzer()
        report = analyzer.generate_full_report("2026-01")
    """

    # Fallback benchmarks (only used when no historical data)
    # These are generic defaults - personalized benchmarks from user's
    # 3-month average are preferred
    FALLBACK_BENCHMARKS = {
        "Ristoranti": 150,
        "Caffe": 50,
        "Spesa": 350,
        "Shopping": 100,
        "Abbonamenti": 100,
        "Trasporti": 150,
        "Utenze": 200,
        "Viaggi": 150,
        "Intrattenimento": 50,
        "Sport": 50,
        "Salute": 50,
        "Regali": 50,
        "Gatti": 80,
        "Contanti": 200,
    }

    # Category icons
    ICONS = {
        "Ristoranti": "🍽️",
        "Caffe": "☕",
        "Spesa": "🛒",
        "Shopping": "🛍️",
        "Abbonamenti": "📺",
        "Trasporti": "🚗",
        "Utenze": "💡",
        "Viaggi": "✈️",
        "Intrattenimento": "🎬",
        "Sport": "🏋️",
        "Salute": "🏥",
        "Regali": "🎁",
        "Finanziamenti": "💳",
        "Stipendio": "💰",
        "Altro": "📦",
    }

    # Subscription value assessments (name pattern -> value score 1-10)
    SUBSCRIPTION_VALUES = {
        "netflix": 7,
        "spotify": 8,
        "amazon prime": 8,
        "github": 9,
        "claude": 9,
        "chatgpt": 6,  # Redundant if using Claude
        "openai": 5,   # Redundant
        "notion": 7,
        "whoop": 5,
        "revolut": 6,
        "onlyfans": 2,
        "midjourney": 5,
        "cursor": 7,
        "copilot": 6,
    }

    def __init__(self):
        self.xray_analyzer = XRayAnalyzer()
        self.categories = {c["name"]: c for c in get_categories()}

    def _get_personalized_benchmarks(self, month: str, averages: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate personalized benchmarks based on user's 3-month average.

        Logic:
        - If user has historical data: benchmark = avg_3m * 1.1 (10% buffer)
        - If no historical data: use FALLBACK_BENCHMARKS
        - If not in fallback either: return None (will be skipped)

        This makes judgments relative to YOUR spending patterns,
        not arbitrary hardcoded values.

        Args:
            month: Current month being analyzed
            averages: Dict of category -> 3-month average amounts

        Returns:
            Dict of category -> personalized benchmark
        """
        benchmarks = {}

        for cat_name, avg_amount in averages.items():
            if avg_amount > 0:
                # Use user's own average + 10% buffer
                benchmarks[cat_name] = avg_amount * 1.1
            elif cat_name in self.FALLBACK_BENCHMARKS:
                # No history - use generic fallback
                benchmarks[cat_name] = self.FALLBACK_BENCHMARKS[cat_name]
            # Otherwise category won't have a benchmark (skip judgment)

        # Add fallbacks for categories not in averages
        for cat_name, fallback in self.FALLBACK_BENCHMARKS.items():
            if cat_name not in benchmarks:
                benchmarks[cat_name] = fallback

        return benchmarks

    def generate_full_report(self, month: str = None) -> FullFinancialReport:
        """Generate complete financial report for a month."""
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        # Get base X-Ray analysis
        xray = self.xray_analyzer.generate_xray(month)

        # Generate all sections
        executive_summary = self._generate_executive_summary(xray, month)
        category_spending = self._analyze_category_spending(month)
        subscription_audit = self._audit_subscriptions()
        debt_priority = self._analyze_debt_priority()
        recommendations = self._generate_recommendations(
            category_spending, subscription_audit, debt_priority, xray
        )
        month_comparison = self._generate_month_comparison(month)

        return FullFinancialReport(
            report_date=date.today(),
            month=month,
            executive_summary=executive_summary,
            category_spending=category_spending,
            subscription_audit=subscription_audit,
            debt_priority=debt_priority,
            recommendations=recommendations,
            month_comparison=month_comparison,
        )

    def _generate_executive_summary(
        self, xray: FinancialXRay, month: str
    ) -> ExecutiveSummary:
        """Generate executive summary from X-Ray data."""
        cash_flow = xray.cash_flow
        debt_analysis = xray.debt_analysis
        risk = xray.risk_indicators

        # Determine overall judgment
        if xray.health_score >= 80:
            overall_judgment = Judgment.EXCELLENT
        elif xray.health_score >= 65:
            overall_judgment = Judgment.GOOD
        elif xray.health_score >= 50:
            overall_judgment = Judgment.WARNING
        else:
            overall_judgment = Judgment.CRITICAL

        # Identify key issues
        key_issues = []
        if risk.savings_rate < 10:
            key_issues.append(f"Savings rate basso: {risk.savings_rate:.1f}%")
        if risk.dti_ratio > 30:
            key_issues.append(f"DTI alto: {risk.dti_ratio:.1f}%")
        if risk.emergency_fund_months < 3:
            key_issues.append(f"Fondo emergenza: {risk.emergency_fund_months:.1f} mesi")
        if debt_analysis.total_debt > 20000:
            key_issues.append(f"Debito significativo: €{debt_analysis.total_debt:,.0f}")

        # Identify key wins
        key_wins = []
        if risk.savings_rate > 20:
            key_wins.append(f"Ottimo savings rate: {risk.savings_rate:.1f}%")
        if debt_analysis.months_to_freedom and debt_analysis.months_to_freedom < 24:
            key_wins.append(f"Debiti estinti in {debt_analysis.months_to_freedom} mesi")
        if risk.emergency_fund_months >= 6:
            key_wins.append("Fondo emergenza solido")

        return ExecutiveSummary(
            health_score=xray.health_score,
            health_grade=xray.health_grade,
            total_income=cash_flow.income,
            total_expenses=cash_flow.total_expenses,
            net_savings=cash_flow.available_for_savings,
            savings_rate=cash_flow.savings_rate,
            total_debt=debt_analysis.total_debt,
            debt_payment_monthly=debt_analysis.total_monthly_payments,
            months_to_debt_free=debt_analysis.months_to_freedom,
            overall_judgment=overall_judgment,
            key_issues=key_issues,
            key_wins=key_wins,
        )

    def _analyze_category_spending(self, month: str) -> List[CategorySpending]:
        """Analyze spending by category with judgments."""
        results = []

        # Get current month spending
        current_spending = get_spending_by_category(month)

        # Get 3-month average
        ref_date = datetime.strptime(month + "-01", "%Y-%m-%d")
        historical = {}

        for i in range(1, 4):
            past_month = (ref_date - relativedelta(months=i)).strftime("%Y-%m")
            past_spending = get_spending_by_category(past_month)
            for cat in past_spending:
                cat_name = cat.get("category_name", "")
                if cat_name not in historical:
                    historical[cat_name] = []
                historical[cat_name].append(abs(cat.get("total_spent", 0) or 0))

        # Calculate averages
        averages = {
            cat: sum(vals) / len(vals) if vals else 0
            for cat, vals in historical.items()
        }

        # Skip income/transfer categories
        skip_categories = ["Stipendio", "Trasferimenti", "Risparmi Automatici"]

        for cat_data in current_spending:
            cat_name = cat_data.get("category_name", "")
            if cat_name in skip_categories:
                continue

            amount = abs(cat_data.get("total_spent", 0) or 0)
            if amount < 5:  # Skip tiny amounts
                continue

            avg_3m = averages.get(cat_name, amount)

            # Get personalized benchmark (user's avg + 10% buffer)
            personalized_benchmarks = self._get_personalized_benchmarks(month, averages)
            benchmark = personalized_benchmarks.get(cat_name, avg_3m * 1.1)

            # Calculate judgment based on personalized benchmark
            # Thresholds are relative to YOUR spending patterns, not arbitrary values
            if benchmark > 0:
                ratio = amount / benchmark
                if ratio < 0.9:
                    judgment = Judgment.EXCELLENT  # < 90% of your benchmark
                elif ratio <= 1.1:
                    judgment = Judgment.GOOD       # 90-110% of your benchmark
                elif ratio <= 1.4:
                    judgment = Judgment.WARNING    # 110-140% of your benchmark
                else:
                    judgment = Judgment.CRITICAL   # > 140% of your benchmark
            else:
                judgment = Judgment.GOOD

            # Calculate variance
            variance_pct = ((amount - avg_3m) / avg_3m * 100) if avg_3m > 0 else 0

            # Generate notes and suggestions
            notes, suggestion = self._get_category_notes(
                cat_name, amount, avg_3m, benchmark, judgment
            )

            results.append(CategorySpending(
                category=cat_name,
                icon=self.ICONS.get(cat_name, "📦"),
                amount_current=amount,
                amount_avg_3m=avg_3m,
                benchmark=benchmark,
                judgment=judgment,
                variance_percent=variance_pct,
                notes=notes,
                suggestion=suggestion,
            ))

        # Sort by judgment severity, then by amount
        judgment_order = {
            Judgment.CRITICAL: 0,
            Judgment.WARNING: 1,
            Judgment.GOOD: 2,
            Judgment.EXCELLENT: 3,
        }
        results.sort(key=lambda x: (judgment_order[x.judgment], -x.amount_current))

        return results

    def _get_category_notes(
        self, category: str, amount: float, avg: float, benchmark: float, judgment: Judgment
    ) -> Tuple[str, Optional[str]]:
        """Generate notes and suggestions for a category."""
        variance = amount - avg

        # Category-specific notes
        notes_map = {
            "Ristoranti": {
                Judgment.CRITICAL: f"€{amount:.0f} in ristoranti e troppo. Obiettivo: max €{benchmark:.0f}/mese.",
                Judgment.WARNING: f"€{amount:.0f} sopra media. Considera cucinare piu a casa.",
                Judgment.GOOD: f"Buon controllo: €{amount:.0f}/mese.",
                Judgment.EXCELLENT: f"Ottimo! Solo €{amount:.0f}/mese.",
            },
            "Caffe": {
                Judgment.CRITICAL: f"€{amount:.0f} in bar/caffe e eccessivo. Porta il caffe da casa.",
                Judgment.WARNING: f"€{amount:.0f}/mese. Riduci le colazioni fuori.",
                Judgment.GOOD: f"Ragionevole: €{amount:.0f}/mese.",
                Judgment.EXCELLENT: f"Ben controllato: €{amount:.0f}/mese.",
            },
            "Abbonamenti": {
                Judgment.CRITICAL: f"€{amount:.0f} in abbonamenti e troppo. Fai un audit completo.",
                Judgment.WARNING: f"€{amount:.0f}/mese. Verifica quali usi davvero.",
                Judgment.GOOD: f"Nella norma: €{amount:.0f}/mese.",
                Judgment.EXCELLENT: f"Ottimizzato: €{amount:.0f}/mese.",
            },
            "Shopping": {
                Judgment.CRITICAL: f"€{amount:.0f} in shopping. Applica la regola delle 48 ore.",
                Judgment.WARNING: f"€{amount:.0f} sopra media. Attenzione agli acquisti impulsivi.",
                Judgment.GOOD: f"Sotto controllo: €{amount:.0f}/mese.",
                Judgment.EXCELLENT: f"Ottimo autocontrollo: €{amount:.0f}/mese.",
            },
        }

        # Get specific note or generate generic
        cat_notes = notes_map.get(category, {})
        notes = cat_notes.get(judgment, f"€{amount:.0f}/mese (media: €{avg:.0f})")

        # Generate suggestion for WARNING/CRITICAL
        suggestion = None
        if judgment in (Judgment.WARNING, Judgment.CRITICAL):
            excess = amount - benchmark
            suggestion_map = {
                "Ristoranti": f"Riduci di €{excess:.0f}/mese. Prova meal prep e batch cooking.",
                "Caffe": f"Risparmia €{excess:.0f}/mese portando il caffe da casa.",
                "Abbonamenti": f"Cancella abbonamenti inutilizzati per risparmiare €{excess:.0f}.",
                "Shopping": f"Aspetta 48h prima di ogni acquisto. Target: -€{excess:.0f}/mese.",
                "Intrattenimento": f"Cerca alternative gratuite. Risparmio potenziale: €{excess:.0f}.",
            }
            suggestion = suggestion_map.get(
                category,
                f"Riduci la spesa in {category} di €{excess:.0f}/mese."
            )

        return notes, suggestion

    def _audit_subscriptions(self) -> List[SubscriptionAudit]:
        """Audit all subscriptions with recommendations."""
        audits = []

        recurring = get_recurring_expenses(active_only=True)

        for rec in recurring:
            name = rec.get("pattern_name", "Sconosciuto")
            category = rec.get("category_name", "Abbonamenti")
            monthly = abs(rec.get("avg_amount", 0) or 0)

            if monthly < 1:
                continue

            annual = monthly * 12
            name_lower = name.lower()

            # Determine value score
            value_score = 5  # Default
            for pattern, score in self.SUBSCRIPTION_VALUES.items():
                if pattern in name_lower:
                    value_score = score
                    break

            # Determine action and reason
            action, reason, potential_savings, alternative = self._get_subscription_action(
                name_lower, monthly, value_score
            )

            audits.append(SubscriptionAudit(
                name=name,
                category=category,
                monthly_cost=monthly,
                annual_cost=annual,
                action=action,
                reason=reason,
                potential_savings=potential_savings,
                value_score=value_score,
                alternative=alternative,
            ))

        # Sort by action priority (CANCEL first)
        action_order = {
            SubscriptionAction.CANCEL: 0,
            SubscriptionAction.DOWNGRADE: 1,
            SubscriptionAction.NEGOTIATE: 2,
            SubscriptionAction.REVIEW: 3,
            SubscriptionAction.KEEP: 4,
        }
        audits.sort(key=lambda x: (action_order[x.action], -x.monthly_cost))

        return audits

    def _get_subscription_action(
        self, name: str, monthly: float, value_score: int
    ) -> Tuple[SubscriptionAction, str, float, Optional[str]]:
        """Determine action for a subscription."""

        # Specific recommendations
        if "onlyfans" in name:
            return (
                SubscriptionAction.CANCEL,
                "Spesa non essenziale con alto costo.",
                monthly,
                None
            )

        if "openai" in name or "chatgpt" in name:
            return (
                SubscriptionAction.CANCEL,
                "Ridondante se usi gia Claude. Consolida in un solo servizio AI.",
                monthly,
                "Claude Pro"
            )

        if "revolut" in name and monthly > 10:
            return (
                SubscriptionAction.DOWNGRADE,
                "Piano Metal costoso. Valuta downgrade a Plus o Free.",
                monthly - 3.99,  # Plus plan cost
                "Revolut Plus (€3.99)"
            )

        if "cursor" in name and ("copilot" in name or "github" in name):
            return (
                SubscriptionAction.REVIEW,
                "Hai piu tool per coding AI. Scegline uno.",
                monthly * 0.5,
                None
            )

        if "whoop" in name:
            return (
                SubscriptionAction.REVIEW,
                "Costo alto per fitness tracker. Valuta alternative.",
                monthly * 0.7,
                "Apple Watch / Garmin"
            )

        # General rules based on value score
        if value_score <= 3:
            return (
                SubscriptionAction.CANCEL,
                f"Valore basso (score: {value_score}/10). Considera cancellazione.",
                monthly,
                None
            )
        elif value_score <= 5:
            return (
                SubscriptionAction.REVIEW,
                f"Valore medio (score: {value_score}/10). Verifica utilizzo reale.",
                monthly * 0.3,
                None
            )
        elif monthly > 30:
            return (
                SubscriptionAction.NEGOTIATE,
                f"Costo elevato. Cerca offerte o piani annuali scontati.",
                monthly * 0.15,
                None
            )
        else:
            return (
                SubscriptionAction.KEEP,
                f"Buon valore (score: {value_score}/10). Mantieni.",
                0,
                None
            )

    def _analyze_debt_priority(self) -> List[DebtPriority]:
        """Analyze debts and prioritize for payoff."""
        priorities = []

        debts = get_debts(active_only=True)

        for debt in debts:
            balance = debt.get("current_balance", 0) or 0
            apr = debt.get("interest_rate", 0) or 0
            payment = debt.get("monthly_payment", 0) or 0
            name = debt.get("name", "Debito")
            debt_id = debt.get("id", 0)

            if balance <= 0:
                continue

            # Calculate interest vs principal
            monthly_interest = balance * (apr / 100 / 12)
            monthly_principal = max(0, payment - monthly_interest)

            # Calculate months remaining
            if monthly_principal > 0:
                months_remaining = int(balance / monthly_principal)
            else:
                months_remaining = 999

            payoff_date = None
            if months_remaining < 999:
                payoff_date = date.today() + relativedelta(months=months_remaining)

            # Total remaining cost (principal + interest)
            total_remaining = balance + (monthly_interest * months_remaining * 0.5)

            # Priority score (higher APR = higher priority)
            priority_score = int(apr * 10)

            priorities.append(DebtPriority(
                id=debt_id,
                name=name,
                balance=balance,
                apr=apr,
                monthly_payment=payment,
                interest_monthly=monthly_interest,
                principal_monthly=monthly_principal,
                priority_score=priority_score,
                months_remaining=months_remaining,
                payoff_date=payoff_date,
                total_remaining_cost=total_remaining,
            ))

        # Sort by APR (avalanche method)
        priorities.sort(key=lambda x: -x.apr)

        return priorities

    def _generate_recommendations(
        self,
        categories: List[CategorySpending],
        subscriptions: List[SubscriptionAudit],
        debts: List[DebtPriority],
        xray: FinancialXRay,
    ) -> List[Recommendation]:
        """Generate prioritized recommendations."""
        recommendations = []
        rec_id = 0

        # Subscription cancellations
        for sub in subscriptions:
            if sub.action == SubscriptionAction.CANCEL and sub.potential_savings > 0:
                rec_id += 1
                recommendations.append(Recommendation(
                    id=f"rec_{rec_id}",
                    title=f"Cancella {sub.name}",
                    description=sub.reason,
                    impact_monthly=sub.potential_savings,
                    impact_annual=sub.potential_savings * 12,
                    difficulty=Difficulty.EASY,
                    category="subscriptions",
                    action_steps=[
                        f"Accedi al tuo account {sub.name}",
                        "Vai alle impostazioni abbonamento",
                        "Seleziona 'Cancella abbonamento'",
                        "Conferma la cancellazione",
                    ],
                    priority=1,
                ))

        # Subscription downgrades
        for sub in subscriptions:
            if sub.action == SubscriptionAction.DOWNGRADE and sub.potential_savings > 0:
                rec_id += 1
                recommendations.append(Recommendation(
                    id=f"rec_{rec_id}",
                    title=f"Downgrade {sub.name}",
                    description=sub.reason,
                    impact_monthly=sub.potential_savings,
                    impact_annual=sub.potential_savings * 12,
                    difficulty=Difficulty.EASY,
                    category="subscriptions",
                    action_steps=[
                        f"Accedi a {sub.name}",
                        "Vai a 'Gestione piano'",
                        f"Passa a {sub.alternative or 'piano base'}",
                    ],
                    priority=2,
                ))

        # Category spending reductions
        for cat in categories:
            if cat.judgment in (Judgment.CRITICAL, Judgment.WARNING) and cat.suggestion:
                rec_id += 1
                excess = cat.amount_current - cat.benchmark
                recommendations.append(Recommendation(
                    id=f"rec_{rec_id}",
                    title=f"Riduci spese {cat.category}",
                    description=cat.suggestion,
                    impact_monthly=excess * 0.5,  # Assume 50% reduction achievable
                    impact_annual=excess * 0.5 * 12,
                    difficulty=Difficulty.MEDIUM,
                    category="spending",
                    action_steps=[
                        f"Imposta budget mensile: €{cat.benchmark:.0f}",
                        f"Traccia ogni spesa in {cat.category}",
                        "Cerca alternative piu economiche",
                        "Rivedi settimanalmente i progressi",
                    ],
                    priority=2 if cat.judgment == Judgment.CRITICAL else 3,
                ))

        # Debt optimization
        if debts:
            highest_apr_debt = debts[0]  # Already sorted by APR
            if highest_apr_debt.apr > 10:
                rec_id += 1
                extra_payment = 100
                interest_saved = extra_payment * highest_apr_debt.apr / 100
                recommendations.append(Recommendation(
                    id=f"rec_{rec_id}",
                    title=f"Paga extra su {highest_apr_debt.name}",
                    description=f"APR {highest_apr_debt.apr}% e il piu alto. Ogni euro extra riduce interessi.",
                    impact_monthly=0,
                    impact_annual=interest_saved,
                    difficulty=Difficulty.MEDIUM,
                    category="debt",
                    action_steps=[
                        "Identifica €100 extra dai risparmi",
                        f"Fai bonifico a {highest_apr_debt.name}",
                        "Specifica 'imputare al capitale'",
                        "Ripeti ogni mese",
                    ],
                    priority=2,
                ))

        # Sort by priority and impact
        recommendations.sort(key=lambda x: (x.priority, -x.impact_annual))

        return recommendations

    def _generate_month_comparison(self, month: str) -> List[MonthComparison]:
        """Generate month-over-month comparison."""
        comparisons = []

        # Get current and previous month data
        current_month = month
        ref_date = datetime.strptime(month + "-01", "%Y-%m-%d")
        previous_month = (ref_date - relativedelta(months=1)).strftime("%Y-%m")

        current_spending = get_spending_by_category(current_month)
        previous_spending = get_spending_by_category(previous_month)

        # Create lookup for previous month
        prev_lookup = {
            s.get("category_name", ""): abs(s.get("total_spent", 0) or 0)
            for s in previous_spending
        }

        # Skip categories
        skip = ["Stipendio", "Trasferimenti", "Risparmi Automatici"]

        for cat_data in current_spending:
            cat_name = cat_data.get("category_name", "")
            if cat_name in skip:
                continue

            current = abs(cat_data.get("total_spent", 0) or 0)
            previous = prev_lookup.get(cat_name, 0)

            if current < 10 and previous < 10:
                continue

            delta = current - previous
            delta_pct = (delta / previous * 100) if previous > 0 else 0

            if delta_pct > 10:
                trend = "up"
            elif delta_pct < -10:
                trend = "down"
            else:
                trend = "stable"

            comparisons.append(MonthComparison(
                category=cat_name,
                current_month=current,
                previous_month=previous,
                delta=delta,
                delta_percent=delta_pct,
                trend=trend,
            ))

        # Sort by absolute delta
        comparisons.sort(key=lambda x: -abs(x.delta))

        return comparisons

    def to_dict(self, report: FullFinancialReport) -> Dict[str, Any]:
        """Convert report to dictionary for API response."""
        return {
            "report_date": report.report_date.isoformat(),
            "month": report.month,
            "executive_summary": {
                "health_score": report.executive_summary.health_score,
                "health_grade": report.executive_summary.health_grade,
                "total_income": report.executive_summary.total_income,
                "total_expenses": report.executive_summary.total_expenses,
                "net_savings": report.executive_summary.net_savings,
                "savings_rate": report.executive_summary.savings_rate,
                "total_debt": report.executive_summary.total_debt,
                "debt_payment_monthly": report.executive_summary.debt_payment_monthly,
                "months_to_debt_free": report.executive_summary.months_to_debt_free,
                "overall_judgment": report.executive_summary.overall_judgment.value,
                "key_issues": report.executive_summary.key_issues,
                "key_wins": report.executive_summary.key_wins,
            },
            "category_spending": [
                {
                    "category": cs.category,
                    "icon": cs.icon,
                    "amount_current": cs.amount_current,
                    "amount_avg_3m": cs.amount_avg_3m,
                    "benchmark": cs.benchmark,
                    "judgment": cs.judgment.value,
                    "variance_percent": cs.variance_percent,
                    "notes": cs.notes,
                    "suggestion": cs.suggestion,
                }
                for cs in report.category_spending
            ],
            "subscription_audit": [
                {
                    "name": sa.name,
                    "category": sa.category,
                    "monthly_cost": sa.monthly_cost,
                    "annual_cost": sa.annual_cost,
                    "action": sa.action.value,
                    "reason": sa.reason,
                    "potential_savings": sa.potential_savings,
                    "value_score": sa.value_score,
                    "alternative": sa.alternative,
                }
                for sa in report.subscription_audit
            ],
            "debt_priority": [
                {
                    "id": dp.id,
                    "name": dp.name,
                    "balance": dp.balance,
                    "apr": dp.apr,
                    "monthly_payment": dp.monthly_payment,
                    "interest_monthly": dp.interest_monthly,
                    "principal_monthly": dp.principal_monthly,
                    "priority_score": dp.priority_score,
                    "months_remaining": dp.months_remaining,
                    "payoff_date": dp.payoff_date.isoformat() if dp.payoff_date else None,
                    "total_remaining_cost": dp.total_remaining_cost,
                }
                for dp in report.debt_priority
            ],
            "recommendations": [
                {
                    "id": rec.id,
                    "title": rec.title,
                    "description": rec.description,
                    "impact_monthly": rec.impact_monthly,
                    "impact_annual": rec.impact_annual,
                    "difficulty": rec.difficulty.value,
                    "category": rec.category,
                    "action_steps": rec.action_steps,
                    "priority": rec.priority,
                }
                for rec in report.recommendations
            ],
            "month_comparison": [
                {
                    "category": mc.category,
                    "current_month": mc.current_month,
                    "previous_month": mc.previous_month,
                    "delta": mc.delta,
                    "delta_percent": mc.delta_percent,
                    "trend": mc.trend,
                }
                for mc in report.month_comparison
            ],
        }
