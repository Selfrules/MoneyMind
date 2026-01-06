"""
Quick Wins Engine for MoneyMind v6.0

Identifies and prioritizes easy-to-implement, high-impact financial optimizations.
Quick wins are scored by:
- Implementation effort (easy = higher score)
- Savings impact (higher = better)
- Confidence level (higher = better)
- Time to realization (faster = better)
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum

from src.database import (
    get_recurring_expenses,
    get_debts,
    get_transactions,
    get_spending_by_category,
    get_db_context,
)
from src.ai.recurring_optimizer import RecurringOptimizer, OptimizationStrategy


class QuickWinType(str, Enum):
    SUBSCRIPTION_CANCEL = "subscription_cancel"
    SUBSCRIPTION_DOWNGRADE = "subscription_downgrade"
    PROVIDER_SWITCH = "provider_switch"
    NEGOTIATE_RATE = "negotiate_rate"
    SPENDING_CUT = "spending_cut"
    DEBT_OPTIMIZATION = "debt_optimization"
    AUTOMATION = "automation"


@dataclass
class QuickWin:
    """A prioritized quick win opportunity."""
    id: str
    type: QuickWinType
    title: str
    description: str

    # Impact metrics
    estimated_savings_monthly: float
    estimated_savings_annual: float
    payoff_impact_days: int

    # Effort metrics
    effort_level: str  # "trivial", "easy", "medium", "hard"
    time_to_complete: str  # "5 min", "30 min", "1 hour", "few days"

    # Scoring
    quick_win_score: float  # 0-100, higher is better
    confidence: float  # 0-1

    # Action details
    action_steps: List[str]
    cta_text: str  # Call to action button text
    cta_url: Optional[str] = None  # Optional URL for action

    # Context
    category: Optional[str] = None
    provider: Optional[str] = None
    recurring_expense_id: Optional[int] = None
    debt_id: Optional[int] = None

    # Display
    icon: str = "💰"
    priority_badge: str = "Quick Win"


@dataclass
class QuickWinsReport:
    """Complete quick wins analysis."""
    wins: List[QuickWin]
    total_monthly_savings: float
    total_annual_savings: float
    total_payoff_days_saved: int
    easy_wins_count: int
    medium_wins_count: int
    execution_order: List[str]  # List of win IDs in recommended order


class QuickWinsEngine:
    """
    Identifies and prioritizes quick win opportunities.

    Usage:
        engine = QuickWinsEngine(debt_total=23000)
        report = engine.analyze()
        top_5 = engine.get_top_quick_wins(5)
    """

    # Scoring weights
    WEIGHTS = {
        "savings_impact": 0.35,
        "effort_level": 0.30,
        "confidence": 0.20,
        "speed": 0.15,
    }

    # Effort level scores (higher = easier)
    EFFORT_SCORES = {
        "trivial": 100,
        "easy": 80,
        "medium": 50,
        "hard": 20,
    }

    # Speed scores (higher = faster)
    SPEED_SCORES = {
        "5 min": 100,
        "15 min": 90,
        "30 min": 75,
        "1 hour": 50,
        "few hours": 30,
        "few days": 10,
    }

    def __init__(self, debt_total: float = 0, monthly_income: float = 3200):
        self.debt_total = debt_total
        self.monthly_income = monthly_income
        self.recurring_optimizer = RecurringOptimizer(debt_total=debt_total)

    def analyze(self) -> QuickWinsReport:
        """Generate complete quick wins report."""
        wins: List[QuickWin] = []

        # Analyze recurring expenses
        recurring_wins = self._analyze_recurring_expenses()
        wins.extend(recurring_wins)

        # Analyze spending patterns
        spending_wins = self._analyze_spending_patterns()
        wins.extend(spending_wins)

        # Analyze debt optimization
        debt_wins = self._analyze_debt_opportunities()
        wins.extend(debt_wins)

        # Score and sort all wins
        for win in wins:
            win.quick_win_score = self._calculate_score(win)

        wins.sort(key=lambda w: w.quick_win_score, reverse=True)

        # Calculate totals
        total_monthly = sum(w.estimated_savings_monthly for w in wins)
        total_annual = sum(w.estimated_savings_annual for w in wins)
        total_days = sum(w.payoff_impact_days for w in wins)

        easy_count = len([w for w in wins if w.effort_level in ("trivial", "easy")])
        medium_count = len([w for w in wins if w.effort_level == "medium"])

        # Create execution order (easy and high-impact first)
        execution_order = [w.id for w in wins[:10]]

        return QuickWinsReport(
            wins=wins,
            total_monthly_savings=round(total_monthly, 2),
            total_annual_savings=round(total_annual, 2),
            total_payoff_days_saved=total_days,
            easy_wins_count=easy_count,
            medium_wins_count=medium_count,
            execution_order=execution_order,
        )

    def get_top_quick_wins(self, limit: int = 5) -> List[QuickWin]:
        """Get top quick wins sorted by score."""
        report = self.analyze()
        return report.wins[:limit]

    def _calculate_score(self, win: QuickWin) -> float:
        """Calculate composite quick win score (0-100)."""
        # Savings impact score (normalized to 0-100)
        max_savings = 100  # €100/month is max score
        savings_score = min(100, (win.estimated_savings_monthly / max_savings) * 100)

        # Effort score
        effort_score = self.EFFORT_SCORES.get(win.effort_level, 50)

        # Confidence score
        confidence_score = win.confidence * 100

        # Speed score
        speed_score = self.SPEED_SCORES.get(win.time_to_complete, 50)

        # Weighted composite score
        score = (
            savings_score * self.WEIGHTS["savings_impact"] +
            effort_score * self.WEIGHTS["effort_level"] +
            confidence_score * self.WEIGHTS["confidence"] +
            speed_score * self.WEIGHTS["speed"]
        )

        return round(score, 1)

    def _analyze_recurring_expenses(self) -> List[QuickWin]:
        """Analyze recurring expenses for quick wins."""
        wins = []

        try:
            opportunities = self.recurring_optimizer.get_top_opportunities(limit=10)
        except Exception:
            return wins

        for analysis in opportunities:
            if not analysis.recommended_strategy:
                continue

            strategy = analysis.recommended_strategy

            # Map strategy type to quick win type
            win_type_map = {
                "cancel": QuickWinType.SUBSCRIPTION_CANCEL,
                "downgrade": QuickWinType.SUBSCRIPTION_DOWNGRADE,
                "switch": QuickWinType.PROVIDER_SWITCH,
                "renegotiate": QuickWinType.NEGOTIATE_RATE,
                "bundle": QuickWinType.SUBSCRIPTION_DOWNGRADE,
            }

            # Map difficulty to effort level
            effort_map = {
                "easy": "easy",
                "medium": "medium",
                "hard": "hard",
            }

            # Map difficulty to time
            time_map = {
                "easy": "15 min",
                "medium": "30 min",
                "hard": "few hours",
            }

            win = QuickWin(
                id=f"recurring_{analysis.recurring_id}",
                type=win_type_map.get(strategy.strategy_type, QuickWinType.SUBSCRIPTION_DOWNGRADE),
                title=strategy.title,
                description=strategy.description,
                estimated_savings_monthly=strategy.estimated_savings_monthly,
                estimated_savings_annual=strategy.estimated_savings_annual,
                payoff_impact_days=strategy.payoff_impact_days,
                effort_level=effort_map.get(strategy.implementation_difficulty, "medium"),
                time_to_complete=time_map.get(strategy.implementation_difficulty, "30 min"),
                quick_win_score=0,  # Will be calculated
                confidence=strategy.confidence,
                action_steps=strategy.implementation_steps,
                cta_text="Ottimizza ora",
                category=analysis.category,
                provider=analysis.provider,
                recurring_expense_id=analysis.recurring_id,
                icon=self._get_icon_for_category(analysis.category),
                priority_badge=self._get_priority_badge(strategy.estimated_savings_monthly),
            )
            wins.append(win)

        return wins

    def _analyze_spending_patterns(self) -> List[QuickWin]:
        """Analyze spending patterns for quick wins."""
        wins = []

        try:
            # Get current month spending
            today = date.today()
            current_month = today.strftime("%Y-%m")

            spending = get_spending_by_category(current_month)

            # Find categories with high discretionary spending
            discretionary_categories = ["Ristoranti", "Shopping", "Caffe", "Intrattenimento"]

            for cat_data in spending:
                cat_name = cat_data.get("category", "")
                if cat_name not in discretionary_categories:
                    continue

                total = abs(cat_data.get("total", 0))
                if total < 50:  # Min threshold
                    continue

                # Suggest 20% reduction
                savings = total * 0.20

                wins.append(QuickWin(
                    id=f"spending_{cat_name.lower().replace(' ', '_')}",
                    type=QuickWinType.SPENDING_CUT,
                    title=f"Riduci {cat_name} del 20%",
                    description=f"Spendi €{total:.0f}/mese in {cat_name}. Un taglio del 20% è raggiungibile.",
                    estimated_savings_monthly=round(savings, 2),
                    estimated_savings_annual=round(savings * 12, 2),
                    payoff_impact_days=self._calculate_payoff_impact(savings),
                    effort_level="medium",
                    time_to_complete="few days",
                    quick_win_score=0,
                    confidence=0.7,
                    action_steps=[
                        f"Imposta un budget di €{total * 0.8:.0f}/mese per {cat_name}",
                        "Traccia ogni spesa in questa categoria",
                        "Cerca alternative più economiche",
                        "Valuta cosa puoi eliminare"
                    ],
                    cta_text="Imposta budget",
                    category=cat_name,
                    icon=self._get_icon_for_category(cat_name),
                    priority_badge="Risparmio potenziale",
                ))

        except Exception:
            pass

        return wins

    def _analyze_debt_opportunities(self) -> List[QuickWin]:
        """Analyze debt for quick wins (e.g., rate renegotiation)."""
        wins = []

        try:
            debts = get_debts(active_only=True)

            for debt in debts:
                rate = debt.get("interest_rate", 0)
                balance = debt.get("current_balance", 0)
                name = debt.get("name", "Debito")
                debt_id = debt.get("id")

                # High interest rate renegotiation opportunity
                if rate > 10 and balance > 1000:
                    potential_reduction = rate * 0.2  # 20% rate reduction
                    monthly_savings = (balance * potential_reduction / 100) / 12

                    wins.append(QuickWin(
                        id=f"debt_rate_{debt_id}",
                        type=QuickWinType.NEGOTIATE_RATE,
                        title=f"Rinegozia tasso {name}",
                        description=f"Tasso attuale {rate}% è alto. Potresti ottenere ~{rate - potential_reduction:.1f}%.",
                        estimated_savings_monthly=round(monthly_savings, 2),
                        estimated_savings_annual=round(monthly_savings * 12, 2),
                        payoff_impact_days=self._calculate_payoff_impact(monthly_savings),
                        effort_level="medium",
                        time_to_complete="1 hour",
                        quick_win_score=0,
                        confidence=0.5,
                        action_steps=[
                            "Cerca tassi offerti da altre banche",
                            f"Contatta {name} per chiedere riduzione tasso",
                            "Valuta surroga/portabilità se necessario",
                            "Confronta offerte e negozia"
                        ],
                        cta_text="Confronta tassi",
                        debt_id=debt_id,
                        icon="💳",
                        priority_badge="Ottimizzazione debito",
                    ))

                # Extra payment opportunity
                if balance > 500:
                    extra_payment = 50  # Suggest €50 extra
                    days_saved = int((extra_payment / balance) * 365 * (rate / 100))

                    wins.append(QuickWin(
                        id=f"debt_extra_{debt_id}",
                        type=QuickWinType.DEBT_OPTIMIZATION,
                        title=f"Paga €50 extra su {name}",
                        description=f"Un pagamento extra accelera l'estinzione e riduce gli interessi.",
                        estimated_savings_monthly=0,
                        estimated_savings_annual=round(extra_payment * rate / 100, 2),
                        payoff_impact_days=days_saved,
                        effort_level="easy",
                        time_to_complete="5 min",
                        quick_win_score=0,
                        confidence=0.95,
                        action_steps=[
                            "Accedi all'home banking",
                            f"Fai un bonifico extra di €{extra_payment} verso {name}",
                            "Richiedi che venga imputato al capitale"
                        ],
                        cta_text="Paga extra",
                        debt_id=debt_id,
                        icon="🎯",
                        priority_badge="Accelera payoff",
                    ))

        except Exception:
            pass

        return wins

    def _calculate_payoff_impact(self, monthly_savings: float) -> int:
        """Calculate days earlier debt-free."""
        if self.debt_total <= 0 or monthly_savings <= 0:
            return 0
        months_impact = monthly_savings / 50
        return int(months_impact * 30)

    def _get_icon_for_category(self, category: str) -> str:
        """Get icon for category."""
        icons = {
            "Abbonamenti": "📺",
            "Telefonia": "📱",
            "Utenze": "💡",
            "Ristoranti": "🍽️",
            "Shopping": "🛍️",
            "Caffe": "☕",
            "Trasporti": "🚗",
            "Intrattenimento": "🎬",
            "Sport": "🏋️",
            "Assicurazioni": "🛡️",
        }
        return icons.get(category, "💰")

    def _get_priority_badge(self, savings: float) -> str:
        """Get priority badge based on savings."""
        if savings >= 50:
            return "🔥 Alta priorità"
        elif savings >= 20:
            return "⭐ Media priorità"
        else:
            return "Quick Win"

    def to_dict(self, win: QuickWin) -> Dict[str, Any]:
        """Convert QuickWin to dictionary for API response."""
        return {
            "id": win.id,
            "type": win.type.value,
            "title": win.title,
            "description": win.description,
            "estimated_savings_monthly": win.estimated_savings_monthly,
            "estimated_savings_annual": win.estimated_savings_annual,
            "payoff_impact_days": win.payoff_impact_days,
            "effort_level": win.effort_level,
            "time_to_complete": win.time_to_complete,
            "quick_win_score": win.quick_win_score,
            "confidence": win.confidence,
            "action_steps": win.action_steps,
            "cta_text": win.cta_text,
            "cta_url": win.cta_url,
            "category": win.category,
            "provider": win.provider,
            "recurring_expense_id": win.recurring_expense_id,
            "debt_id": win.debt_id,
            "icon": win.icon,
            "priority_badge": win.priority_badge,
        }

    def report_to_dict(self, report: QuickWinsReport) -> Dict[str, Any]:
        """Convert QuickWinsReport to dictionary for API response."""
        return {
            "wins": [self.to_dict(w) for w in report.wins],
            "total_monthly_savings": report.total_monthly_savings,
            "total_annual_savings": report.total_annual_savings,
            "total_payoff_days_saved": report.total_payoff_days_saved,
            "easy_wins_count": report.easy_wins_count,
            "medium_wins_count": report.medium_wins_count,
            "execution_order": report.execution_order,
        }
