"""
Full Financial Report API endpoints.
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
import sqlite3

# Add src directory to path (avoid PROJECT_DIR to prevent app.py conflict)
BACKEND_DIR = Path(__file__).parent.parent.parent.parent
PROJECT_DIR = BACKEND_DIR.parent
SRC_DIR = PROJECT_DIR / "src"
# Only add SRC_DIR - NOT PROJECT_DIR (Streamlit app.py conflicts with backend/app/)
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app.api.deps import get_db
from app.schemas.report import FullFinancialReport

# Import report analyzer
from core_finance.report_analyzer import ReportAnalyzer

router = APIRouter()


@router.get("/report/full", response_model=FullFinancialReport)
async def get_full_report(
    month: Optional[str] = Query(None, description="Month in YYYY-MM format"),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Get complete financial report including:
    - Executive summary with health score
    - Category spending analysis with judgments
    - Subscription audit with action recommendations
    - Debt priority matrix
    - Recommendations
    - Month-over-month comparison
    """
    try:
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        analyzer = ReportAnalyzer()
        report = analyzer.generate_full_report(month)

        return analyzer.to_dict(report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
