"""
Budget Generator for MoneyMind v4.0

Auto-generates budgets based on:
1. Debt payment plan (priority 1)
2. Essential spending from 3-month baseline
3. 50/30/20 rule adapted for debt payoff phase

Debt Phase Rule: 50% needs / 20% wants / 30% savings+debt
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List, Any
from dateutil.relativedelta import relativedelta

from src.database import (
    get_categories,
    get_spending_by_category,
    set_budget,
    get_user_profile,
    get_db_context,
)
from .baseline import BaselineCalculator
from .debt_planner import DebtPlanner


@dataclass
class CategoryBudget:
    """Generated budget for a category."""
    category_id: int
    category_name: str
    category_icon: str
    amount: float
    budget_type: str  # "essential", "discretionary", "savings", "debt"
    source: str  # "baseline", "rule", "manual"
    baseline_avg: float  # 3-month average for reference
    recommended_change: float  # Suggested change from baseline


@dataclass
class GeneratedBudgetPlan:
    """Complete budget plan for a month."""
    month: str
    total_income: float
    debt_allocation: float
    savings_allocation: float
    needs_allocation: float
    wants_allocation: float
    category_budgets: List[CategoryBudget]
    notes: List[str]


class BudgetGenerator:
    """
    Generates budgets from debt plan and spending baselines.

    Usage:
        gen = BudgetGenerator()
        plan = gen.generate_from_debt_plan("2026-02", debt_plan, income=3000)
        gen.save_plan(plan)
    """

    # Categories considered "essential" (needs)
    ESSENTIAL_CATEGORIES = [
        "Alimentari",
        "Utenze",
        "Affitto",
        "Trasporti",
        "Salute",
        "Assicurazioni",
        "Finanziamenti",  # Existing debt payments
    ]

    # Categories considered "savings"
    SAVINGS_CATEGORIES = [
        "Risparmi Automatici",
        "Investimenti",
    ]

    def __init__(self):
        self.baseline_calc = BaselineCalculator()
        self.debt_planner = DebtPlanner()

    def generate_from_debt_plan(self, month: str, debt_plan=None,
                                 income: float = None) -> GeneratedBudgetPlan:
        """
        Generate budget starting from debt payment plan.

        Priority order:
        1. Debt payments (from plan)
        2. Essential expenses (from baseline)
        3. Remaining split between wants and extra savings

        Args:
            month: Target month (YYYY-MM)
            debt_plan: MonthlyDebtPlan (if None, generates one)
            income: Monthly income (if None, uses profile)

        Returns:
            GeneratedBudgetPlan with all category budgets
        """
        # Get income
        if income is None:
            income = self._get_monthly_income()

        if income <= 0:
            return GeneratedBudgetPlan(
                month=month,
                total_income=0,
                debt_allocation=0,
                savings_allocation=0,
                needs_allocation=0,
                wants_allocation=0,
                category_budgets=[],
                notes=["Income not set - please update profile"],
            )

        # Get or generate debt plan
        if debt_plan is None:
            debt_plan = self.debt_planner.generate_monthly_plan(month)

        debt_total = sum(p.planned_payment for p in debt_plan.payments) if debt_plan.payments else 0

        # Get category baselines
        category_baselines = self.baseline_calc.calculate_category_baselines(month)
        baseline_map = {c["category_id"]: c for c in category_baselines}

        # Get all categories
        categories = get_categories()
        category_lookup = {c["id"]: c for c in categories}

        # Apply 50/20/30 rule for debt phase
        allocations = self._calculate_allocations_debt_phase(income, debt_total)

        notes = []
        category_budgets = []

        # 1. Allocate debt payments
        debt_category = self._find_category_by_name("Finanziamenti", categories)
        if debt_category and debt_total > 0:
            category_budgets.append(CategoryBudget(
                category_id=debt_category["id"],
                category_name=debt_category["name"],
                category_icon=debt_category.get("icon", ""),
                amount=debt_total,
                budget_type="debt",
                source="debt_plan",
                baseline_avg=baseline_map.get(debt_category["id"], {}).get("avg_spending_3mo", 0),
                recommended_change=0,
            ))

        # 2. Allocate essential categories
        remaining_needs = allocations["needs"]
        for cat in categories:
            if cat["name"] in self.ESSENTIAL_CATEGORIES and cat["name"] != "Finanziamenti":
                baseline = baseline_map.get(cat["id"], {}).get("avg_spending_3mo", 0)

                # Use baseline or cap at remaining
                amount = min(baseline, remaining_needs) if baseline > 0 else 0
                remaining_needs -= amount

                if amount > 0:
                    category_budgets.append(CategoryBudget(
                        category_id=cat["id"],
                        category_name=cat["name"],
                        category_icon=cat.get("icon", ""),
                        amount=round(amount, 2),
                        budget_type="essential",
                        source="baseline",
                        baseline_avg=baseline,
                        recommended_change=0,
                    ))

        # 3. Allocate savings categories
        remaining_savings = allocations["savings"]
        for cat in categories:
            if cat["name"] in self.SAVINGS_CATEGORIES:
                # Aim for at least baseline or equal split
                baseline = baseline_map.get(cat["id"], {}).get("avg_spending_3mo", 0)
                amount = min(baseline if baseline > 0 else remaining_savings / 2, remaining_savings)
                remaining_savings -= amount

                if amount > 0:
                    category_budgets.append(CategoryBudget(
                        category_id=cat["id"],
                        category_name=cat["name"],
                        category_icon=cat.get("icon", ""),
                        amount=round(amount, 2),
                        budget_type="savings",
                        source="rule",
                        baseline_avg=baseline,
                        recommended_change=0,
                    ))

        # 4. Allocate discretionary (wants) categories
        remaining_wants = allocations["wants"]
        discretionary_cats = [
            c for c in categories
            if c["name"] not in self.ESSENTIAL_CATEGORIES
            and c["name"] not in self.SAVINGS_CATEGORIES
            and c["name"] != "Finanziamenti"
        ]

        # Sort by baseline spending (prioritize categories user actually uses)
        discretionary_cats.sort(
            key=lambda c: baseline_map.get(c["id"], {}).get("avg_spending_3mo", 0),
            reverse=True
        )

        for cat in discretionary_cats:
            if remaining_wants <= 0:
                break

            baseline = baseline_map.get(cat["id"], {}).get("avg_spending_3mo", 0)
            if baseline <= 0:
                continue

            # Budget at 80% of baseline (encourage reduction)
            amount = min(baseline * 0.8, remaining_wants)
            remaining_wants -= amount
            recommended_change = baseline - amount

            category_budgets.append(CategoryBudget(
                category_id=cat["id"],
                category_name=cat["name"],
                category_icon=cat.get("icon", ""),
                amount=round(amount, 2),
                budget_type="discretionary",
                source="baseline",
                baseline_avg=baseline,
                recommended_change=round(recommended_change, 2),
            ))

            if recommended_change > 10:
                notes.append(f"Ridurre {cat['name']} di €{recommended_change:.0f}/mese")

        return GeneratedBudgetPlan(
            month=month,
            total_income=income,
            debt_allocation=debt_total,
            savings_allocation=allocations["savings"],
            needs_allocation=allocations["needs"],
            wants_allocation=allocations["wants"],
            category_budgets=category_budgets,
            notes=notes,
        )

    def save_plan(self, plan: GeneratedBudgetPlan) -> int:
        """
        Save generated budget plan to database.

        Returns:
            Count of budgets saved
        """
        count = 0
        for budget in plan.category_budgets:
            set_budget(
                category_id=budget.category_id,
                amount=budget.amount,
                month=plan.month,
            )
            count += 1
        return count

    def calculate_adjustment_impact(self, category_id: int, current_amount: float,
                                     new_amount: float, month: str) -> Dict[str, Any]:
        """
        Calculate impact of changing a budget on savings and payoff.

        Args:
            category_id: Category being adjusted
            current_amount: Current budget
            new_amount: Proposed new budget
            month: Month of adjustment

        Returns:
            Dict with impact analysis
        """
        delta = new_amount - current_amount

        # Positive delta = spending more = less savings
        # Negative delta = spending less = more savings
        monthly_savings_impact = -delta

        # Estimate payoff impact (rough calculation)
        # Each €100/month extra towards debt = ~X months earlier
        from src.database import get_total_debt
        total_debt = get_total_debt()

        if total_debt > 0 and monthly_savings_impact != 0:
            # Rough estimate: months = debt / monthly_extra
            if monthly_savings_impact > 0:
                months_impact = -int(total_debt / abs(monthly_savings_impact) / 10)  # Approximation
            else:
                months_impact = int(total_debt / abs(monthly_savings_impact) / 10)
        else:
            months_impact = 0

        return {
            "category_id": category_id,
            "budget_change": delta,
            "monthly_savings_impact": round(monthly_savings_impact, 2),
            "direction": "increase" if delta > 0 else "decrease",
            "payoff_impact_months": months_impact,
            "recommendation": "Ridurre" if delta > 0 else "Buona scelta!" if delta < 0 else "Nessun cambiamento",
        }

    def apply_rule_50_30_20_debt_phase(self, income: float,
                                        debt_payments: float) -> Dict[str, float]:
        """
        Apply 50/20/30 rule adapted for debt payoff phase.

        Standard 50/30/20: 50% needs, 30% wants, 20% savings
        Debt phase 50/20/30: 50% needs, 20% wants, 30% savings+debt

        Args:
            income: Monthly net income
            debt_payments: Monthly debt payments required

        Returns:
            Dict with allocations per category type
        """
        return self._calculate_allocations_debt_phase(income, debt_payments)

    def _calculate_allocations_debt_phase(self, income: float,
                                           debt_payments: float) -> Dict[str, float]:
        """
        Calculate budget allocations using debt-phase 50/20/30 rule.

        The 30% for savings+debt is split:
        - First cover debt payments
        - Remainder goes to savings
        """
        needs = income * 0.50
        wants = income * 0.20
        savings_debt = income * 0.30

        # Debt comes from savings+debt bucket
        if debt_payments > savings_debt:
            # Debt exceeds allocation, reduce wants
            overflow = debt_payments - savings_debt
            wants = max(0, wants - overflow)
            savings = 0
        else:
            savings = savings_debt - debt_payments

        return {
            "needs": round(needs, 2),
            "wants": round(wants, 2),
            "savings": round(savings, 2),
            "debt": round(debt_payments, 2),
        }

    def _get_monthly_income(self) -> float:
        """Get monthly income from user profile."""
        profile = get_user_profile()
        if profile:
            return profile.get("monthly_net_income", 0)
        return 0

    def _find_category_by_name(self, name: str, categories: List[dict]) -> Optional[dict]:
        """Find category by name."""
        for cat in categories:
            if cat["name"] == name:
                return cat
        return None

    def suggest_budget_optimizations(self, month: str) -> List[Dict[str, Any]]:
        """
        Analyze current spending and suggest budget optimizations.

        Returns:
            List of optimization suggestions with impact
        """
        baselines = self.baseline_calc.calculate_category_baselines(month)
        categories = get_categories()
        cat_lookup = {c["id"]: c for c in categories}

        suggestions = []

        for baseline in baselines:
            cat_id = baseline["category_id"]
            cat = cat_lookup.get(cat_id, {})
            cat_name = cat.get("name", "")

            # Skip essential and savings categories
            if cat_name in self.ESSENTIAL_CATEGORIES or cat_name in self.SAVINGS_CATEGORIES:
                continue

            avg_spending = baseline["avg_spending_3mo"]

            # Suggest 20% reduction for discretionary spending
            if avg_spending > 50:  # Only for meaningful amounts
                suggested_reduction = avg_spending * 0.20
                suggestions.append({
                    "category_id": cat_id,
                    "category_name": cat_name,
                    "current_avg": avg_spending,
                    "suggested_budget": round(avg_spending * 0.80, 2),
                    "potential_savings": round(suggested_reduction, 2),
                    "difficulty": "easy" if suggested_reduction < 30 else "medium",
                })

        # Sort by potential savings
        suggestions.sort(key=lambda x: x["potential_savings"], reverse=True)

        return suggestions[:5]  # Top 5 suggestions
