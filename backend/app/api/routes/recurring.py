"""Recurring expenses API routes."""
import sys
from pathlib import Path
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# Add project root to path for importing src modules
ROUTES_DIR = Path(__file__).parent  # routes/
API_DIR = ROUTES_DIR.parent  # api/
APP_DIR = API_DIR.parent  # app/
BACKEND_DIR = APP_DIR.parent  # backend/
PROJECT_DIR = BACKEND_DIR.parent  # MoneyMind/
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from fastapi import APIRouter, Depends

from app.schemas.recurring import (
    RecurringExpenseResponse,
    RecurringSummaryResponse,
)
from app.api.deps import get_db
from src.repositories.recurring_repository import RecurringRepository
from src.database import get_user_profile
from src.data.transaction_mappings import get_readable_description


router = APIRouter()


def calculate_next_due_date(last_occurrence: date, frequency: str) -> date:
    """Calculate next payment date based on frequency."""
    if not last_occurrence:
        return None

    today = date.today()

    # FIX: Check if subscription is too old (likely cancelled)
    # If last payment was too long ago, don't calculate future due dates
    max_gap_days = {
        "weekly": 30,      # 4 weeks without payment = inactive
        "monthly": 75,     # 2.5 months without payment = inactive
        "quarterly": 150,  # 5 months without payment = inactive
        "annual": 420      # 14 months without payment = inactive
    }
    days_since_last = (today - last_occurrence).days
    if days_since_last > max_gap_days.get(frequency, 75):
        return None  # Subscription likely cancelled, don't show due date

    # Calculate next date based on frequency
    if frequency == "weekly":
        next_date = last_occurrence + relativedelta(weeks=1)
    elif frequency == "monthly":
        next_date = last_occurrence + relativedelta(months=1)
    elif frequency == "quarterly":
        next_date = last_occurrence + relativedelta(months=3)
    elif frequency == "annual":
        next_date = last_occurrence + relativedelta(years=1)
    else:
        next_date = last_occurrence + relativedelta(months=1)

    # If next_date is in the past, keep adding until it's in the future
    # FIX: Add max iterations to prevent infinite loop
    max_iterations = 24
    iterations = 0
    while next_date < today and iterations < max_iterations:
        if frequency == "weekly":
            next_date = next_date + relativedelta(weeks=1)
        elif frequency == "monthly":
            next_date = next_date + relativedelta(months=1)
        elif frequency == "quarterly":
            next_date = next_date + relativedelta(months=3)
        elif frequency == "annual":
            next_date = next_date + relativedelta(years=1)
        else:
            next_date = next_date + relativedelta(months=1)
        iterations += 1

    return next_date


def is_subscription_active(last_occurrence: date, frequency: str) -> bool:
    """
    Determine if a subscription is still active based on last payment date.

    A subscription is considered INACTIVE if too much time has passed
    since the last payment (likely cancelled or no longer used).
    """
    if not last_occurrence:
        return False

    today = date.today()
    days_since_last = (today - last_occurrence).days

    # Thresholds for considering a subscription inactive
    inactivity_thresholds = {
        "weekly": 21,      # 3 weeks without payment = inactive
        "monthly": 60,     # 2 months without payment = inactive
        "quarterly": 120,  # 4 months = inactive
        "annual": 400      # 13 months = inactive
    }

    threshold = inactivity_thresholds.get(frequency, 60)
    return days_since_last <= threshold


def generate_ai_suggestion(exp, monthly_income: float, total_recurring: float):
    """Generate AI-powered optimization suggestion for a recurring expense."""
    monthly_amount = exp.avg_amount
    if exp.frequency == "quarterly":
        monthly_amount = exp.avg_amount / 3
    elif exp.frequency == "annual":
        monthly_amount = exp.avg_amount / 12

    # Calculate budget impact
    budget_impact = (monthly_amount / monthly_income * 100) if monthly_income > 0 else 0

    # Determine action and priority based on rules
    action = "keep"
    reason = ""
    priority = "low"

    if exp.is_essential:
        # Essential expenses: suggest review only if trending up significantly
        if exp.trend_percent and exp.trend_percent > 20:
            action = "renegotiate"
            reason = f"Costo in aumento del {exp.trend_percent:.0f}%. Valuta alternative o rinegozia."
            priority = "medium"
        else:
            action = "keep"
            reason = "Spesa essenziale, importo stabile."
            priority = "low"
    else:
        # Non-essential: evaluate based on impact and trend
        if budget_impact > 5:
            # High impact on budget
            action = "review"
            reason = f"Impatto alto sul budget ({budget_impact:.1f}%). Verifica se è necessario."
            priority = "high"
        elif exp.trend_percent and exp.trend_percent > 15:
            action = "renegotiate"
            reason = f"Costo aumentato del {exp.trend_percent:.0f}%. Cerca offerte migliori."
            priority = "medium"
        elif monthly_amount > 30 and exp.optimization_status == "not_reviewed":
            action = "review"
            reason = f"Abbonamento da €{monthly_amount:.0f}/mese non ancora ottimizzato."
            priority = "medium"
        elif monthly_amount < 10:
            action = "keep"
            reason = "Importo contenuto, impatto minimo sul budget."
            priority = "low"
        else:
            action = "keep"
            reason = "Spesa ragionevole per il servizio."
            priority = "low"

    # Special cases by category
    if exp.category_name == "Abbonamenti":
        if "netflix" in (exp.pattern_name or "").lower():
            if monthly_amount > 15:
                action = "review"
                reason = "Valuta piano base Netflix o condivisione."
                priority = "medium"
        elif "spotify" in (exp.pattern_name or "").lower():
            action = "keep"
            reason = "Spotify: verifica piano Duo o Family se condividi."
            priority = "low"
    elif exp.category_name == "Finanziamenti":
        action = "keep"
        reason = "Finanziamento: rispetta il piano di rimborso."
        priority = "low"
        if exp.trend_percent and exp.trend_percent < -5:
            reason = "Finanziamento in diminuzione, ottimo progresso!"
    elif exp.category_name == "Utenze":
        if exp.trend_percent and exp.trend_percent > 10:
            action = "renegotiate"
            reason = f"Utenza in aumento ({exp.trend_percent:.0f}%). Confronta tariffe."
            priority = "medium"

    return {
        "budget_impact_percent": round(budget_impact, 1),
        "ai_action": action,
        "ai_reason": reason,
        "ai_priority": priority
    }

# Categories that are NOT real subscriptions - regular shopping/dining/services patterns
# These should not appear in the recurring expenses list
NON_SUBSCRIPTION_CATEGORIES = [
    "Spesa",           # Grocery shopping - regular but not a subscription
    "Ristoranti",      # Dining out - regular but not a subscription
    "Caffe",           # Coffee/bars - regular but not a subscription
    "Food Delivery",   # Delivery apps - individual orders, not subscription
    "Trasferimenti",   # Personal transfers - not subscriptions
    "Contanti",        # Cash withdrawals - not subscriptions
    "Shopping",        # General shopping - regular but not a subscription
    "Viaggi",          # Travel - not regular subscriptions
    "Gatti",           # Pet expenses - regular but not cancellable subscriptions
    "Salute",          # Health - not regular subscriptions
    "Barbiere",        # Haircuts - regular but not a subscription
    "Altro",           # Miscellaneous - often false positives
    "Psicologo",       # Therapy sessions (Unobravo) - regular service, not subscription
    "Intrattenimento", # Gaming purchases (Steam), events - one-time, not subscription
]


@router.get("/recurring", response_model=RecurringSummaryResponse)
async def get_recurring_summary():
    """Get summary of all recurring expenses with due dates and AI suggestions."""
    repo = RecurringRepository()

    # Get all active recurring expenses
    all_expenses = repo.get_active()

    # Filter out:
    # 1. Non-subscription categories (regular shopping/dining patterns)
    # 2. Inactive subscriptions (no payment for too long = likely cancelled)
    expenses = [
        exp for exp in all_expenses
        if exp.category_name not in NON_SUBSCRIPTION_CATEGORIES
        and is_subscription_active(exp.last_occurrence, exp.frequency)
    ]

    # Get user profile for income
    profile = get_user_profile()
    monthly_income = profile.get("monthly_net_income", 3000) if profile else 3000

    # Calculate total recurring for context
    total_recurring = sum(
        exp.avg_amount / (3 if exp.frequency == "quarterly" else 12 if exp.frequency == "annual" else 1)
        for exp in expenses
    )

    # Build response
    expense_list = []
    total_monthly = 0.0
    essential_monthly = 0.0
    non_essential_monthly = 0.0
    potential_savings = 0.0
    optimizable_count = 0
    due_this_month_count = 0
    due_this_month_total = 0.0
    high_priority_count = 0

    today = date.today()
    current_month = today.month
    current_year = today.year

    for exp in expenses:
        # Normalize to monthly amount
        monthly_amount = exp.avg_amount
        if exp.frequency == "quarterly":
            monthly_amount = exp.avg_amount / 3
        elif exp.frequency == "annual":
            monthly_amount = exp.avg_amount / 12

        # Calculate next due date
        next_due = calculate_next_due_date(exp.last_occurrence, exp.frequency)
        days_until = (next_due - today).days if next_due else None

        # Check if due this month
        is_due_this_month = (
            next_due and
            next_due.month == current_month and
            next_due.year == current_year
        )

        # Generate AI suggestion
        ai = generate_ai_suggestion(exp, monthly_income, total_recurring)

        # Map cryptic pattern names to readable descriptions
        display_name = get_readable_description(exp.pattern_name or "")

        expense_list.append(RecurringExpenseResponse(
            id=exp.id,
            pattern_name=display_name,
            category_id=exp.category_id,
            category_name=exp.category_name,
            category_icon=exp.category_icon,
            frequency=exp.frequency,
            avg_amount=exp.avg_amount,
            last_amount=exp.last_amount,
            trend_percent=exp.trend_percent,
            last_occurrence=exp.last_occurrence,
            occurrence_count=exp.occurrence_count,
            provider=exp.provider,
            is_essential=exp.is_essential,
            optimization_status=exp.optimization_status,
            optimization_suggestion=exp.optimization_suggestion,
            estimated_savings_monthly=exp.estimated_savings_monthly,
            # New FASE 2 fields
            next_due_date=next_due,
            days_until_due=days_until,
            budget_impact_percent=ai["budget_impact_percent"],
            ai_action=ai["ai_action"],
            ai_reason=ai["ai_reason"],
            ai_priority=ai["ai_priority"]
        ))

        total_monthly += monthly_amount
        if exp.is_essential:
            essential_monthly += monthly_amount
        else:
            non_essential_monthly += monthly_amount

        if exp.estimated_savings_monthly:
            potential_savings += exp.estimated_savings_monthly

        if exp.optimization_status == "not_reviewed" and not exp.is_essential:
            optimizable_count += 1

        if is_due_this_month:
            due_this_month_count += 1
            due_this_month_total += exp.avg_amount

        if ai["ai_priority"] == "high":
            high_priority_count += 1

    # Sort by next due date (soonest first), then by amount
    expense_list.sort(key=lambda x: (
        x.next_due_date or date(2099, 12, 31),
        -x.avg_amount
    ))

    return RecurringSummaryResponse(
        total_monthly=total_monthly,
        essential_monthly=essential_monthly,
        non_essential_monthly=non_essential_monthly,
        potential_savings=potential_savings,
        expenses=expense_list,
        optimizable_count=optimizable_count,
        due_this_month_count=due_this_month_count,
        due_this_month_total=due_this_month_total,
        high_priority_actions=high_priority_count
    )
