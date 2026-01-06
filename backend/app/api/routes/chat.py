"""Chat API routes with SSE streaming support."""
import sys
from pathlib import Path
import uuid
import json
from typing import AsyncGenerator

# Add project root to path for src imports
ROUTES_DIR = Path(__file__).parent
API_DIR = ROUTES_DIR.parent
APP_DIR = API_DIR.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_DIR = BACKEND_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional

from app.schemas.chat import (
    ChatMessage,
    ChatHistoryResponse,
    ChatRequest,
    SuggestedQuestion,
    SuggestedQuestionsResponse,
)
from app.api.deps import get_db
from src.database import (
    get_chat_history,
    add_chat_message,
    delete_chat_session,
    get_user_profile,
    get_debts,
    get_goals,
)
from src.analytics import get_financial_snapshot, calculate_financial_health_score

import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Model configuration
MODEL_ID = "claude-opus-4-5-20251101"

FINANCIAL_ADVISOR_SYSTEM = """Sei un consulente finanziario personale esperto e amichevole per MoneyMind.

## Il Tuo Ruolo
- Sei l'amico esperto che tutti vorrebbero avere per le finanze
- Parli in italiano con tono caldo ma professionale
- Usi metafore semplici per spiegare concetti complessi
- Celebri i piccoli successi dell'utente
- Ogni risposta termina con UN'AZIONE CONCRETA che l'utente può fare subito

## Linee Guida
1. **Sii Pratico**: Suggerimenti specifici, non generici
2. **Sii Incoraggiante**: Ogni passo avanti è un successo
3. **Sii Onesto**: Se qualcosa non va, dillo con gentilezza
4. **Sii Concreto**: Numeri, date, azioni specifiche
5. **Sii Breve**: Risposte concise e actionable (max 300 parole)

## Formato Risposta
- Usa emoji con moderazione per rendere il testo più leggibile
- Struttura con bullet points quando appropriato
- Termina SEMPRE con "**Prossimo passo:**" e un'azione concreta"""


def get_client() -> anthropic.Anthropic:
    """Get Anthropic client with API key."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")
    return anthropic.Anthropic(api_key=api_key)


def build_financial_context() -> str:
    """Build financial context string for the AI."""
    from datetime import datetime

    month = datetime.now().strftime("%Y-%m")

    # Get financial health score and snapshot
    try:
        kpis = calculate_financial_health_score()
        snapshot = get_financial_snapshot(month)
        kpis.update(snapshot)
    except Exception:
        kpis = {}

    # Get profile
    profile = get_user_profile() or {}

    # Get debts
    debts = get_debts(active_only=True)

    # Get goals
    goals = get_goals(status="active")

    context = f"""
## Situazione Finanziaria Attuale

### Patrimonio
- Net Worth: €{kpis.get('net_worth', 0):,.0f}
- Debiti Totali: €{kpis.get('total_debt', 0):,.0f}

### KPI
- Savings Rate: {kpis.get('savings_rate', 0):.1f}%
- DTI Ratio: {kpis.get('dti_ratio', 0):.1f}%
- Fondo Emergenza: {kpis.get('emergency_fund_months', 0):.1f} mesi

### Debiti Attivi
"""
    for debt in debts[:5]:  # Limit to 5
        context += f"- {debt['name']}: €{debt['current_balance']:,.0f}"
        if debt.get('interest_rate'):
            context += f" ({debt['interest_rate']}% APR)"
        context += "\n"

    context += "\n### Obiettivi\n"
    for goal in goals[:3]:  # Limit to 3
        target = goal.get('target_amount', 1)
        current = goal.get('current_amount', 0)
        progress = (current / target * 100) if target > 0 else 0
        context += f"- {goal['name']}: €{current:,.0f}/€{target:,.0f} ({progress:.0f}%)\n"

    return context


@router.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history_endpoint(
    session_id: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    db=Depends(get_db)
):
    """Get chat history for a session."""
    if not session_id:
        session_id = "default"

    history = get_chat_history(session_id, limit)

    messages = []
    total_tokens = 0

    for msg in history:
        messages.append(ChatMessage(
            id=msg.get("id"),
            role=msg["role"],
            content=msg["content"],
            tokens_used=msg.get("tokens_used"),
            created_at=msg.get("created_at")
        ))
        total_tokens += msg.get("tokens_used", 0)

    return ChatHistoryResponse(
        session_id=session_id,
        messages=messages,
        total_tokens=total_tokens
    )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    db=Depends(get_db)
):
    """Stream chat response using SSE."""
    session_id = request.session_id or str(uuid.uuid4())

    # Save user message
    add_chat_message(session_id, "user", request.message, 0)

    # Get conversation history
    history = get_chat_history(session_id, 10)

    # Build messages for API
    messages = []
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Add context to last user message
    context = build_financial_context()
    if messages and messages[-1]["role"] == "user":
        messages[-1]["content"] = f"{context}\n\n---\n\n**Domanda:**\n{messages[-1]['content']}"

    async def generate() -> AsyncGenerator[str, None]:
        """Generate SSE events."""
        client = get_client()
        full_response = ""

        try:
            # Send session_id first
            yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"

            # Stream response
            with client.messages.stream(
                model=MODEL_ID,
                max_tokens=1024,
                system=FINANCIAL_ADVISOR_SYSTEM,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    yield f"data: {json.dumps({'type': 'text', 'content': text})}\n\n"

            # Save assistant response
            add_chat_message(session_id, "assistant", full_response, 0)

            # Send completion
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.delete("/chat/session")
async def clear_session(
    session_id: Optional[str] = Query(None),
    db=Depends(get_db)
):
    """Clear chat session and start fresh."""
    if not session_id:
        session_id = "default"

    success = delete_chat_session(session_id)
    return {"success": success, "session_id": session_id}


@router.get("/chat/suggestions", response_model=SuggestedQuestionsResponse)
async def get_suggested_questions(db=Depends(get_db)):
    """Get suggested questions based on user's financial situation."""
    questions = [
        SuggestedQuestion(
            text="Come posso accelerare il pagamento dei miei debiti?",
            category="debt"
        ),
        SuggestedQuestion(
            text="Qual è la mia situazione finanziaria attuale?",
            category="general"
        ),
        SuggestedQuestion(
            text="Come posso risparmiare di più questo mese?",
            category="savings"
        ),
        SuggestedQuestion(
            text="Dovrei concentrarmi sui debiti o sul fondo emergenza?",
            category="budget"
        ),
        SuggestedQuestion(
            text="Quali spese posso tagliare facilmente?",
            category="spending"
        ),
    ]

    return SuggestedQuestionsResponse(questions=questions)
