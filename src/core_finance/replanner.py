"""
Monthly Replanner for MoneyMind v4.0

Analyzes month performance vs plan and generates new plans.
Helps users stay on track with debt payoff and savings goals.
"""

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from typing import Optional, Dict, List, Any

from src.database import (
    get_monthly_summary,
    get_debts,
    get_budgets,
    get_debt_plans_for_month,
    create_debt_monthly_plan,
    get_spending_by_category,
    get_user_profile,
)
from src.core_finance.debt_planner import DebtPlanner
from src.core_finance.baseline import BaselineCalculator


class MonthlyReplanner:
    """
    Analyzes month performance and generates updated plans.

    Usage:
        replanner = MonthlyReplanner()
        performance = replanner.analyze_month_performance("2026-01")
        new_plan = replanner.generate_replan("2026-02")
        explanation = replanner.explain_changes(old_plan, new_plan)
    """

    def __init__(self):
        self.debt_planner = DebtPlanner()
        self.baseline_calculator = BaselineCalculator()

    def analyze_month_performance(self, month: str) -> Dict[str, Any]:
        """
        Analyze how the month performed vs the plan.

        Args:
            month: Month to analyze (YYYY-MM format)

        Returns:
            Dict with performance metrics and status
        """
        # Get actual spending
        summary = get_monthly_summary(month)
        if not summary:
            return {"status": "no_data", "message": "Nessun dato per questo mese"}

        total_income = summary.get("total_income", 0)
        total_expenses = summary.get("total_expenses", 0)
        actual_savings = total_income - abs(total_expenses)

        # Get budgets for comparison
        budgets = get_budgets(month)
        total_budget = sum(b.get("amount", 0) for b in budgets) if budgets else 0

        # Get debt payment performance
        debts = get_debts(active_only=True)
        debt_plans = get_debt_plans_for_month(month)

        total_planned_payments = sum(
            p.get("planned_payment", 0) + p.get("extra_payment", 0)
            for p in debt_plans
        ) if debt_plans else 0

        # Calculate actual debt payments from transactions (simplified)
        # In reality, we'd match transactions to debts
        debt_category_spending = 0
        spending_by_cat = get_spending_by_category(month)
        for cat in spending_by_cat:
            if cat.get("category_name", "").lower() in ["finanziamenti", "prestiti", "debiti"]:
                debt_category_spending += abs(cat.get("total", 0))

        # Calculate performance metrics
        budget_variance = total_budget - abs(total_expenses) if total_budget > 0 else 0
        budget_status = "under" if budget_variance >= 0 else "over"

        savings_rate = (actual_savings / total_income * 100) if total_income > 0 else 0

        # Determine overall status
        if budget_variance >= 0 and actual_savings > 0:
            status = "on_track"
            status_message = "Ottimo! Sei rimasto nel budget"
        elif budget_variance < 0 and budget_variance > -100:
            status = "slightly_over"
            status_message = "Leggermente sopra budget, ma gestibile"
        elif budget_variance < -100:
            status = "over_budget"
            status_message = "Budget superato - rivediamo il piano"
        else:
            status = "needs_review"
            status_message = "Servono più dati per valutare"

        return {
            "month": month,
            "status": status,
            "status_message": status_message,
            "total_income": total_income,
            "total_expenses": abs(total_expenses),
            "actual_savings": actual_savings,
            "savings_rate": round(savings_rate, 1),
            "total_budget": total_budget,
            "budget_variance": budget_variance,
            "budget_status": budget_status,
            "debt_payments_planned": total_planned_payments,
            "debt_payments_actual": debt_category_spending,
            "categories_over_budget": self._get_categories_over_budget(month),
        }

    def _get_categories_over_budget(self, month: str) -> List[Dict]:
        """Get categories that went over budget."""
        budgets = get_budgets(month)
        spending = get_spending_by_category(month)

        over_budget = []
        budget_by_cat = {b["category_id"]: b for b in budgets} if budgets else {}

        for cat in spending:
            cat_id = cat.get("category_id")
            if cat_id in budget_by_cat:
                budget_amount = budget_by_cat[cat_id].get("amount", 0)
                spent = abs(cat.get("total", 0))
                if spent > budget_amount:
                    over_budget.append({
                        "category_name": cat.get("category_name", ""),
                        "budget": budget_amount,
                        "spent": spent,
                        "over_by": spent - budget_amount,
                        "percent_over": round((spent / budget_amount - 1) * 100, 0) if budget_amount > 0 else 0
                    })

        return sorted(over_budget, key=lambda x: x["over_by"], reverse=True)

    def generate_replan(self, target_month: str) -> Dict[str, Any]:
        """
        Generate a new plan for the target month based on recent performance.

        Args:
            target_month: Month to plan for (YYYY-MM format)

        Returns:
            Dict with the new plan
        """
        profile = get_user_profile()
        monthly_income = profile.get("monthly_net_income", 0) if profile else 0

        # Get baseline for comparison
        baseline = self.baseline_calculator.calculate_3mo_baseline(target_month)

        # Get previous month performance
        prev_month = (datetime.strptime(target_month, "%Y-%m") - relativedelta(months=1)).strftime("%Y-%m")
        prev_performance = self.analyze_month_performance(prev_month)

        # Generate new debt plan
        debts = get_debts(active_only=True)
        debt_plan = []

        if debts:
            # Use debt planner to create optimized plan
            scenario = self.debt_planner.calculate_scenario_comparison()

            # Order debts by interest rate (Avalanche)
            sorted_debts = sorted(debts, key=lambda d: d.get("interest_rate", 0), reverse=True)

            for i, debt in enumerate(sorted_debts):
                debt_plan.append({
                    "debt_id": debt["id"],
                    "debt_name": debt["name"],
                    "planned_payment": debt.get("monthly_payment", 0),
                    "extra_payment": self._calculate_extra_payment(debt, monthly_income, prev_performance),
                    "order_in_strategy": i + 1,
                    "strategy_type": "avalanche"
                })

        # Calculate budget adjustments based on performance
        budget_adjustments = self._suggest_budget_adjustments(prev_performance, monthly_income)

        # Calculate projected savings
        total_debt_payments = sum(d["planned_payment"] + d["extra_payment"] for d in debt_plan)
        total_budget = sum(b["suggested_amount"] for b in budget_adjustments)
        projected_savings = monthly_income - total_debt_payments - total_budget

        return {
            "target_month": target_month,
            "monthly_income": monthly_income,
            "debt_plan": debt_plan,
            "budget_adjustments": budget_adjustments,
            "projected_savings": max(0, projected_savings),
            "projected_savings_rate": round((projected_savings / monthly_income * 100), 1) if monthly_income > 0 else 0,
            "based_on_performance": prev_performance.get("status", "unknown"),
            "recommendations": self._generate_recommendations(prev_performance)
        }

    def _calculate_extra_payment(self, debt: Dict, income: float, performance: Dict) -> float:
        """Calculate suggested extra payment for a debt."""
        # If under budget last month, suggest putting savings toward debt
        if performance.get("budget_status") == "under" and performance.get("budget_variance", 0) > 0:
            # Put 50% of savings toward highest rate debt
            available = performance["budget_variance"] * 0.5
            # Only for highest rate debt
            debts = get_debts(active_only=True)
            if debts:
                sorted_debts = sorted(debts, key=lambda d: d.get("interest_rate", 0), reverse=True)
                if sorted_debts[0]["id"] == debt["id"]:
                    return min(available, 200)  # Cap at 200
        return 0

    def _suggest_budget_adjustments(self, performance: Dict, income: float) -> List[Dict]:
        """Suggest budget adjustments based on performance."""
        adjustments = []

        # Get categories that went over budget
        over_budget = performance.get("categories_over_budget", [])

        for cat in over_budget:
            # Suggest increasing budget slightly if consistently over
            if cat["percent_over"] > 20:
                # Reduce by 10% if way over
                new_amount = cat["budget"] * 0.9
                adjustments.append({
                    "category_name": cat["category_name"],
                    "current_budget": cat["budget"],
                    "suggested_amount": round(new_amount, 0),
                    "change": round(new_amount - cat["budget"], 0),
                    "reason": f"Ridurre spese - superato del {cat['percent_over']:.0f}%"
                })
            else:
                # Adjust to actual spending + 5% buffer
                new_amount = cat["spent"] * 1.05
                adjustments.append({
                    "category_name": cat["category_name"],
                    "current_budget": cat["budget"],
                    "suggested_amount": round(new_amount, 0),
                    "change": round(new_amount - cat["budget"], 0),
                    "reason": "Adeguamento al consumo effettivo"
                })

        return adjustments

    def _generate_recommendations(self, performance: Dict) -> List[str]:
        """Generate specific recommendations based on performance."""
        recommendations = []

        status = performance.get("status", "unknown")

        if status == "on_track":
            recommendations.append("Continua così! Considera di aumentare i pagamenti extra sui debiti.")
            if performance.get("savings_rate", 0) > 20:
                recommendations.append("Ottimo savings rate! Valuta di investire il surplus.")

        elif status == "slightly_over":
            recommendations.append("Rivedi le categorie che hanno sforato per il prossimo mese.")
            over_cats = performance.get("categories_over_budget", [])
            if over_cats:
                top_cat = over_cats[0]["category_name"]
                recommendations.append(f"Focus principale: ridurre {top_cat}")

        elif status == "over_budget":
            recommendations.append("Priorità: rientrare nel budget. Riduci le spese non essenziali.")
            recommendations.append("Considera di sospendere i pagamenti extra sui debiti questo mese.")

        if performance.get("actual_savings", 0) < 0:
            recommendations.append("Attenzione: hai speso più di quanto guadagnato. Rivedi il budget urgentemente.")

        return recommendations

    def explain_changes(self, old_plan: Dict, new_plan: Dict) -> str:
        """
        Generate a human-readable explanation of changes between plans.

        Args:
            old_plan: Previous month's plan
            new_plan: New proposed plan

        Returns:
            Explanation text
        """
        explanations = []

        # Compare debt payments
        old_debt_total = sum(d.get("planned_payment", 0) + d.get("extra_payment", 0) for d in old_plan.get("debt_plan", []))
        new_debt_total = sum(d.get("planned_payment", 0) + d.get("extra_payment", 0) for d in new_plan.get("debt_plan", []))

        if new_debt_total > old_debt_total:
            diff = new_debt_total - old_debt_total
            explanations.append(f"📈 Pagamenti debiti aumentati di €{diff:.0f} per accelerare il payoff")
        elif new_debt_total < old_debt_total:
            diff = old_debt_total - new_debt_total
            explanations.append(f"📉 Pagamenti debiti ridotti di €{diff:.0f} per bilanciare il budget")

        # Compare budget adjustments
        for adj in new_plan.get("budget_adjustments", []):
            if adj["change"] > 0:
                explanations.append(f"⬆️ Budget {adj['category_name']}: +€{adj['change']:.0f} ({adj['reason']})")
            elif adj["change"] < 0:
                explanations.append(f"⬇️ Budget {adj['category_name']}: €{adj['change']:.0f} ({adj['reason']})")

        # Compare projected savings
        old_savings = old_plan.get("projected_savings", 0)
        new_savings = new_plan.get("projected_savings", 0)

        if new_savings > old_savings:
            explanations.append(f"💰 Risparmio previsto aumentato: €{new_savings:.0f} (+€{new_savings - old_savings:.0f})")
        elif new_savings < old_savings:
            explanations.append(f"💰 Risparmio previsto ridotto: €{new_savings:.0f} (€{new_savings - old_savings:.0f})")

        # Add recommendations
        recommendations = new_plan.get("recommendations", [])
        if recommendations:
            explanations.append("\n💡 Raccomandazioni:")
            for rec in recommendations:
                explanations.append(f"  • {rec}")

        return "\n".join(explanations) if explanations else "Nessuna modifica significativa al piano."

    def get_replan_summary(self, month: str) -> Dict[str, Any]:
        """
        Get a complete replanning summary for display.

        Args:
            month: Target month for replanning

        Returns:
            Dict with all replanning information
        """
        prev_month = (datetime.strptime(month, "%Y-%m") - relativedelta(months=1)).strftime("%Y-%m")

        performance = self.analyze_month_performance(prev_month)
        new_plan = self.generate_replan(month)

        # Get current plan if exists
        current_plans = get_debt_plans_for_month(month)
        old_plan = {
            "debt_plan": current_plans if current_plans else [],
            "projected_savings": 0
        }

        explanation = self.explain_changes(old_plan, new_plan)

        return {
            "previous_month": prev_month,
            "target_month": month,
            "performance": performance,
            "new_plan": new_plan,
            "explanation": explanation,
            "action_required": performance.get("status") != "on_track"
        }
