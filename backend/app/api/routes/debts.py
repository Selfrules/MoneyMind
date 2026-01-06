"""Debt API routes."""
import sys
from pathlib import Path

# Add project root to path for src imports
ROUTES_DIR = Path(__file__).parent
API_DIR = ROUTES_DIR.parent
APP_DIR = API_DIR.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_DIR = BACKEND_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from app.schemas.debts import (
    DebtResponse,
    DebtSummaryResponse,
    DebtTimelineEntry,
    DebtTimelineResponse,
    MonthlyPlanEntry,
    MonthlyDebtPlanResponse,
    PaymentHistoryEntry,
)
from app.api.deps import get_db
from src.database import (
    get_debts,
    get_debt_by_id,
    get_debt_plans_for_month,
    get_total_debt,
    get_transactions,
)
from src.analytics import calculate_debt_payoff_avalanche, calculate_debt_payoff_snowball
from src.core_finance.debt_planner import DebtPlanner


# Mapping patterns to match transactions to debts
# Key: debt name as stored in database
DEBT_PAYMENT_PATTERNS = {
    "Agos - Prestito Personale": {
        "patterns": ["pr.", "agos", "77260688"],
        "amount_range": (80, 110),
    },
    "Findomestic - Prestito Personale 2": {
        "patterns": ["202216820433692026643530190020221682043369"],
        "amount_range": (150, 160),
    },
    "Findomestic - Prestito Personale 3": {
        "patterns": ["202218724931422026643530190020221872493142"],
        "amount_range": (120, 130),
    },
    "Revolut Credit": {
        "patterns": ["repayment"],
        "amount_range": (170, 200),
    },
}


def match_transaction_to_debt(tx_description: str, tx_amount: float, debt_name: str) -> bool:
    """Check if a transaction matches a specific debt payment."""
    amount = abs(tx_amount)
    desc_lower = tx_description.lower()

    if debt_name not in DEBT_PAYMENT_PATTERNS:
        return False

    config = DEBT_PAYMENT_PATTERNS[debt_name]
    patterns = config.get("patterns", [])
    amount_range = config.get("amount_range", (0, 0))

    # Check if amount is in expected range
    if not (amount_range[0] <= amount <= amount_range[1]):
        return False

    # Check if any pattern matches
    for pattern in patterns:
        if pattern.lower() in desc_lower:
            return True

    return False


def get_debt_payments(debt: dict) -> list:
    """Get all transactions that match this debt's payments."""
    # Get all transactions in Finanziamenti category
    txs = get_transactions({"category": "Finanziamenti"})

    payments = []
    for tx in txs:
        if tx["amount"] >= 0:  # Skip income/refunds
            continue

        if match_transaction_to_debt(tx["description"], tx["amount"], debt["name"]):
            payments.append({
                "date": tx["date"],
                "amount": abs(tx["amount"]),
                "description": tx["description"][:60],
            })

    return sorted(payments, key=lambda x: x["date"], reverse=True)

router = APIRouter()


def calculate_payoff_info(debt: dict) -> dict:
    """Calculate payoff date and months remaining for a debt."""
    if debt["current_balance"] <= 0 or debt["monthly_payment"] <= 0:
        return {"payoff_date": None, "months_remaining": None, "total_interest": None}

    balance = debt["current_balance"]
    monthly_rate = debt["interest_rate"] / 100 / 12
    payment = debt["monthly_payment"]

    if monthly_rate > 0 and payment <= balance * monthly_rate:
        # Payment too low to ever pay off
        return {"payoff_date": None, "months_remaining": None, "total_interest": None}

    months = 0
    total_interest = 0

    while balance > 0 and months < 360:  # Max 30 years
        interest = balance * monthly_rate
        total_interest += interest
        principal = min(payment - interest, balance)
        balance -= principal
        months += 1

    payoff_date = datetime.now().date() + relativedelta(months=months)

    return {
        "payoff_date": payoff_date,
        "months_remaining": months,
        "total_interest": round(total_interest, 2)
    }


# ============================================================================
# STATIC ROUTES MUST COME BEFORE PARAMETERIZED ROUTES
# ============================================================================

@router.get("/debts/journey")
async def get_debt_journey():
    """Get comprehensive debt-free journey summary with phase tracking."""
    planner = DebtPlanner()
    journey = planner.get_debt_journey_summary()

    return {
        "phase_info": journey["phase_info"],
        "total_original_debt": journey["total_original_debt"],
        "total_current_debt": journey["total_current_debt"],
        "total_paid": journey["total_paid"],
        "overall_progress_percent": journey["overall_progress_percent"],
        "monthly_payment": journey["monthly_payment"],
        "projected_payoff_date": journey.get("projected_payoff_date"),
        "months_remaining": journey["months_remaining"],
        "interest_remaining": journey["interest_remaining"],
        "potential_interest_saved": journey["potential_interest_saved"],
        "milestones": journey["milestones"],
    }


@router.get("/debts/timeline", response_model=DebtTimelineResponse)
async def get_debt_timeline(
    strategy: str = Query("avalanche", description="Payoff strategy: avalanche or snowball"),
    extra_payment: float = Query(0, description="Extra monthly payment")
):
    """Get debt payoff timeline with specified strategy."""
    if strategy == "avalanche":
        payoff_data = calculate_debt_payoff_avalanche(extra_payment)
    elif strategy == "snowball":
        payoff_data = calculate_debt_payoff_snowball(extra_payment)
    else:
        raise HTTPException(status_code=400, detail="Invalid strategy. Use 'avalanche' or 'snowball'")

    timeline = []
    total_interest = 0
    debt_free_date = None

    for entry in payoff_data:
        timeline.append(DebtTimelineEntry(
            month=entry["month"],
            debt_id=entry["debt_id"],
            debt_name=entry["debt_name"],
            planned_payment=entry["payment"],
            extra_payment=entry.get("extra_payment", 0),
            balance_after=entry["balance_after"],
            is_payoff_month=entry.get("is_payoff", False)
        ))
        total_interest += entry.get("interest", 0)

        if entry.get("is_payoff", False) and entry["balance_after"] == 0:
            debt_free_date = datetime.strptime(entry["month"], "%Y-%m").date()

    return DebtTimelineResponse(
        strategy=strategy,
        timeline=timeline,
        total_months=len(set(e.month for e in timeline)),
        total_interest_paid=round(total_interest, 2),
        debt_free_date=debt_free_date,
        monthly_extra_available=extra_payment
    )


@router.get("/debts/plan/{month}", response_model=MonthlyDebtPlanResponse)
async def get_monthly_plan(month: str):
    """Get debt payment plan for a specific month."""
    plans = get_debt_plans_for_month(month)

    entries = []
    for plan in plans:
        entries.append(MonthlyPlanEntry(
            debt_id=plan["debt_id"],
            debt_name=plan.get("debt_name", "Unknown"),
            planned_payment=plan["planned_payment"],
            extra_payment=plan.get("extra_payment", 0),
            actual_payment=plan.get("actual_payment"),
            status=plan.get("status", "pending"),
            order_in_strategy=plan.get("order_in_strategy", 0)
        ))

    total_planned = sum(e.planned_payment for e in entries)
    total_extra = sum(e.extra_payment for e in entries)
    total_actual = sum(e.actual_payment or 0 for e in entries)

    return MonthlyDebtPlanResponse(
        month=month,
        strategy_type=plans[0].get("strategy_type", "avalanche") if plans else "avalanche",
        total_planned=total_planned,
        total_extra=total_extra,
        total_actual=total_actual,
        entries=entries
    )


# ============================================================================
# MAIN ROUTES
# ============================================================================

@router.get("/debts", response_model=DebtSummaryResponse)
async def get_debts_summary(
    active_only: bool = Query(True, description="Only return active debts")
):
    """Get summary of all debts."""
    debts = get_debts(active_only=active_only)

    # Sort by interest rate for Avalanche priority ranking
    sorted_debts = sorted(debts, key=lambda d: d["interest_rate"], reverse=True)
    debt_priority = {d["id"]: idx + 1 for idx, d in enumerate(sorted_debts)}

    debt_responses = []
    for debt in debts:
        payoff_info = calculate_payoff_info(debt)

        # Get payment history from transactions
        payments = get_debt_payments(debt)
        payments_made = len(payments)
        total_paid = sum(p["amount"] for p in payments)

        # Calculate payments remaining
        if debt["monthly_payment"] > 0:
            payments_remaining = int(debt["current_balance"] / debt["monthly_payment"])
        else:
            payments_remaining = 0

        # Calculate progress percentage
        total_payments = payments_made + payments_remaining
        if total_payments > 0:
            progress_percent = (payments_made / total_payments) * 100
        else:
            progress_percent = 0.0

        # Create payment history entries (last 12)
        payment_history = [
            PaymentHistoryEntry(
                date=p["date"] if isinstance(p["date"], date) else datetime.strptime(p["date"], "%Y-%m-%d").date(),
                amount=p["amount"],
                description=p["description"]
            )
            for p in payments[:12]
        ]

        # Determine recommended strategy based on interest rate
        if debt["interest_rate"] >= 15:
            recommended_strategy = "avalanche"
        elif debt["interest_rate"] <= 5:
            recommended_strategy = "snowball"
        else:
            recommended_strategy = "avalanche"  # Default to avalanche

        debt_responses.append(DebtResponse(
            id=debt["id"],
            name=debt["name"],
            type=debt["type"],
            original_amount=debt["original_amount"],
            current_balance=debt["current_balance"],
            interest_rate=debt["interest_rate"],
            monthly_payment=debt["monthly_payment"],
            payment_day=debt["payment_day"],
            start_date=debt.get("start_date"),
            is_active=debt["is_active"],
            payoff_date=payoff_info["payoff_date"],
            months_remaining=payoff_info["months_remaining"],
            total_interest=payoff_info["total_interest"],
            payments_made=payments_made,
            payments_remaining=payments_remaining,
            total_paid=round(total_paid, 2),
            payment_progress_percent=round(progress_percent, 1),
            payment_history=payment_history,
            priority_rank=debt_priority.get(debt["id"]),
            recommended_strategy=recommended_strategy
        ))

    total_debt = sum(d.current_balance for d in debt_responses)
    total_monthly = sum(d.monthly_payment for d in debt_responses)

    # Calculate overall debt-free date
    if debt_responses:
        latest_payoff = max(
            (d.payoff_date for d in debt_responses if d.payoff_date),
            default=None
        )
        if latest_payoff:
            months_to_freedom = (latest_payoff.year - datetime.now().year) * 12 + \
                               (latest_payoff.month - datetime.now().month)
        else:
            months_to_freedom = None
    else:
        latest_payoff = None
        months_to_freedom = None

    return DebtSummaryResponse(
        total_debt=total_debt,
        total_monthly_payment=total_monthly,
        debts=debt_responses,
        active_count=len([d for d in debt_responses if d.is_active]),
        projected_debt_free_date=latest_payoff,
        months_to_freedom=months_to_freedom
    )


@router.get("/debts/{debt_id}", response_model=DebtResponse)
async def get_debt(debt_id: int):
    """Get a specific debt by ID."""
    debt = get_debt_by_id(debt_id)
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")

    payoff_info = calculate_payoff_info(debt)

    # Get payment history
    payments = get_debt_payments(debt)
    payments_made = len(payments)
    total_paid = sum(p["amount"] for p in payments)

    if debt["monthly_payment"] > 0:
        payments_remaining = int(debt["current_balance"] / debt["monthly_payment"])
    else:
        payments_remaining = 0

    total_payments = payments_made + payments_remaining
    progress_percent = (payments_made / total_payments) * 100 if total_payments > 0 else 0.0

    payment_history = [
        PaymentHistoryEntry(
            date=p["date"] if isinstance(p["date"], date) else datetime.strptime(p["date"], "%Y-%m-%d").date(),
            amount=p["amount"],
            description=p["description"]
        )
        for p in payments[:12]
    ]

    return DebtResponse(
        id=debt["id"],
        name=debt["name"],
        type=debt["type"],
        original_amount=debt["original_amount"],
        current_balance=debt["current_balance"],
        interest_rate=debt["interest_rate"],
        monthly_payment=debt["monthly_payment"],
        payment_day=debt["payment_day"],
        start_date=debt.get("start_date"),
        is_active=debt["is_active"],
        payoff_date=payoff_info["payoff_date"],
        months_remaining=payoff_info["months_remaining"],
        total_interest=payoff_info["total_interest"],
        payments_made=payments_made,
        payments_remaining=payments_remaining,
        total_paid=round(total_paid, 2),
        payment_progress_percent=round(progress_percent, 1),
        payment_history=payment_history
    )
