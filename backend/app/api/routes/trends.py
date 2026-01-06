"""Trends API routes."""
import sys
from pathlib import Path

# Add project root to path for importing src modules
ROUTES_DIR = Path(__file__).parent  # routes/
API_DIR = ROUTES_DIR.parent  # api/
APP_DIR = API_DIR.parent  # app/
BACKEND_DIR = APP_DIR.parent  # backend/
PROJECT_DIR = BACKEND_DIR.parent  # MoneyMind/
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta
from collections import defaultdict

from app.schemas.trends import (
    MonthlyTrend,
    CategoryTrend,
    TrendsResponse,
)
from app.api.deps import get_db
from src.repositories.transaction_repository import TransactionRepository


router = APIRouter()


@router.get("/trends", response_model=TrendsResponse)
async def get_spending_trends(
    months: int = Query(6, description="Number of months to analyze")
):
    """Get spending trends over the last N months."""
    repo = TransactionRepository()

    today = datetime.now()
    month_list = []
    monthly_totals = []
    category_data = defaultdict(lambda: {"amounts": [], "icon": None})

    # Collect data for each month
    for i in range(months - 1, -1, -1):
        month_date = today - timedelta(days=30 * i)
        month_str = month_date.strftime("%Y-%m")
        month_list.append(month_str)

        # Get all transactions for the month
        transactions = repo.get_for_month(month_str)

        # Calculate totals
        income = 0.0
        expenses = 0.0
        cat_spending = defaultdict(float)

        for tx in transactions:
            if tx.amount > 0:
                income += tx.amount
            else:
                expenses += abs(tx.amount)
                cat_name = tx.category_name or "Altro"
                cat_spending[cat_name] += abs(tx.amount)
                if tx.category_icon and not category_data[cat_name]["icon"]:
                    category_data[cat_name]["icon"] = tx.category_icon

        monthly_totals.append(MonthlyTrend(
            month=month_str,
            income=income,
            expenses=expenses,
            savings=income - expenses
        ))

        # Store category data
        for cat_name in category_data:
            cat_amount = cat_spending.get(cat_name, 0.0)
            category_data[cat_name]["amounts"].append(cat_amount)

    # Build top categories
    top_categories = []
    for cat_name, data in category_data.items():
        amounts = data["amounts"]
        if len(amounts) < months:
            # Pad with zeros for months with no data
            amounts = [0.0] * (months - len(amounts)) + amounts

        avg = sum(amounts) / len(amounts) if amounts else 0.0

        # Calculate trend (last 3 months vs previous 3 months)
        trend_percent = None
        if len(amounts) >= 6:
            recent = sum(amounts[-3:]) / 3
            previous = sum(amounts[-6:-3]) / 3
            if previous > 0:
                trend_percent = ((recent - previous) / previous) * 100

        if avg > 0:  # Only include categories with spending
            top_categories.append(CategoryTrend(
                category_name=cat_name,
                category_icon=data["icon"],
                monthly_data=amounts,
                average=avg,
                trend_percent=trend_percent
            ))

    # Sort by average spending
    top_categories = sorted(top_categories, key=lambda x: x.average, reverse=True)[:10]

    # Calculate overall spending trend
    avg_spending = sum(m.expenses for m in monthly_totals) / len(monthly_totals) if monthly_totals else 0.0

    spending_trend_percent = None
    if len(monthly_totals) >= 2:
        recent_avg = sum(m.expenses for m in monthly_totals[-3:]) / min(3, len(monthly_totals[-3:]))
        previous_avg = sum(m.expenses for m in monthly_totals[:-3]) / max(1, len(monthly_totals[:-3])) if len(monthly_totals) > 3 else recent_avg
        if previous_avg > 0:
            spending_trend_percent = ((recent_avg - previous_avg) / previous_avg) * 100

    return TrendsResponse(
        months=month_list,
        monthly_totals=monthly_totals,
        top_categories=top_categories,
        average_monthly_spending=avg_spending,
        spending_trend_percent=spending_trend_percent
    )
