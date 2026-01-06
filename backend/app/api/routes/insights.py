"""
Insights API endpoints.
"""
import sys
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
import sqlite3

# Add src directory to path
BACKEND_DIR = Path(__file__).parent.parent.parent.parent
PROJECT_DIR = BACKEND_DIR.parent
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from app.api.deps import get_db
from app.schemas.insights import (
    Insight,
    InsightsResponse,
    InsightSeverity,
)

# Import existing database functions
from database import (
    get_insights,
    get_unread_insight_count,
    mark_insight_read,
    dismiss_insight,
    get_category_by_name,
)

router = APIRouter()


@router.get("/insights", response_model=InsightsResponse)
async def list_insights(
    unread_only: bool = False,
    limit: int = 20,
    db: sqlite3.Connection = Depends(get_db),
):
    """
    Get list of active insights.
    """
    try:
        raw_insights = get_insights(unread_only=unread_only, limit=limit)

        insights = []
        for i in raw_insights:
            # Get category info if present
            category_name = None
            category_icon = None
            if i.get("category"):
                cat = get_category_by_name(i["category"])
                if cat:
                    category_name = cat["name"]
                    category_icon = cat.get("icon")

            # Parse severity
            try:
                severity = InsightSeverity(i.get("severity", "low"))
            except ValueError:
                severity = InsightSeverity.LOW

            insights.append(
                Insight(
                    id=i["id"],
                    type=i.get("type") or "general",
                    category=i.get("category"),
                    severity=severity,
                    title=i.get("title") or "Insight",
                    message=i.get("message") or "",
                    action_text=i.get("action_text"),
                    is_read=bool(i.get("is_read")),
                    is_dismissed=bool(i.get("is_dismissed")),
                    created_at=datetime.fromisoformat(i["created_at"]) if i.get("created_at") else datetime.now(),
                    category_name=category_name,
                    category_icon=category_icon,
                )
            )

        unread_count = get_unread_insight_count()

        return InsightsResponse(
            insights=insights,
            unread_count=unread_count,
            total_count=len(insights),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading insights: {str(e)}")


@router.post("/insights/{insight_id}/read")
async def mark_as_read(
    insight_id: int,
    db: sqlite3.Connection = Depends(get_db),
):
    """
    Mark an insight as read.
    """
    try:
        success = mark_insight_read(insight_id)
        if not success:
            raise HTTPException(status_code=404, detail="Insight not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking insight: {str(e)}")


@router.post("/insights/{insight_id}/dismiss")
async def dismiss_insight_endpoint(
    insight_id: int,
    db: sqlite3.Connection = Depends(get_db),
):
    """
    Dismiss an insight permanently.
    """
    try:
        success = dismiss_insight(insight_id)
        if not success:
            raise HTTPException(status_code=404, detail="Insight not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dismissing insight: {str(e)}")
