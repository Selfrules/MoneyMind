"""AI-powered deep financial analysis API routes."""
import sys
from pathlib import Path
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
import json
import os

# Add project root to path
ROUTES_DIR = Path(__file__).parent
API_DIR = ROUTES_DIR.parent
APP_DIR = API_DIR.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_DIR = BACKEND_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_db
from src.database import get_transactions, get_recurring_expenses, get_user_profile

# Try to import anthropic
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================

class RecurringInsight(BaseModel):
    """Insight about a recurring expense."""
    name: str
    category: str
    monthly_amount: float
    type: str  # 'subscription', 'service', 'financing', 'essential'
    recommendation: str  # 'keep', 'review', 'cancel', 'negotiate'
    reason: str
    potential_savings: Optional[float] = None


class AnomalyDetail(BaseModel):
    """Detected anomaly in transactions."""
    description: str
    date: str
    amount: float
    anomaly_type: str  # 'unusual_amount', 'duplicate', 'unexpected_category', 'timing'
    explanation: str


class SavingsOpportunity(BaseModel):
    """Identified savings opportunity."""
    area: str
    current_spending: float
    suggested_target: float
    potential_savings: float
    action: str


class DeepAnalysisResponse(BaseModel):
    """Complete deep analysis response."""
    summary: str
    financial_health_score: int  # 0-100
    monthly_overview: Dict[str, float]
    recurring_insights: List[RecurringInsight]
    anomalies: List[AnomalyDetail]
    savings_opportunities: List[SavingsOpportunity]
    categorization_issues: List[Dict[str, Any]]
    recommendations: List[str]


# ============================================================================
# Analysis Prompts
# ============================================================================

DEEP_ANALYSIS_PROMPT = """Sei un consulente finanziario esperto che analizza le transazioni di Mattia.

CONTESTO:
- Mattia vuole raggiungere la libertà finanziaria
- Ha debiti attivi (finanziamenti) da estinguere
- Obiettivo: aumentare il risparmio mensile e ridurre il tempo di estinzione debiti

TRANSAZIONI ULTIMI 3 MESI (formato JSON):
{transactions_json}

SPESE RICORRENTI ATTUALI:
{recurring_json}

PROFILO:
- Reddito mensile netto: €{monthly_income}
- Debiti totali: €{total_debt}

ANALIZZA E RISPONDI IN JSON con questa struttura esatta:
{{
    "summary": "Breve riassunto della situazione finanziaria in 2-3 frasi",
    "financial_health_score": <numero 0-100>,
    "monthly_overview": {{
        "income": <totale entrate>,
        "fixed_expenses": <spese fisse>,
        "discretionary_expenses": <spese discrezionali>,
        "savings": <risparmio>,
        "debt_payments": <rate debiti>
    }},
    "recurring_insights": [
        {{
            "name": "Nome servizio",
            "category": "Categoria",
            "monthly_amount": <importo>,
            "type": "subscription|service|financing|essential",
            "recommendation": "keep|review|cancel|negotiate",
            "reason": "Spiegazione breve",
            "potential_savings": <risparmio potenziale o null>
        }}
    ],
    "anomalies": [
        {{
            "description": "Descrizione transazione",
            "date": "YYYY-MM-DD",
            "amount": <importo>,
            "anomaly_type": "unusual_amount|duplicate|unexpected_category|timing",
            "explanation": "Perché è anomala"
        }}
    ],
    "savings_opportunities": [
        {{
            "area": "Area di spesa",
            "current_spending": <spesa attuale>,
            "suggested_target": <obiettivo>,
            "potential_savings": <risparmio>,
            "action": "Azione concreta"
        }}
    ],
    "categorization_issues": [
        {{
            "transaction_desc": "Descrizione",
            "current_category": "Categoria attuale",
            "suggested_category": "Categoria corretta",
            "reason": "Motivo"
        }}
    ],
    "recommendations": [
        "Raccomandazione 1 (azione concreta)",
        "Raccomandazione 2 (azione concreta)",
        "Raccomandazione 3 (azione concreta)"
    ]
}}

REGOLE IMPORTANTI:
1. Unobravo = psicologa settimanale, NON è un abbonamento cancellabile
2. Steam = acquisti giochi one-time, NON abbonamento
3. Considera INATTIVE le subscription senza pagamenti negli ultimi 60 giorni
4. Focus su azioni concrete per aumentare risparmio e ridurre debiti
5. Sii specifico con i numeri e le raccomandazioni
"""


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/deep-analysis", response_model=DeepAnalysisResponse)
async def get_deep_analysis():
    """
    Perform AI-powered deep analysis of financial situation.

    Uses Claude to analyze:
    - Transaction patterns and anomalies
    - Recurring expense optimization
    - Savings opportunities
    - Categorization accuracy
    """
    if not ANTHROPIC_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Anthropic library not available. Install with: pip install anthropic"
        )

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY not configured"
        )

    # Gather data
    three_months_ago = (date.today() - timedelta(days=90)).strftime("%Y-%m-%d")
    transactions = get_transactions({"start_date": three_months_ago})
    recurring = get_recurring_expenses(active_only=True)
    profile = get_user_profile() or {}

    monthly_income = profile.get("monthly_net_income", 3000)
    total_debt = profile.get("total_debt", 0)

    # Prepare data for AI
    # Limit transactions to avoid token limits
    tx_sample = transactions[:200] if len(transactions) > 200 else transactions
    tx_json = json.dumps([
        {
            "date": t["date"],
            "description": t["description"][:100],
            "amount": t["amount"],
            "category": t.get("category_name", "Altro")
        }
        for t in tx_sample
    ], ensure_ascii=False, indent=2)

    recurring_json = json.dumps([
        {
            "name": r["pattern_name"],
            "amount": r["avg_amount"],
            "frequency": r["frequency"],
            "category": r.get("category_name", ""),
            "last_occurrence": r.get("last_occurrence", "")
        }
        for r in recurring
    ], ensure_ascii=False, indent=2)

    # Build prompt
    prompt = DEEP_ANALYSIS_PROMPT.format(
        transactions_json=tx_json,
        recurring_json=recurring_json,
        monthly_income=monthly_income,
        total_debt=total_debt
    )

    # Call Claude
    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        response_text = response.content[0].text

        # Extract JSON from response
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            analysis = json.loads(json_str)
        else:
            raise ValueError("No valid JSON in response")

        # Build response
        return DeepAnalysisResponse(
            summary=analysis.get("summary", "Analisi non disponibile"),
            financial_health_score=analysis.get("financial_health_score", 50),
            monthly_overview=analysis.get("monthly_overview", {}),
            recurring_insights=[
                RecurringInsight(**r) for r in analysis.get("recurring_insights", [])
            ],
            anomalies=[
                AnomalyDetail(**a) for a in analysis.get("anomalies", [])
            ],
            savings_opportunities=[
                SavingsOpportunity(**s) for s in analysis.get("savings_opportunities", [])
            ],
            categorization_issues=analysis.get("categorization_issues", []),
            recommendations=analysis.get("recommendations", [])
        )

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse AI response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {str(e)}"
        )


@router.get("/quick-insights")
async def get_quick_insights():
    """
    Get quick financial insights without AI (faster, no API call).

    Returns rule-based insights about spending patterns.
    """
    three_months_ago = (date.today() - timedelta(days=90)).strftime("%Y-%m-%d")
    transactions = get_transactions({"start_date": three_months_ago})
    recurring = get_recurring_expenses(active_only=True)
    profile = get_user_profile() or {}

    monthly_income = profile.get("monthly_net_income", 3000)

    # Calculate spending by category
    category_spending = {}
    for tx in transactions:
        if tx["amount"] < 0:  # Expenses only
            cat = tx.get("category_name", "Altro")
            category_spending[cat] = category_spending.get(cat, 0) + abs(tx["amount"])

    # Identify top spending categories
    sorted_cats = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
    top_5_categories = sorted_cats[:5]

    # Calculate monthly averages (3 months)
    total_income = sum(tx["amount"] for tx in transactions if tx["amount"] > 0)
    total_expenses = sum(abs(tx["amount"]) for tx in transactions if tx["amount"] < 0)

    avg_monthly_income = total_income / 3
    avg_monthly_expenses = total_expenses / 3
    savings_rate = ((avg_monthly_income - avg_monthly_expenses) / avg_monthly_income * 100) if avg_monthly_income > 0 else 0

    # Count active recurring
    active_recurring_count = len([
        r for r in recurring
        if r.get("last_occurrence") and
        (date.today() - date.fromisoformat(r["last_occurrence"])).days <= 60
    ])

    # Total recurring monthly
    total_recurring_monthly = sum(
        r["avg_amount"] / (3 if r["frequency"] == "quarterly" else 12 if r["frequency"] == "annual" else 1)
        for r in recurring
    )

    insights = []

    # Savings insight
    if savings_rate > 30:
        insights.append({
            "type": "positive",
            "title": "Ottimo tasso di risparmio",
            "message": f"Stai risparmiando il {savings_rate:.1f}% del reddito. Eccellente!"
        })
    elif savings_rate > 15:
        insights.append({
            "type": "neutral",
            "title": "Tasso di risparmio nella media",
            "message": f"Risparmi il {savings_rate:.1f}%. Obiettivo: raggiungere il 30%."
        })
    else:
        insights.append({
            "type": "warning",
            "title": "Tasso di risparmio basso",
            "message": f"Solo {savings_rate:.1f}% di risparmio. Riduci le spese discrezionali."
        })

    # Recurring expenses insight
    recurring_percent = (total_recurring_monthly / avg_monthly_income * 100) if avg_monthly_income > 0 else 0
    if recurring_percent > 50:
        insights.append({
            "type": "warning",
            "title": "Spese ricorrenti elevate",
            "message": f"Le spese fisse sono il {recurring_percent:.0f}% del reddito. Valuta ottimizzazioni."
        })

    # Top spending category insight
    if top_5_categories:
        top_cat, top_amount = top_5_categories[0]
        top_monthly = top_amount / 3
        top_percent = (top_monthly / avg_monthly_income * 100) if avg_monthly_income > 0 else 0
        insights.append({
            "type": "info",
            "title": f"Categoria principale: {top_cat}",
            "message": f"€{top_monthly:.0f}/mese ({top_percent:.0f}% del reddito)"
        })

    return {
        "monthly_summary": {
            "avg_income": round(avg_monthly_income, 2),
            "avg_expenses": round(avg_monthly_expenses, 2),
            "avg_savings": round(avg_monthly_income - avg_monthly_expenses, 2),
            "savings_rate": round(savings_rate, 1)
        },
        "top_categories": [
            {"category": cat, "total": round(amount, 2), "monthly_avg": round(amount/3, 2)}
            for cat, amount in top_5_categories
        ],
        "recurring_summary": {
            "active_count": active_recurring_count,
            "total_monthly": round(total_recurring_monthly, 2),
            "percent_of_income": round(recurring_percent, 1)
        },
        "insights": insights
    }
