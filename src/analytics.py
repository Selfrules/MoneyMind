"""
MoneyMind Analytics Module

Financial KPI calculations, debt payoff strategies, and trend analysis.
"""

from datetime import datetime, timedelta
from typing import Optional
from database import (
    get_transactions, get_monthly_summary, get_debts, get_total_debt,
    get_goals, get_user_profile, get_latest_balances, save_kpi_snapshot,
    get_kpi_history, get_spending_by_category
)


# ============================================================================
# Core KPI Calculations
# ============================================================================

def calculate_net_worth() -> dict:
    """
    Calculate current net worth (Assets - Liabilities).

    Returns:
        dict with total_assets, total_debt, net_worth
    """
    # Assets: current bank balances
    balances = get_latest_balances()
    total_assets = sum(b.get("balance", 0) or 0 for b in balances)

    # Liabilities: total active debt
    total_debt = get_total_debt()

    return {
        "total_assets": total_assets,
        "total_debt": total_debt,
        "net_worth": total_assets - total_debt
    }


def calculate_savings_rate(month: str) -> Optional[float]:
    """
    Calculate savings rate for a month: (Income - Expenses) / Income * 100.

    Uses profile income if transaction income is below threshold (incomplete month).

    Args:
        month: Month in YYYY-MM format

    Returns:
        Savings rate as percentage, or None if no income data
    """
    summary = get_monthly_summary(month)
    profile = get_user_profile()

    # Use transaction income if substantial, otherwise use profile income
    profile_income = profile.get("monthly_net_income", 0) if profile else 0
    transaction_income = summary["total_income"]

    # If transaction income is less than 50% of profile income, use profile income
    # This handles incomplete months where salary hasn't arrived yet
    if transaction_income < profile_income * 0.5 and profile_income > 0:
        monthly_income = profile_income
    else:
        monthly_income = transaction_income

    if monthly_income <= 0:
        return None

    savings = monthly_income - summary["total_expenses"]
    return (savings / monthly_income) * 100


def calculate_dti_ratio(month: str = None) -> Optional[float]:
    """
    Calculate Debt-to-Income ratio: Monthly Debt Payments / Monthly Income * 100.

    Uses profile income for more stable calculation.

    Args:
        month: Optional month for income calculation (defaults to current)

    Returns:
        DTI ratio as percentage, or None if no income data
    """
    if month is None:
        month = datetime.now().strftime("%Y-%m")

    # Prefer profile income for DTI as it's more stable
    profile = get_user_profile()
    profile_income = profile.get("monthly_net_income", 0) if profile else 0

    # Get transaction income as fallback
    summary = get_monthly_summary(month)
    transaction_income = summary["total_income"]

    # Use profile income if available and substantial, otherwise use transaction income
    if profile_income > 0:
        monthly_income = profile_income
    elif transaction_income > 0:
        monthly_income = transaction_income
    else:
        return None

    # Get total monthly debt payments
    debts = get_debts(active_only=True)
    monthly_payments = sum(d.get("monthly_payment", 0) or 0 for d in debts)

    return (monthly_payments / monthly_income) * 100


def calculate_emergency_fund_months(emergency_fund_balance: float = 0) -> float:
    """
    Calculate how many months of expenses the emergency fund covers.

    Args:
        emergency_fund_balance: Current emergency fund balance

    Returns:
        Number of months covered
    """
    # Calculate average monthly expenses over last 3 months
    today = datetime.now()
    total_expenses = 0
    months_counted = 0

    for i in range(1, 4):  # Last 3 complete months
        month_date = today - timedelta(days=30 * i)
        month_str = month_date.strftime("%Y-%m")
        summary = get_monthly_summary(month_str)
        if summary["total_expenses"] > 0:
            total_expenses += summary["total_expenses"]
            months_counted += 1

    if months_counted == 0 or total_expenses == 0:
        return 0

    avg_monthly_expenses = total_expenses / months_counted
    return emergency_fund_balance / avg_monthly_expenses


def get_financial_snapshot(month: str = None) -> dict:
    """
    Get a complete financial snapshot for a month.

    Args:
        month: Month in YYYY-MM format (defaults to current)

    Returns:
        dict with all KPIs and summary data
    """
    if month is None:
        month = datetime.now().strftime("%Y-%m")

    # Basic metrics
    net_worth_data = calculate_net_worth()
    monthly_summary = get_monthly_summary(month)
    savings_rate = calculate_savings_rate(month)
    dti_ratio = calculate_dti_ratio(month)

    # Debt data
    debts = get_debts(active_only=True)
    total_debt = get_total_debt()

    # Goals
    goals = get_goals(status="active")

    # Emergency fund (from savings goals or account)
    emergency_goal = next((g for g in goals if g["type"] == "emergency_fund"), None)
    emergency_fund = emergency_goal["current_amount"] if emergency_goal else 0
    emergency_months = calculate_emergency_fund_months(emergency_fund)

    return {
        "month": month,
        "net_worth": net_worth_data["net_worth"],
        "total_assets": net_worth_data["total_assets"],
        "total_debt": total_debt,
        "total_income": monthly_summary["total_income"],
        "total_expenses": monthly_summary["total_expenses"],
        "net_cash_flow": monthly_summary["net"],
        "savings_rate": savings_rate,
        "dti_ratio": dti_ratio,
        "emergency_fund": emergency_fund,
        "emergency_fund_months": emergency_months,
        "active_debts_count": len(debts),
        "active_goals_count": len(goals),
        "transaction_count": monthly_summary["transaction_count"]
    }


def save_monthly_kpi_snapshot(month: str = None) -> int:
    """
    Calculate and save KPI snapshot for a month.

    Args:
        month: Month in YYYY-MM format (defaults to current)

    Returns:
        KPI record ID
    """
    snapshot = get_financial_snapshot(month)
    return save_kpi_snapshot(month or datetime.now().strftime("%Y-%m"), snapshot)


# ============================================================================
# Debt Analysis & Payoff Strategies
# ============================================================================

def calculate_debt_payoff_avalanche(extra_payment: float = 0) -> list[dict]:
    """
    Calculate debt payoff timeline using Avalanche method (highest interest first).

    Args:
        extra_payment: Additional monthly payment beyond minimums

    Returns:
        List of debts with payoff projections, sorted by payoff order
    """
    debts = get_debts(active_only=True)

    if not debts:
        return []

    # Sort by interest rate (highest first)
    debts_sorted = sorted(
        debts,
        key=lambda d: d.get("interest_rate", 0) or 0,
        reverse=True
    )

    results = []
    freed_payment = 0

    for i, debt in enumerate(debts_sorted):
        balance = debt["current_balance"]
        rate = (debt.get("interest_rate", 0) or 0) / 100 / 12  # Monthly rate
        min_payment = debt.get("monthly_payment", 0) or 0

        # Payment for this debt = minimum + extra + freed payments from paid-off debts
        if i == 0:
            payment = min_payment + extra_payment + freed_payment
        else:
            payment = min_payment + freed_payment

        # Calculate months to payoff
        if payment <= 0:
            months = float("inf")
            total_interest = float("inf")
        elif rate == 0:
            months = balance / payment if payment > 0 else float("inf")
            total_interest = 0
        else:
            # Formula: n = -log(1 - (r*PV/PMT)) / log(1+r)
            import math
            try:
                if payment <= balance * rate:
                    months = float("inf")
                    total_interest = float("inf")
                else:
                    months = -math.log(1 - (rate * balance / payment)) / math.log(1 + rate)
                    total_interest = (payment * months) - balance
            except (ValueError, ZeroDivisionError):
                months = float("inf")
                total_interest = float("inf")

        payoff_date = None
        if months != float("inf"):
            payoff_date = (datetime.now() + timedelta(days=30 * months)).strftime("%Y-%m")
            freed_payment += min_payment  # This payment becomes available for next debt

        results.append({
            "id": debt["id"],
            "name": debt["name"],
            "current_balance": balance,
            "interest_rate": debt.get("interest_rate", 0),
            "monthly_payment": payment,
            "months_to_payoff": months if months != float("inf") else None,
            "payoff_date": payoff_date,
            "total_interest": total_interest if total_interest != float("inf") else None,
            "order": i + 1,
            "strategy": "avalanche"
        })

    return results


def calculate_debt_payoff_snowball(extra_payment: float = 0) -> list[dict]:
    """
    Calculate debt payoff timeline using Snowball method (smallest balance first).

    Args:
        extra_payment: Additional monthly payment beyond minimums

    Returns:
        List of debts with payoff projections, sorted by payoff order
    """
    debts = get_debts(active_only=True)

    if not debts:
        return []

    # Sort by balance (smallest first)
    debts_sorted = sorted(debts, key=lambda d: d["current_balance"])

    results = []
    freed_payment = 0

    for i, debt in enumerate(debts_sorted):
        balance = debt["current_balance"]
        rate = (debt.get("interest_rate", 0) or 0) / 100 / 12
        min_payment = debt.get("monthly_payment", 0) or 0

        if i == 0:
            payment = min_payment + extra_payment + freed_payment
        else:
            payment = min_payment + freed_payment

        if payment <= 0:
            months = float("inf")
            total_interest = float("inf")
        elif rate == 0:
            months = balance / payment if payment > 0 else float("inf")
            total_interest = 0
        else:
            import math
            try:
                if payment <= balance * rate:
                    months = float("inf")
                    total_interest = float("inf")
                else:
                    months = -math.log(1 - (rate * balance / payment)) / math.log(1 + rate)
                    total_interest = (payment * months) - balance
            except (ValueError, ZeroDivisionError):
                months = float("inf")
                total_interest = float("inf")

        payoff_date = None
        if months != float("inf"):
            payoff_date = (datetime.now() + timedelta(days=30 * months)).strftime("%Y-%m")
            freed_payment += min_payment

        results.append({
            "id": debt["id"],
            "name": debt["name"],
            "current_balance": balance,
            "interest_rate": debt.get("interest_rate", 0),
            "monthly_payment": payment,
            "months_to_payoff": months if months != float("inf") else None,
            "payoff_date": payoff_date,
            "total_interest": total_interest if total_interest != float("inf") else None,
            "order": i + 1,
            "strategy": "snowball"
        })

    return results


def compare_payoff_strategies(extra_payment: float = 0) -> dict:
    """
    Compare Avalanche vs Snowball payoff strategies.

    Args:
        extra_payment: Additional monthly payment

    Returns:
        dict comparing both strategies with total time and interest
    """
    avalanche = calculate_debt_payoff_avalanche(extra_payment)
    snowball = calculate_debt_payoff_snowball(extra_payment)

    def sum_metrics(debts):
        total_months = max((d["months_to_payoff"] or 0) for d in debts) if debts else 0
        total_interest = sum((d["total_interest"] or 0) for d in debts)
        return total_months, total_interest

    avalanche_months, avalanche_interest = sum_metrics(avalanche)
    snowball_months, snowball_interest = sum_metrics(snowball)

    interest_saved = snowball_interest - avalanche_interest
    months_saved = snowball_months - avalanche_months

    return {
        "avalanche": {
            "debts": avalanche,
            "total_months": avalanche_months,
            "total_interest": avalanche_interest,
            "last_payoff_date": max((d["payoff_date"] for d in avalanche if d["payoff_date"]), default=None)
        },
        "snowball": {
            "debts": snowball,
            "total_months": snowball_months,
            "total_interest": snowball_interest,
            "last_payoff_date": max((d["payoff_date"] for d in snowball if d["payoff_date"]), default=None)
        },
        "recommendation": "avalanche" if avalanche_interest <= snowball_interest else "snowball",
        "avalanche_interest_saved": interest_saved if interest_saved > 0 else 0,
        "avalanche_months_saved": months_saved if months_saved > 0 else 0
    }


# ============================================================================
# Spending Analysis
# ============================================================================

def get_spending_trends(months: int = 6) -> list[dict]:
    """
    Get spending trends by category over the last N months.

    Args:
        months: Number of months to analyze

    Returns:
        List of monthly spending by category
    """
    today = datetime.now()
    trends = []

    for i in range(months):
        month_date = today - timedelta(days=30 * i)
        month_str = month_date.strftime("%Y-%m")
        spending = get_spending_by_category(month_str)

        trends.append({
            "month": month_str,
            "categories": {s["category_name"]: s["total_spent"] for s in spending},
            "total": sum(s["total_spent"] for s in spending)
        })

    return list(reversed(trends))


def detect_spending_anomalies(month: str = None, threshold: float = 1.5) -> list[dict]:
    """
    Detect categories where spending is anomalously high compared to average.

    Args:
        month: Month to check (defaults to current)
        threshold: Multiple of average to flag as anomaly (default 1.5x)

    Returns:
        List of anomalies with category, amount, average, and deviation
    """
    if month is None:
        month = datetime.now().strftime("%Y-%m")

    # Get current month spending
    current_spending = get_spending_by_category(month)
    current_by_cat = {s["category_name"]: s["total_spent"] for s in current_spending}

    # Get historical averages (last 3 months excluding current)
    today = datetime.now()
    historical = {}
    count = {}

    for i in range(1, 4):
        month_date = today - timedelta(days=30 * i)
        month_str = month_date.strftime("%Y-%m")
        if month_str == month:
            continue

        spending = get_spending_by_category(month_str)
        for s in spending:
            cat = s["category_name"]
            historical[cat] = historical.get(cat, 0) + s["total_spent"]
            count[cat] = count.get(cat, 0) + 1

    # Calculate averages and find anomalies
    anomalies = []
    for cat, amount in current_by_cat.items():
        if cat in historical and count[cat] > 0:
            avg = historical[cat] / count[cat]
            if avg > 0 and amount > avg * threshold:
                anomalies.append({
                    "category": cat,
                    "current_amount": amount,
                    "average_amount": avg,
                    "deviation": (amount - avg) / avg * 100,
                    "threshold_exceeded": amount / avg
                })

    return sorted(anomalies, key=lambda x: x["deviation"], reverse=True)


def get_top_spending_categories(month: str = None, limit: int = 5) -> list[dict]:
    """
    Get top spending categories for a month.

    Args:
        month: Month in YYYY-MM format (defaults to current)
        limit: Number of categories to return

    Returns:
        List of top categories with amounts and percentages
    """
    if month is None:
        month = datetime.now().strftime("%Y-%m")

    spending = get_spending_by_category(month)
    total = sum(s["total_spent"] for s in spending)

    top_cats = sorted(spending, key=lambda x: x["total_spent"], reverse=True)[:limit]

    return [
        {
            "category_name": s["category_name"],
            "category_icon": s["category_icon"],
            "amount": s["total_spent"],
            "percentage": (s["total_spent"] / total * 100) if total > 0 else 0,
            "transaction_count": s["transaction_count"]
        }
        for s in top_cats
    ]


# ============================================================================
# Financial Health Score
# ============================================================================

def calculate_financial_health_score() -> dict:
    """
    Calculate an overall financial health score (0-100).

    Components:
    - Savings Rate (25 points): 20%+ = 25, 10% = 15, 0% = 0
    - DTI Ratio (25 points): <20% = 25, <36% = 15, >50% = 0
    - Emergency Fund (25 points): 6+ months = 25, 3 months = 15, 0 = 0
    - Net Worth Trend (25 points): Positive trend = 25, Flat = 10, Negative = 0

    Returns:
        dict with total score, component scores, and grade
    """
    month = datetime.now().strftime("%Y-%m")
    snapshot = get_financial_snapshot(month)

    # Savings Rate Score (0-25)
    savings_rate = snapshot.get("savings_rate") or 0
    if savings_rate >= 20:
        savings_score = 25
    elif savings_rate >= 10:
        savings_score = 15 + (savings_rate - 10) * 1  # 15-25 range
    elif savings_rate > 0:
        savings_score = savings_rate * 1.5  # 0-15 range
    else:
        savings_score = 0

    # DTI Ratio Score (0-25)
    dti = snapshot.get("dti_ratio") or 0
    if dti <= 20:
        dti_score = 25
    elif dti <= 36:
        dti_score = 25 - (dti - 20) * 0.625  # Linear decrease
    elif dti <= 50:
        dti_score = 15 - (dti - 36) * 1.07
    else:
        dti_score = 0

    # Emergency Fund Score (0-25)
    emergency_months = snapshot.get("emergency_fund_months") or 0
    if emergency_months >= 6:
        emergency_score = 25
    elif emergency_months >= 3:
        emergency_score = 15 + (emergency_months - 3) * 3.33
    elif emergency_months > 0:
        emergency_score = emergency_months * 5
    else:
        emergency_score = 0

    # Net Worth Trend Score (0-25)
    kpi_history = get_kpi_history(3)
    if len(kpi_history) >= 2:
        net_worths = [k["net_worth"] or 0 for k in kpi_history]
        trend = net_worths[0] - net_worths[-1]  # Most recent - oldest
        if trend > 0:
            trend_score = min(25, 15 + (trend / 1000))  # Bonus for improvement
        elif trend == 0:
            trend_score = 10
        else:
            trend_score = max(0, 10 + (trend / 500))  # Penalty for decline
    else:
        trend_score = 10  # Neutral if no history

    # Calculate total and grade
    total_score = savings_score + dti_score + emergency_score + trend_score
    total_score = max(0, min(100, total_score))  # Clamp to 0-100

    if total_score >= 80:
        grade = "A"
        description = "Eccellente salute finanziaria"
    elif total_score >= 65:
        grade = "B"
        description = "Buona gestione finanziaria"
    elif total_score >= 50:
        grade = "C"
        description = "Situazione stabile, margini di miglioramento"
    elif total_score >= 35:
        grade = "D"
        description = "Attenzione richiesta su alcuni aspetti"
    else:
        grade = "F"
        description = "Situazione critica, intervento necessario"

    return {
        "total_score": round(total_score, 1),
        "grade": grade,
        "description": description,
        "components": {
            "savings_rate": {
                "score": round(savings_score, 1),
                "max": 25,
                "value": savings_rate,
                "target": 20
            },
            "dti_ratio": {
                "score": round(dti_score, 1),
                "max": 25,
                "value": dti,
                "target": 36
            },
            "emergency_fund": {
                "score": round(emergency_score, 1),
                "max": 25,
                "value": emergency_months,
                "target": 6
            },
            "net_worth_trend": {
                "score": round(trend_score, 1),
                "max": 25
            }
        }
    }


# ============================================================================
# Budget Recommendations
# ============================================================================

def generate_budget_recommendation() -> dict:
    """
    Generate personalized budget recommendation based on 50/30/20 rule
    adapted to user's situation.

    Returns:
        dict with recommended budget allocation
    """
    # Get average income from last 3 months
    today = datetime.now()
    total_income = 0
    months_counted = 0

    for i in range(3):
        month_date = today - timedelta(days=30 * i)
        month_str = month_date.strftime("%Y-%m")
        summary = get_monthly_summary(month_str)
        if summary["total_income"] > 0:
            total_income += summary["total_income"]
            months_counted += 1

    if months_counted == 0:
        return {"error": "Insufficient income data"}

    avg_income = total_income / months_counted

    # Get debt payments
    debts = get_debts(active_only=True)
    monthly_debt_payments = sum(d.get("monthly_payment", 0) or 0 for d in debts)

    # Calculate 50/30/20 allocation
    # If in debt payoff phase, adjust to 50/20/30 (30% to debt + savings)
    total_debt = get_total_debt()

    if total_debt > 0:
        # Debt payoff phase: prioritize debt elimination
        needs_percent = 50
        wants_percent = 20
        savings_debt_percent = 30

        return {
            "monthly_income": avg_income,
            "phase": "debt_payoff",
            "allocation": {
                "needs": {
                    "percent": needs_percent,
                    "amount": avg_income * needs_percent / 100,
                    "description": "Necessità (affitto, utenze, spesa, trasporti)"
                },
                "wants": {
                    "percent": wants_percent,
                    "amount": avg_income * wants_percent / 100,
                    "description": "Desideri (ristoranti, intrattenimento, shopping)"
                },
                "savings_debt": {
                    "percent": savings_debt_percent,
                    "amount": avg_income * savings_debt_percent / 100,
                    "description": "Risparmio + Extra Debiti",
                    "breakdown": {
                        "minimum_debt_payments": monthly_debt_payments,
                        "extra_debt_payment": max(0, (avg_income * savings_debt_percent / 100) - monthly_debt_payments)
                    }
                }
            },
            "recommendation": f"Con €{total_debt:,.0f} di debiti, concentrati sul ripagamento. Destina {savings_debt_percent}% del reddito a debiti e risparmio."
        }
    else:
        # Wealth building phase: standard 50/30/20
        return {
            "monthly_income": avg_income,
            "phase": "wealth_building",
            "allocation": {
                "needs": {
                    "percent": 50,
                    "amount": avg_income * 0.50,
                    "description": "Necessità (affitto, utenze, spesa, trasporti)"
                },
                "wants": {
                    "percent": 30,
                    "amount": avg_income * 0.30,
                    "description": "Desideri (ristoranti, intrattenimento, shopping)"
                },
                "savings": {
                    "percent": 20,
                    "amount": avg_income * 0.20,
                    "description": "Risparmio e Investimenti"
                }
            },
            "recommendation": "Senza debiti, segui la regola 50/30/20 per bilanciare presente e futuro."
        }
