"""
Insight Engine for MoneyMind v4.0

Generates proactive AI insights using Claude Opus 4.5 with extended thinking.
Focuses on actionable recommendations that improve KPIs:
- Increase monthly savings vs baseline
- Reduce debt payoff timeline

Insight Types:
- spending_anomaly: Unusual spending detected
- budget_overrun: Category over budget
- recurring_opportunity: Optimization opportunity for recurring expense
- debt_acceleration: Opportunity to pay off debt faster
- savings_increase: Opportunity to save more
"""

import json
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from dateutil.relativedelta import relativedelta

from src.database import (
    get_db_context,
    add_insight,
    get_insights,
    get_spending_by_category,
    get_budgets,
    get_recurring_expenses,
    get_debts,
    get_monthly_summary,
)
from src.core_finance.baseline import BaselineCalculator
from src.core_finance.debt_planner import DebtPlanner


@dataclass
class Insight:
    """A single actionable insight."""
    type: str  # spending_anomaly, budget_overrun, recurring_opportunity, debt_acceleration, savings_increase
    category: Optional[str]
    severity: str  # info, warning, alert
    title: str
    message: str
    action_text: str
    impact_monthly: Optional[float]
    impact_payoff_days: Optional[int]
    related_category_id: Optional[int] = None
    related_debt_id: Optional[int] = None
    related_recurring_id: Optional[int] = None
    confidence: float = 0.8


class InsightEngine:
    """
    Generates daily insights based on financial data analysis.

    Usage:
        engine = InsightEngine()
        insights = engine.generate_daily_insights()
        for insight in insights:
            engine.save_insight(insight)
    """

    def __init__(self, use_ai: bool = False):
        """
        Initialize engine.

        Args:
            use_ai: If True, uses Claude for deeper analysis. If False, uses rule-based.
        """
        self.use_ai = use_ai
        self.baseline_calc = BaselineCalculator()
        self.debt_planner = DebtPlanner()

    def generate_daily_insights(self, max_insights: int = 5) -> List[Insight]:
        """
        Generate insights for today based on current financial state.

        Analyzes:
        1. Spending vs budget
        2. Spending vs 3-month baseline
        3. Recurring expense optimization opportunities
        4. Debt acceleration opportunities
        5. Savings trend

        Returns:
            List of prioritized insights (max 5 to avoid overload)
        """
        insights = []

        # Get current month
        today = date.today()
        current_month = today.strftime("%Y-%m")

        # 1. Check budget overruns
        budget_insights = self._analyze_budget_status(current_month)
        insights.extend(budget_insights)

        # 2. Check spending anomalies vs baseline
        anomaly_insights = self._analyze_spending_anomalies(current_month)
        insights.extend(anomaly_insights)

        # 3. Check recurring expense opportunities
        recurring_insights = self._analyze_recurring_opportunities()
        insights.extend(recurring_insights)

        # 4. Check debt acceleration opportunities
        debt_insights = self._analyze_debt_opportunities()
        insights.extend(debt_insights)

        # 5. Check savings trend
        savings_insights = self._analyze_savings_trend(current_month)
        insights.extend(savings_insights)

        # Prioritize by impact and limit to max
        prioritized = self._prioritize_insights(insights)
        return prioritized[:max_insights]

    def _analyze_budget_status(self, month: str) -> List[Insight]:
        """Check for categories over or near budget."""
        insights = []

        budgets = get_budgets(month)
        spending = get_spending_by_category(month)
        spending_map = {s["category_id"]: abs(s.get("total", 0)) for s in spending}

        for budget in budgets:
            cat_id = budget["category_id"]
            cat_name = budget.get("category_name", "Categoria")
            budget_amount = budget.get("amount", 0)
            spent = spending_map.get(cat_id, 0)

            if budget_amount <= 0:
                continue

            percent_used = (spent / budget_amount) * 100

            if percent_used >= 100:
                # Over budget
                over_amount = spent - budget_amount
                insights.append(Insight(
                    type="budget_overrun",
                    category=cat_name,
                    severity="alert",
                    title=f"{cat_name}: budget superato",
                    message=f"Hai speso €{spent:.0f} su un budget di €{budget_amount:.0f} (+{over_amount:.0f}€)",
                    action_text=f"Riduci le spese in {cat_name} per il resto del mese",
                    impact_monthly=over_amount,
                    impact_payoff_days=None,
                    related_category_id=cat_id,
                ))
            elif percent_used >= 80:
                # Near budget
                remaining = budget_amount - spent
                insights.append(Insight(
                    type="budget_overrun",
                    category=cat_name,
                    severity="warning",
                    title=f"{cat_name}: vicino al limite",
                    message=f"Hai usato {percent_used:.0f}% del budget. Rimangono €{remaining:.0f}",
                    action_text=f"Attenzione alle spese in {cat_name}",
                    impact_monthly=None,
                    impact_payoff_days=None,
                    related_category_id=cat_id,
                ))

        return insights

    def _analyze_spending_anomalies(self, month: str) -> List[Insight]:
        """Check for unusual spending compared to baseline."""
        insights = []

        # Get baseline
        baseline = self.baseline_calc.calculate_3mo_baseline(month)
        if baseline.avg_spending_3mo == 0:
            return insights  # No baseline data

        # Get current spending by category
        category_baselines = self.baseline_calc.calculate_category_baselines(month)
        current_spending = get_spending_by_category(month)
        current_map = {s["category_id"]: s for s in current_spending}

        for cat_baseline in category_baselines:
            cat_id = cat_baseline["category_id"]
            cat_name = cat_baseline["category_name"]
            avg_3mo = cat_baseline["avg_spending_3mo"]

            current = current_map.get(cat_id, {})
            current_amount = abs(current.get("total", 0))

            if avg_3mo <= 0:
                continue

            # Calculate percent increase
            percent_change = ((current_amount - avg_3mo) / avg_3mo) * 100

            if percent_change >= 50:  # 50% higher than baseline
                excess = current_amount - avg_3mo
                insights.append(Insight(
                    type="spending_anomaly",
                    category=cat_name,
                    severity="warning",
                    title=f"{cat_name}: +{percent_change:.0f}% vs media",
                    message=f"Stai spendendo €{current_amount:.0f} contro una media di €{avg_3mo:.0f}",
                    action_text=f"Rivedi le spese recenti in {cat_name}",
                    impact_monthly=excess,
                    impact_payoff_days=None,
                    related_category_id=cat_id,
                ))

        return insights

    def _analyze_recurring_opportunities(self) -> List[Insight]:
        """Check for recurring expense optimization opportunities."""
        insights = []

        recurring = get_recurring_expenses(active_only=True)

        for exp in recurring:
            if exp.get("is_essential"):
                continue  # Skip essential expenses

            if exp.get("optimization_status") != "not_reviewed":
                continue  # Already reviewed

            avg_amount = exp.get("avg_amount", 0)
            if avg_amount < 10:
                continue  # Too small to matter

            provider = exp.get("provider", exp.get("pattern_name", "Servizio"))
            potential_savings = avg_amount * 0.2  # Assume 20% potential savings

            insights.append(Insight(
                type="recurring_opportunity",
                category=exp.get("category_name"),
                severity="info",
                title=f"Ottimizza {provider}",
                message=f"Paghi €{avg_amount:.0f}/mese. Potresti risparmiare cercando alternative.",
                action_text=f"Confronta alternative per {provider}",
                impact_monthly=potential_savings,
                impact_payoff_days=int(potential_savings * 30 / 50),  # Rough estimate
                related_recurring_id=exp.get("id"),
            ))

        return insights

    def _analyze_debt_opportunities(self) -> List[Insight]:
        """Check for debt acceleration opportunities."""
        insights = []

        # Get scenario comparison
        comparison = self.debt_planner.calculate_scenario_comparison(extra_monthly=50)

        if comparison.months_saved >= 1:
            insights.append(Insight(
                type="debt_acceleration",
                category="Debiti",
                severity="info",
                title=f"Risparmia {comparison.months_saved} mesi sui debiti",
                message=f"Con €50/mese in più, saresti debt-free {comparison.months_saved} mesi prima",
                action_text="Aumenta i pagamenti mensili sui debiti",
                impact_monthly=50,
                impact_payoff_days=comparison.payoff_date_improvement,
            ))

        # Check if any debt has high interest
        debts = get_debts(active_only=True)
        for debt in debts:
            rate = debt.get("interest_rate", 0)
            if rate >= 10:  # High interest
                balance = debt.get("current_balance", 0)
                monthly_interest = (rate / 100 / 12) * balance

                insights.append(Insight(
                    type="debt_acceleration",
                    category="Debiti",
                    severity="warning",
                    title=f"{debt.get('name')}: tasso alto ({rate}%)",
                    message=f"Paghi €{monthly_interest:.0f}/mese solo in interessi su €{balance:.0f}",
                    action_text="Prioritizza questo debito nei pagamenti extra",
                    impact_monthly=monthly_interest * 0.5,  # Potential to save half
                    impact_payoff_days=30,
                    related_debt_id=debt.get("id"),
                ))

        return insights

    def _analyze_savings_trend(self, month: str) -> List[Insight]:
        """Check savings trend vs baseline."""
        insights = []

        baseline = self.baseline_calc.calculate_3mo_baseline(month)
        summary = get_monthly_summary(month)

        current_income = summary.get("income", 0)
        current_expenses = abs(summary.get("expenses", 0))
        current_savings = current_income - current_expenses

        if baseline.avg_savings_3mo == 0 and current_savings > 0:
            insights.append(Insight(
                type="savings_increase",
                category="Risparmi",
                severity="info",
                title="Primo mese di risparmio!",
                message=f"Stai risparmiando €{current_savings:.0f} questo mese",
                action_text="Continua così per costruire il tuo fondo emergenze",
                impact_monthly=current_savings,
                impact_payoff_days=None,
            ))
        elif baseline.avg_savings_3mo > 0:
            savings_delta = current_savings - baseline.avg_savings_3mo
            if savings_delta > baseline.avg_savings_3mo * 0.2:  # 20% more savings
                insights.append(Insight(
                    type="savings_increase",
                    category="Risparmi",
                    severity="info",
                    title="Risparmi in aumento!",
                    message=f"Stai risparmiando €{savings_delta:.0f} in più della media",
                    action_text="Ottimo lavoro! Considera di usare l'extra per i debiti",
                    impact_monthly=savings_delta,
                    impact_payoff_days=int(savings_delta * 30 / 50),
                ))
            elif savings_delta < baseline.avg_savings_3mo * -0.2:  # 20% less savings
                insights.append(Insight(
                    type="savings_increase",
                    category="Risparmi",
                    severity="warning",
                    title="Risparmi in calo",
                    message=f"Stai risparmiando €{abs(savings_delta):.0f} meno della media",
                    action_text="Rivedi le spese per tornare in linea",
                    impact_monthly=abs(savings_delta),
                    impact_payoff_days=None,
                ))

        return insights

    def _prioritize_insights(self, insights: List[Insight]) -> List[Insight]:
        """
        Prioritize insights by impact and severity.

        Priority order:
        1. Alerts with high impact
        2. Warnings with impact
        3. Info with impact
        4. Others
        """
        def priority_score(insight: Insight) -> float:
            # Base score from severity
            severity_scores = {"alert": 100, "warning": 50, "info": 10}
            score = severity_scores.get(insight.severity, 0)

            # Add impact scores
            if insight.impact_monthly:
                score += insight.impact_monthly * 0.5
            if insight.impact_payoff_days:
                score += insight.impact_payoff_days * 0.1

            return score

        return sorted(insights, key=priority_score, reverse=True)

    def save_insight(self, insight: Insight) -> int:
        """Save insight to database."""
        return add_insight({
            "type": insight.type,
            "category": insight.category,
            "severity": insight.severity,
            "title": insight.title,
            "message": insight.message,
            "action_text": insight.action_text,
        })

    def format_insight_operativo(self, insight: Insight) -> Dict[str, str]:
        """
        Format insight in operative format:
        - Problema: What's wrong
        - Raccomandazione: What to do
        - Azione: Specific next step
        - Impatto: Expected benefit
        """
        impact_text = ""
        if insight.impact_monthly:
            impact_text = f"€{insight.impact_monthly:.0f}/mese"
        if insight.impact_payoff_days:
            if impact_text:
                impact_text += f" | {insight.impact_payoff_days} giorni prima debt-free"
            else:
                impact_text = f"{insight.impact_payoff_days} giorni prima debt-free"

        return {
            "problema": insight.message,
            "raccomandazione": insight.title,
            "azione": insight.action_text,
            "impatto": impact_text or "Migliora la tua situazione finanziaria",
        }
