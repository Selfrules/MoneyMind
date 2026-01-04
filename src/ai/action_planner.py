"""
Action Planner for MoneyMind v4.0

Generates 1-3 daily actions automatically (Full Auto mode).
Actions are high-impact, actionable tasks that help users:
- Reduce spending
- Optimize recurring expenses
- Accelerate debt payoff
- Build savings

Action Types:
- review_subscription: Review a recurring expense for optimization
- increase_payment: Increase debt payment
- cut_category: Reduce spending in a category
- confirm_budget: Confirm/adjust monthly budget
- check_progress: Review progress vs goals
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from dateutil.relativedelta import relativedelta

from src.database import (
    create_daily_action,
    get_today_actions,
    get_pending_action_count,
    get_recurring_expenses,
    get_debts,
    get_budgets,
    get_spending_by_category,
    get_action_history,
)
from src.ai.insight_engine import InsightEngine, Insight


@dataclass
class DailyAction:
    """A single daily action task."""
    title: str
    description: str
    action_type: str
    impact_type: str  # savings, payoff_acceleration, budget_control
    priority: int  # 1 = highest
    estimated_impact_monthly: Optional[float]
    estimated_impact_payoff_days: Optional[int]
    category_id: Optional[int] = None
    debt_id: Optional[int] = None
    recurring_expense_id: Optional[int] = None
    insight_id: Optional[int] = None


class ActionPlanner:
    """
    Generates daily actions automatically (Full Auto mode).

    Usage:
        planner = ActionPlanner()
        actions = planner.generate_daily_actions()
        for action in actions:
            planner.save_action(action)
    """

    # Maximum actions per day to avoid overwhelm
    MAX_ACTIONS_PER_DAY = 3

    # Minimum days between similar actions
    ACTION_COOLDOWN_DAYS = 7

    def __init__(self):
        self.insight_engine = InsightEngine()

    def generate_daily_actions(self, action_date: date = None) -> List[DailyAction]:
        """
        Generate 1-3 daily actions for the given date.

        Process:
        1. Check what actions already exist for today
        2. Check recent action history to avoid repetition
        3. Generate new actions from insights
        4. Prioritize and limit to max 3

        Args:
            action_date: Date to generate actions for (default: today)

        Returns:
            List of DailyAction (max 3)
        """
        if action_date is None:
            action_date = date.today()

        # Check existing actions
        existing = get_today_actions(action_date.isoformat())
        if len(existing) >= self.MAX_ACTIONS_PER_DAY:
            return []  # Already have enough actions

        slots_available = self.MAX_ACTIONS_PER_DAY - len(existing)

        # Get recent action history to avoid repetition
        recent_history = get_action_history(days=self.ACTION_COOLDOWN_DAYS)
        recent_types = self._extract_recent_action_types(recent_history)

        # Generate candidate actions
        candidates = []

        # 1. Actions from insights
        insights = self.insight_engine.generate_daily_insights(max_insights=10)
        for insight in insights:
            action = self._create_action_from_insight(insight)
            if action and not self._is_similar_to_recent(action, recent_types):
                candidates.append(action)

        # 2. Proactive recurring expense reviews
        recurring_actions = self._generate_recurring_review_actions()
        for action in recurring_actions:
            if not self._is_similar_to_recent(action, recent_types):
                candidates.append(action)

        # 3. Budget check action (monthly)
        budget_action = self._generate_budget_check_action(action_date)
        if budget_action and not self._is_similar_to_recent(budget_action, recent_types):
            candidates.append(budget_action)

        # 4. Progress check action (weekly)
        progress_action = self._generate_progress_check_action(action_date)
        if progress_action and not self._is_similar_to_recent(progress_action, recent_types):
            candidates.append(progress_action)

        # Prioritize and limit
        candidates = self._prioritize_actions(candidates)
        return candidates[:slots_available]

    def _create_action_from_insight(self, insight: Insight) -> Optional[DailyAction]:
        """Convert an insight into an actionable task."""

        if insight.type == "budget_overrun":
            return DailyAction(
                title=f"Controlla spese {insight.category}",
                description=insight.message,
                action_type="cut_category",
                impact_type="budget_control",
                priority=1 if insight.severity == "alert" else 2,
                estimated_impact_monthly=insight.impact_monthly,
                estimated_impact_payoff_days=insight.impact_payoff_days,
                category_id=insight.related_category_id,
            )

        elif insight.type == "spending_anomaly":
            return DailyAction(
                title=f"Rivedi spese anomale in {insight.category}",
                description=insight.message,
                action_type="cut_category",
                impact_type="savings",
                priority=2,
                estimated_impact_monthly=insight.impact_monthly,
                estimated_impact_payoff_days=insight.impact_payoff_days,
                category_id=insight.related_category_id,
            )

        elif insight.type == "recurring_opportunity":
            return DailyAction(
                title=insight.title,
                description=insight.message,
                action_type="review_subscription",
                impact_type="savings",
                priority=2,
                estimated_impact_monthly=insight.impact_monthly,
                estimated_impact_payoff_days=insight.impact_payoff_days,
                recurring_expense_id=insight.related_recurring_id,
            )

        elif insight.type == "debt_acceleration":
            return DailyAction(
                title=insight.title,
                description=insight.message,
                action_type="increase_payment",
                impact_type="payoff_acceleration",
                priority=2,
                estimated_impact_monthly=insight.impact_monthly,
                estimated_impact_payoff_days=insight.impact_payoff_days,
                debt_id=insight.related_debt_id,
            )

        elif insight.type == "savings_increase":
            if insight.severity == "warning":
                return DailyAction(
                    title="Rivedi le spese del mese",
                    description=insight.message,
                    action_type="cut_category",
                    impact_type="savings",
                    priority=2,
                    estimated_impact_monthly=insight.impact_monthly,
                    estimated_impact_payoff_days=insight.impact_payoff_days,
                )
            # Positive savings insights don't need actions
            return None

        return None

    def _generate_recurring_review_actions(self) -> List[DailyAction]:
        """Generate actions for reviewing recurring expenses."""
        actions = []

        recurring = get_recurring_expenses(active_only=True)

        for exp in recurring:
            if exp.get("is_essential"):
                continue
            if exp.get("optimization_status") != "not_reviewed":
                continue

            avg_amount = exp.get("avg_amount", 0)
            if avg_amount < 15:  # Skip very small amounts
                continue

            provider = exp.get("provider", exp.get("pattern_name", "abbonamento"))
            potential_savings = avg_amount * 0.15  # Conservative estimate

            actions.append(DailyAction(
                title=f"Rivedi {provider}",
                description=f"Paghi €{avg_amount:.0f}/mese. Verifica se puoi trovare alternative migliori.",
                action_type="review_subscription",
                impact_type="savings",
                priority=3,
                estimated_impact_monthly=potential_savings,
                estimated_impact_payoff_days=int(potential_savings * 30 / 50),
                recurring_expense_id=exp.get("id"),
            ))

        return actions[:3]  # Limit to 3 recurring review suggestions

    def _generate_budget_check_action(self, action_date: date) -> Optional[DailyAction]:
        """Generate budget check action at start of month."""
        # Only suggest on first 3 days of month
        if action_date.day > 3:
            return None

        current_month = action_date.strftime("%Y-%m")
        budgets = get_budgets(current_month)

        if not budgets:
            return DailyAction(
                title="Imposta il budget del mese",
                description="Non hai ancora impostato i budget per questo mese.",
                action_type="confirm_budget",
                impact_type="budget_control",
                priority=1,
                estimated_impact_monthly=None,
                estimated_impact_payoff_days=None,
            )

        return DailyAction(
            title="Conferma budget mensile",
            description="Rivedi e conferma i budget per questo mese.",
            action_type="confirm_budget",
            impact_type="budget_control",
            priority=3,
            estimated_impact_monthly=None,
            estimated_impact_payoff_days=None,
        )

    def _generate_progress_check_action(self, action_date: date) -> Optional[DailyAction]:
        """Generate weekly progress check action."""
        # Only on Sundays
        if action_date.weekday() != 6:
            return None

        return DailyAction(
            title="Controlla i progressi settimanali",
            description="Rivedi i tuoi progressi verso gli obiettivi finanziari.",
            action_type="check_progress",
            impact_type="budget_control",
            priority=3,
            estimated_impact_monthly=None,
            estimated_impact_payoff_days=None,
        )

    def _extract_recent_action_types(self, history: List[dict]) -> Dict[str, date]:
        """Extract recent action types with dates."""
        recent = {}
        for action in history:
            action_type = action.get("action_type", "")
            action_date_str = action.get("action_date", "")
            try:
                action_date = datetime.strptime(action_date_str, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                continue

            # Keep track of most recent date for each type+target combo
            key = f"{action_type}_{action.get('category_id', '')}_{action.get('recurring_expense_id', '')}"
            if key not in recent or action_date > recent[key]:
                recent[key] = action_date

        return recent

    def _is_similar_to_recent(self, action: DailyAction, recent_types: Dict[str, date]) -> bool:
        """Check if action is too similar to recent actions."""
        key = f"{action.action_type}_{action.category_id or ''}_{action.recurring_expense_id or ''}"

        if key in recent_types:
            last_date = recent_types[key]
            days_since = (date.today() - last_date).days
            if days_since < self.ACTION_COOLDOWN_DAYS:
                return True

        return False

    def _prioritize_actions(self, actions: List[DailyAction]) -> List[DailyAction]:
        """Prioritize actions by impact and priority."""
        def score(action: DailyAction) -> float:
            s = (4 - action.priority) * 100  # Lower priority number = higher score

            if action.estimated_impact_monthly:
                s += action.estimated_impact_monthly
            if action.estimated_impact_payoff_days:
                s += action.estimated_impact_payoff_days * 0.5

            return s

        return sorted(actions, key=score, reverse=True)

    def save_action(self, action: DailyAction, action_date: date = None) -> int:
        """Save action to database."""
        if action_date is None:
            action_date = date.today()

        return create_daily_action({
            "action_date": action_date.isoformat(),
            "priority": action.priority,
            "title": action.title,
            "description": action.description,
            "action_type": action.action_type,
            "impact_type": action.impact_type,
            "estimated_impact_monthly": action.estimated_impact_monthly,
            "estimated_impact_payoff_days": action.estimated_impact_payoff_days,
            "category_id": action.category_id,
            "debt_id": action.debt_id,
            "recurring_expense_id": action.recurring_expense_id,
            "insight_id": action.insight_id,
        })

    def estimate_action_impact(self, action: DailyAction) -> Dict[str, Any]:
        """
        Provide detailed impact estimation for an action.

        Returns:
            Dict with monthly savings, annual savings, payoff impact
        """
        monthly = action.estimated_impact_monthly or 0
        annual = monthly * 12
        payoff_days = action.estimated_impact_payoff_days or 0

        impact_level = "alto" if monthly >= 50 or payoff_days >= 30 else "medio" if monthly >= 20 else "basso"

        return {
            "monthly_savings": monthly,
            "annual_savings": annual,
            "payoff_days_reduced": payoff_days,
            "impact_level": impact_level,
            "summary": f"€{monthly:.0f}/mese" if monthly else f"{payoff_days} giorni prima",
        }

    def get_action_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get statistics on action completion."""
        history = get_action_history(days=days)

        total = len(history)
        completed = len([a for a in history if a.get("status") == "completed"])
        pending = len([a for a in history if a.get("status") == "pending"])

        completion_rate = (completed / total * 100) if total > 0 else 0

        # Calculate total estimated impact of completed actions
        total_impact = sum(
            a.get("estimated_impact_monthly", 0) or 0
            for a in history
            if a.get("status") == "completed"
        )

        return {
            "total_actions": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": round(completion_rate, 1),
            "total_estimated_impact_monthly": round(total_impact, 2),
            "period_days": days,
        }
