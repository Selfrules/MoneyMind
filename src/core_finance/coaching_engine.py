"""
Coaching Engine for MoneyMind v6.0

Proactive coaching system that generates:
- Nudges: Gentle reminders and suggestions
- Celebrations: Milestone achievements and progress celebrations
- Alerts: Urgent notifications for important financial events
- Motivation: Daily encouragement and tips

The coaching engine aims to keep users engaged and motivated
while guiding them toward their financial freedom goals.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum

from src.database import (
    get_debts,
    get_goals,
    get_transactions,
    get_spending_by_category,
    get_user_profile,
    get_recurring_expenses,
    get_budgets,
    get_db_context,
)


class CoachingEventType(str, Enum):
    NUDGE = "nudge"
    CELEBRATION = "celebration"
    ALERT = "alert"
    MOTIVATION = "motivation"
    MILESTONE = "milestone"
    TIP = "tip"


class CoachingPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CoachingEvent:
    """A coaching event (nudge, celebration, alert, etc.)."""
    id: str
    type: CoachingEventType
    priority: CoachingPriority
    title: str
    message: str
    icon: str
    action_text: Optional[str] = None
    action_url: Optional[str] = None
    trigger_condition: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_dismissible: bool = True


@dataclass
class StreakInfo:
    """User streak information."""
    streak_type: str
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[date]
    is_active: bool


class CoachingEngine:
    """
    Proactive coaching and motivation system.

    Usage:
        engine = CoachingEngine()
        nudges = engine.check_nudge_triggers()
        celebrations = engine.check_celebration_triggers()
        daily = engine.generate_daily_motivation()
    """

    # Motivational messages by phase
    MOTIVATIONS = {
        "diagnosi": [
            "Capire la tua situazione finanziaria è il primo passo verso la libertà! 📊",
            "Ogni euro tracciato è un euro sotto controllo. Continua così! 💪",
            "La consapevolezza finanziaria è potere. Stai costruendo le fondamenta! 🏗️",
        ],
        "ottimizzazione": [
            "Ogni piccolo taglio alle spese accelera il tuo cammino! ✂️",
            "Stai ottimizzando come un pro! I risultati arriveranno. 🚀",
            "Le abitudini che costruisci oggi ti pagheranno per anni! 💰",
        ],
        "sicurezza": [
            "Il tuo fondo emergenza sta crescendo. Sicurezza prima di tutto! 🛡️",
            "Ogni mese senza debiti ti avvicina alla libertà! 🎯",
            "Stai costruendo una base solida per il futuro! 🏠",
        ],
        "crescita": [
            "Il tempo è dalla tua parte. Gli investimenti cresceranno! 📈",
            "FIRE non è un sogno - è un obiettivo raggiungibile! 🔥",
            "Ogni euro investito lavora per te 24/7! 💼",
        ],
    }

    # Tips by category
    TIPS = {
        "general": [
            "Rivedi i tuoi abbonamenti ogni 3 mesi. Spesso paghiamo servizi che non usiamo.",
            "Imposta trasferimenti automatici verso il risparmio il giorno dello stipendio.",
            "Prima di un acquisto importante, aspetta 24 ore. L'impulso passa, la saggezza resta.",
        ],
        "debt": [
            "Concentra i pagamenti extra sul debito con il tasso più alto (metodo valanga).",
            "Ogni €50 extra al mese può ridurre il debito di mesi!",
            "Negozia i tassi di interesse - il peggio che può succedere è un no.",
        ],
        "savings": [
            "Usa la regola del 50/30/20: 50% necessità, 30% desideri, 20% risparmio.",
            "Arrotonda ogni spesa e risparmia la differenza automaticamente.",
            "Un fondo emergenza di 3-6 mesi ti protegge dagli imprevisti.",
        ],
        "spending": [
            "Porta il pranzo da casa almeno 3 volte a settimana.",
            "Confronta i prezzi online prima di acquistare.",
            "Usa app di cashback per risparmiare sugli acquisti quotidiani.",
        ],
    }

    def __init__(self):
        self.today = date.today()
        self.current_month = self.today.strftime("%Y-%m")

    def check_nudge_triggers(self) -> List[CoachingEvent]:
        """Check all trigger conditions and generate nudges."""
        nudges = []

        # Check budget status
        budget_nudges = self._check_budget_status()
        nudges.extend(budget_nudges)

        # Check debt payment reminders
        debt_nudges = self._check_debt_payments()
        nudges.extend(debt_nudges)

        # Check recurring expense opportunities
        recurring_nudges = self._check_recurring_opportunities()
        nudges.extend(recurring_nudges)

        # Check spending anomalies
        spending_nudges = self._check_spending_anomalies()
        nudges.extend(spending_nudges)

        # Sort by priority
        priority_order = {
            CoachingPriority.CRITICAL: 0,
            CoachingPriority.HIGH: 1,
            CoachingPriority.MEDIUM: 2,
            CoachingPriority.LOW: 3,
        }
        nudges.sort(key=lambda n: priority_order.get(n.priority, 99))

        return nudges

    def check_celebration_triggers(self) -> List[CoachingEvent]:
        """Check for achievements and milestones to celebrate."""
        celebrations = []

        # Check debt milestones
        debt_celebrations = self._check_debt_milestones()
        celebrations.extend(debt_celebrations)

        # Check savings milestones
        savings_celebrations = self._check_savings_milestones()
        celebrations.extend(savings_celebrations)

        # Check streak achievements
        streak_celebrations = self._check_streak_achievements()
        celebrations.extend(streak_celebrations)

        # Check budget adherence
        budget_celebrations = self._check_budget_wins()
        celebrations.extend(budget_celebrations)

        return celebrations

    def generate_daily_motivation(self, phase: str = "diagnosi") -> CoachingEvent:
        """Generate AI-powered daily motivational message."""
        import random

        # Get phase-specific motivation
        phase_motivations = self.MOTIVATIONS.get(phase, self.MOTIVATIONS["diagnosi"])
        message = random.choice(phase_motivations)

        # Add a tip sometimes
        if random.random() > 0.5:
            tip_category = random.choice(["general", "debt", "savings", "spending"])
            tip = random.choice(self.TIPS[tip_category])
            message += f"\n\n💡 Tip: {tip}"

        return CoachingEvent(
            id=f"motivation_{self.today.isoformat()}",
            type=CoachingEventType.MOTIVATION,
            priority=CoachingPriority.LOW,
            title="La tua motivazione del giorno",
            message=message,
            icon="✨",
            is_dismissible=True,
        )

    def get_priority_actions(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Get top priority actions for today."""
        actions = []

        try:
            # Check for overdue actions
            debts = get_debts(active_only=True)
            today_day = self.today.day

            for debt in debts:
                payment_day = debt.get("payment_day", 1)
                if payment_day == today_day:
                    actions.append({
                        "priority": "high",
                        "type": "payment",
                        "title": f"Pagamento {debt.get('name')} in scadenza oggi",
                        "description": f"€{debt.get('monthly_payment', 0):.0f} da pagare",
                        "debt_id": debt.get("id"),
                        "icon": "💳",
                    })

            # Check budget status
            try:
                spending = get_spending_by_category(self.current_month)
                budgets = get_budgets(self.current_month)

                budget_map = {b.get("category_id"): b.get("amount") for b in budgets}

                for cat in spending:
                    cat_id = cat.get("category_id")
                    spent = abs(cat.get("total", 0))
                    budget = budget_map.get(cat_id, 0)

                    if budget > 0:
                        pct = (spent / budget) * 100
                        if pct > 90:
                            actions.append({
                                "priority": "medium",
                                "type": "budget_warning",
                                "title": f"Budget {cat.get('category')} quasi esaurito",
                                "description": f"{pct:.0f}% usato - €{budget - spent:.0f} rimasti",
                                "category": cat.get("category"),
                                "icon": "⚠️",
                            })
            except Exception:
                pass

            # Sort by priority
            priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            actions.sort(key=lambda a: priority_order.get(a.get("priority", "low"), 99))

        except Exception:
            pass

        return actions[:limit]

    def _check_budget_status(self) -> List[CoachingEvent]:
        """Check budget status and generate nudges."""
        nudges = []

        try:
            spending = get_spending_by_category(self.current_month)
            budgets = get_budgets(self.current_month)

            budget_map = {b.get("category_id"): b.get("amount") for b in budgets}

            for cat in spending:
                cat_id = cat.get("category_id")
                cat_name = cat.get("category", "")
                spent = abs(cat.get("total", 0))
                budget = budget_map.get(cat_id, 0)

                if budget <= 0:
                    continue

                pct = (spent / budget) * 100

                if pct >= 100:
                    nudges.append(CoachingEvent(
                        id=f"budget_exceeded_{cat_name.lower()}_{self.current_month}",
                        type=CoachingEventType.ALERT,
                        priority=CoachingPriority.HIGH,
                        title=f"Budget {cat_name} superato!",
                        message=f"Hai speso €{spent:.0f} su un budget di €{budget:.0f} ({pct:.0f}%).",
                        icon="🚨",
                        action_text="Rivedi spese",
                        category=cat_name,
                    ))
                elif pct >= 80:
                    nudges.append(CoachingEvent(
                        id=f"budget_warning_{cat_name.lower()}_{self.current_month}",
                        type=CoachingEventType.NUDGE,
                        priority=CoachingPriority.MEDIUM,
                        title=f"Attenzione: {cat_name} all'{pct:.0f}%",
                        message=f"Ti restano €{budget - spent:.0f} per questo mese.",
                        icon="⚠️",
                        category=cat_name,
                    ))

        except Exception:
            pass

        return nudges

    def _check_debt_payments(self) -> List[CoachingEvent]:
        """Check for upcoming debt payments."""
        nudges = []

        try:
            debts = get_debts(active_only=True)
            today_day = self.today.day

            for debt in debts:
                payment_day = debt.get("payment_day", 1)
                debt_name = debt.get("name", "")
                payment_amount = debt.get("monthly_payment", 0)

                # Days until payment
                if payment_day >= today_day:
                    days_until = payment_day - today_day
                else:
                    # Next month
                    days_until = 30 - today_day + payment_day

                if days_until == 0:
                    nudges.append(CoachingEvent(
                        id=f"payment_today_{debt.get('id')}",
                        type=CoachingEventType.ALERT,
                        priority=CoachingPriority.CRITICAL,
                        title=f"Pagamento {debt_name} OGGI",
                        message=f"€{payment_amount:.0f} in scadenza oggi. Assicurati che ci sia copertura.",
                        icon="🔔",
                        action_text="Verifica",
                    ))
                elif days_until <= 3:
                    nudges.append(CoachingEvent(
                        id=f"payment_soon_{debt.get('id')}",
                        type=CoachingEventType.NUDGE,
                        priority=CoachingPriority.HIGH,
                        title=f"Pagamento {debt_name} tra {days_until} giorni",
                        message=f"€{payment_amount:.0f} in scadenza il {payment_day}.",
                        icon="📅",
                    ))

        except Exception:
            pass

        return nudges

    def _check_recurring_opportunities(self) -> List[CoachingEvent]:
        """Check for recurring expense optimization opportunities."""
        nudges = []

        try:
            recurring = get_recurring_expenses(active_only=True)

            for expense in recurring:
                optimization_status = expense.get("optimization_status")
                if optimization_status and optimization_status != "pending":
                    continue

                estimated_savings = expense.get("estimated_savings_monthly", 0)
                if estimated_savings > 10:
                    nudges.append(CoachingEvent(
                        id=f"recurring_opt_{expense.get('id')}",
                        type=CoachingEventType.TIP,
                        priority=CoachingPriority.MEDIUM,
                        title=f"Ottimizza {expense.get('pattern_name', 'abbonamento')}",
                        message=f"Potresti risparmiare €{estimated_savings:.0f}/mese.",
                        icon="💡",
                        action_text="Vedi come",
                    ))

        except Exception:
            pass

        return nudges[:3]  # Limit to top 3

    def _check_spending_anomalies(self) -> List[CoachingEvent]:
        """Check for unusual spending patterns."""
        nudges = []

        try:
            # Compare current month to previous month
            current = get_spending_by_category(self.current_month)

            prev_month = (date(self.today.year, self.today.month, 1) - timedelta(days=1)).strftime("%Y-%m")
            previous = get_spending_by_category(prev_month)

            prev_map = {c.get("category"): abs(c.get("total", 0)) for c in previous}

            for cat in current:
                cat_name = cat.get("category", "")
                current_spent = abs(cat.get("total", 0))
                prev_spent = prev_map.get(cat_name, 0)

                if prev_spent > 50:  # Only compare if meaningful previous spending
                    pct_change = ((current_spent - prev_spent) / prev_spent) * 100

                    if pct_change > 50 and current_spent > 100:
                        nudges.append(CoachingEvent(
                            id=f"spending_spike_{cat_name.lower()}_{self.current_month}",
                            type=CoachingEventType.NUDGE,
                            priority=CoachingPriority.MEDIUM,
                            title=f"Spesa {cat_name} in aumento",
                            message=f"+{pct_change:.0f}% rispetto al mese scorso (€{current_spent:.0f} vs €{prev_spent:.0f})",
                            icon="📊",
                            category=cat_name,
                        ))

        except Exception:
            pass

        return nudges[:2]  # Limit

    def _check_debt_milestones(self) -> List[CoachingEvent]:
        """Check for debt repayment milestones."""
        celebrations = []

        try:
            debts = get_debts(active_only=True)

            for debt in debts:
                original = debt.get("original_amount", 0)
                current = debt.get("current_balance", 0)

                if original <= 0:
                    continue

                paid_pct = ((original - current) / original) * 100

                # Celebrate milestones
                milestones = [25, 50, 75, 90]
                for milestone in milestones:
                    if paid_pct >= milestone and paid_pct < milestone + 5:
                        celebrations.append(CoachingEvent(
                            id=f"debt_milestone_{debt.get('id')}_{milestone}",
                            type=CoachingEventType.CELEBRATION,
                            priority=CoachingPriority.HIGH,
                            title=f"🎉 {debt.get('name')} al {milestone}%!",
                            message=f"Hai pagato {milestone}% del debito! Solo €{current:.0f} rimasti.",
                            icon="🎊",
                        ))
                        break

        except Exception:
            pass

        return celebrations

    def _check_savings_milestones(self) -> List[CoachingEvent]:
        """Check for savings milestones."""
        celebrations = []

        try:
            profile = get_user_profile()
            emergency_fund = profile.get("emergency_fund", 0) if profile else 0
            monthly_expenses = profile.get("monthly_net_income", 3200) * 0.8  # Estimate

            if monthly_expenses > 0:
                months_covered = emergency_fund / monthly_expenses

                milestones = [1, 3, 6, 12]
                for milestone in milestones:
                    if months_covered >= milestone and months_covered < milestone + 0.5:
                        celebrations.append(CoachingEvent(
                            id=f"emergency_fund_{milestone}mo",
                            type=CoachingEventType.CELEBRATION,
                            priority=CoachingPriority.HIGH,
                            title=f"🏆 Fondo emergenza: {milestone} mese/i!",
                            message=f"Hai accumulato €{emergency_fund:.0f} - {milestone} mesi di spese coperte!",
                            icon="🎯",
                        ))
                        break

        except Exception:
            pass

        return celebrations

    def _check_streak_achievements(self) -> List[CoachingEvent]:
        """Check for streak achievements."""
        # Simplified: In production, this would check user_streaks table
        return []

    def _check_budget_wins(self) -> List[CoachingEvent]:
        """Check for budget adherence wins."""
        celebrations = []

        try:
            spending = get_spending_by_category(self.current_month)
            budgets = get_budgets(self.current_month)

            budget_map = {b.get("category_id"): b.get("amount") for b in budgets}

            under_budget_count = 0
            for cat in spending:
                cat_id = cat.get("category_id")
                spent = abs(cat.get("total", 0))
                budget = budget_map.get(cat_id, 0)

                if budget > 0 and spent <= budget * 0.9:
                    under_budget_count += 1

            if under_budget_count >= 5:
                celebrations.append(CoachingEvent(
                    id=f"budget_master_{self.current_month}",
                    type=CoachingEventType.CELEBRATION,
                    priority=CoachingPriority.MEDIUM,
                    title="🌟 Maestro del Budget!",
                    message=f"{under_budget_count} categorie sotto budget questo mese!",
                    icon="👏",
                ))

        except Exception:
            pass

        return celebrations

    def to_dict(self, event: CoachingEvent) -> Dict[str, Any]:
        """Convert CoachingEvent to dictionary."""
        return {
            "id": event.id,
            "type": event.type.value,
            "priority": event.priority.value,
            "title": event.title,
            "message": event.message,
            "icon": event.icon,
            "action_text": event.action_text,
            "action_url": event.action_url,
            "trigger_condition": event.trigger_condition,
            "category": event.category,
            "created_at": event.created_at.isoformat() if event.created_at else None,
            "expires_at": event.expires_at.isoformat() if event.expires_at else None,
            "is_dismissible": event.is_dismissible,
        }
