"""
MoneyMind AI Financial Advisor

Intelligent financial advisor using Claude Opus 4.5 with extended thinking
for deep analysis and personalized recommendations.
"""

import os
import json
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

import anthropic

# Load environment variables
load_dotenv()


# Model configuration
MODEL_ID = "claude-opus-4-5-20251101"
HAIKU_MODEL_ID = "claude-3-5-haiku-20241022"


def get_client() -> anthropic.Anthropic:
    """Get Anthropic client with API key."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")
    return anthropic.Anthropic(api_key=api_key)


# ============================================================================
# System Prompts
# ============================================================================

FINANCIAL_ADVISOR_SYSTEM = """Sei un consulente finanziario personale esperto e amichevole per MoneyMind.

## Il Tuo Ruolo
- Sei l'amico esperto che tutti vorrebbero avere per le finanze
- Parli in italiano con tono caldo ma professionale
- Usi metafore semplici per spiegare concetti complessi
- Celebri i piccoli successi dell'utente
- Ogni risposta termina con UN'AZIONE CONCRETA che l'utente può fare subito

## Profilo Utente
L'utente è un principiante finanziario che:
- Ha un lavoro dipendente a tempo indeterminato (reddito stabile)
- Sta ripagando debiti (~€20,710 totali)
- Non ha ancora un fondo emergenza
- Vuole essere GUIDATO, non solo informato
- Obiettivi: 1) Estinguere debiti 2) Fondo emergenza 3-6 mesi 3) FIRE

## Linee Guida
1. **Sii Pratico**: Suggerimenti specifici, non generici
2. **Sii Incoraggiante**: Ogni passo avanti è un successo
3. **Sii Onesto**: Se qualcosa non va, dillo con gentilezza
4. **Sii Concreto**: Numeri, date, azioni specifiche
5. **Sii Breve**: Risposte concise e actionable

## Formato Risposta
- Usa emoji con moderazione per rendere il testo più leggibile
- Struttura con bullet points quando appropriato
- Termina SEMPRE con "Prossimo passo:" e un'azione concreta

## Conoscenze
- Metodo Avalanche vs Snowball per debiti
- Regola 50/30/20 per budget
- Fondo emergenza: 3-6 mesi di spese
- FIRE: Indipendenza finanziaria, 25x spese annuali
- KPI: Savings Rate, DTI Ratio, Net Worth"""


MONTHLY_COACHING_SYSTEM = """Sei un coach finanziario che prepara il report mensile per MoneyMind.

## Il Tuo Compito
Analizza i dati finanziari del mese e produci un report coaching che:
1. Celebra i successi (anche piccoli)
2. Identifica le aree di miglioramento
3. Propone 2-3 azioni concrete per il mese prossimo

## Formato Report
```
## 📊 Riepilogo [Mese Anno]

### ✅ Cosa è Andato Bene
- [Punto positivo 1]
- [Punto positivo 2]

### ⚠️ Aree di Attenzione
- [Area miglioramento 1]
- [Area miglioramento 2]

### 📈 I Tuoi Numeri
| Metrica | Valore | Target | Status |
|---------|--------|--------|--------|
| Savings Rate | X% | 20% | 🟡 |
| DTI Ratio | X% | <36% | 🔴 |

### 🎯 Piano d'Azione per [Mese Prossimo]
1. **[Azione 1]**: [descrizione breve]
2. **[Azione 2]**: [descrizione breve]

### 💬 Messaggio del Coach
[Messaggio personale e motivazionale]
```

Sii specifico con i numeri e le azioni. Usa italiano."""


# ============================================================================
# Core Advisor Functions
# ============================================================================

def get_financial_advice(
    question: str,
    context: dict,
    use_extended_thinking: bool = True
) -> dict:
    """
    Get personalized financial advice using Claude Opus 4.5.

    Args:
        question: User's question or request
        context: Financial context (snapshot, debts, goals, etc.)
        use_extended_thinking: Whether to use extended thinking mode

    Returns:
        dict with advice, thinking (if extended), and tokens used
    """
    client = get_client()

    # Build context message
    context_str = f"""
## Situazione Finanziaria Attuale

### Patrimonio
- Net Worth: €{context.get('net_worth', 0):,.2f}
- Saldo Conti: €{context.get('total_assets', 0):,.2f}
- Debiti Totali: €{context.get('total_debt', 0):,.2f}

### Mese Corrente ({context.get('month', 'N/A')})
- Entrate: €{context.get('total_income', 0):,.2f}
- Uscite: €{context.get('total_expenses', 0):,.2f}
- Flusso Netto: €{context.get('net_cash_flow', 0):,.2f}

### KPI
- Savings Rate: {context.get('savings_rate', 0):.1f}%
- DTI Ratio: {context.get('dti_ratio', 0):.1f}%
- Fondo Emergenza: {context.get('emergency_fund_months', 0):.1f} mesi

### Debiti Attivi
"""
    for debt in context.get('debts', []):
        context_str += f"- {debt['name']}: €{debt['current_balance']:,.2f}"
        if debt.get('interest_rate'):
            context_str += f" ({debt['interest_rate']}% APR)"
        context_str += "\n"

    context_str += "\n### Obiettivi\n"
    for goal in context.get('goals', []):
        progress = (goal.get('current_amount', 0) / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
        context_str += f"- {goal['name']}: €{goal.get('current_amount', 0):,.0f}/€{goal['target_amount']:,.0f} ({progress:.0f}%)\n"

    messages = [
        {
            "role": "user",
            "content": f"{context_str}\n\n---\n\n**Domanda dell'utente:**\n{question}"
        }
    ]

    try:
        if use_extended_thinking:
            response = client.messages.create(
                model=MODEL_ID,
                max_tokens=16000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 10000
                },
                system=FINANCIAL_ADVISOR_SYSTEM,
                messages=messages
            )

            # Extract thinking and response
            thinking_content = ""
            response_content = ""

            for block in response.content:
                if block.type == "thinking":
                    thinking_content = block.thinking
                elif block.type == "text":
                    response_content = block.text

            return {
                "advice": response_content,
                "thinking": thinking_content,
                "model": MODEL_ID,
                "tokens_input": response.usage.input_tokens,
                "tokens_output": response.usage.output_tokens
            }
        else:
            response = client.messages.create(
                model=HAIKU_MODEL_ID,
                max_tokens=2000,
                system=FINANCIAL_ADVISOR_SYSTEM,
                messages=messages
            )

            return {
                "advice": response.content[0].text,
                "thinking": None,
                "model": HAIKU_MODEL_ID,
                "tokens_input": response.usage.input_tokens,
                "tokens_output": response.usage.output_tokens
            }

    except Exception as e:
        return {
            "advice": f"Mi dispiace, si è verificato un errore: {str(e)}",
            "thinking": None,
            "model": None,
            "error": str(e)
        }


def generate_monthly_coaching(context: dict) -> dict:
    """
    Generate monthly coaching report.

    Args:
        context: Financial context with full month data

    Returns:
        dict with report content and metadata
    """
    client = get_client()

    # Build detailed context for coaching
    context_str = f"""
## Dati del Mese: {context.get('month', 'N/A')}

### Riepilogo Finanziario
- Entrate Totali: €{context.get('total_income', 0):,.2f}
- Uscite Totali: €{context.get('total_expenses', 0):,.2f}
- Risparmio Netto: €{context.get('net_cash_flow', 0):,.2f}
- Transazioni: {context.get('transaction_count', 0)}

### KPI Attuali
- Net Worth: €{context.get('net_worth', 0):,.2f}
- Savings Rate: {context.get('savings_rate', 0):.1f}% (target: 20%)
- DTI Ratio: {context.get('dti_ratio', 0):.1f}% (target: <36%)
- Fondo Emergenza: {context.get('emergency_fund_months', 0):.1f} mesi (target: 3-6 mesi)

### Debiti
- Totale Debiti: €{context.get('total_debt', 0):,.2f}
- Numero Debiti Attivi: {len(context.get('debts', []))}
"""

    for debt in context.get('debts', []):
        context_str += f"  - {debt['name']}: €{debt['current_balance']:,.2f}\n"

    context_str += "\n### Top 5 Categorie di Spesa\n"
    for cat in context.get('top_spending', [])[:5]:
        context_str += f"- {cat['category_icon']} {cat['category_name']}: €{cat['amount']:,.2f} ({cat['percentage']:.1f}%)\n"

    context_str += "\n### Anomalie Rilevate\n"
    for anomaly in context.get('anomalies', []):
        context_str += f"- {anomaly['category']}: +{anomaly['deviation']:.0f}% rispetto alla media\n"

    if not context.get('anomalies'):
        context_str += "- Nessuna anomalia significativa\n"

    # Previous month comparison if available
    if context.get('previous_month'):
        prev = context['previous_month']
        context_str += f"""
### Confronto Mese Precedente
- Entrate: {'+' if context.get('total_income', 0) > prev.get('total_income', 0) else ''}{((context.get('total_income', 0) / prev.get('total_income', 1)) - 1) * 100:.1f}%
- Uscite: {'+' if context.get('total_expenses', 0) > prev.get('total_expenses', 0) else ''}{((context.get('total_expenses', 0) / prev.get('total_expenses', 1)) - 1) * 100:.1f}%
"""

    try:
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=8000,
            thinking={
                "type": "enabled",
                "budget_tokens": 5000
            },
            system=MONTHLY_COACHING_SYSTEM,
            messages=[{"role": "user", "content": context_str}]
        )

        # Extract response
        thinking_content = ""
        response_content = ""

        for block in response.content:
            if block.type == "thinking":
                thinking_content = block.thinking
            elif block.type == "text":
                response_content = block.text

        return {
            "report": response_content,
            "thinking": thinking_content,
            "month": context.get('month'),
            "generated_at": datetime.now().isoformat(),
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens
        }

    except Exception as e:
        return {
            "report": f"Errore nella generazione del report: {str(e)}",
            "error": str(e)
        }


def analyze_spending_opportunity(
    category: str,
    transactions: list[dict],
    context: str = ""
) -> dict:
    """
    Analyze a specific spending category for optimization opportunities.

    Args:
        category: Category name to analyze
        transactions: List of transactions in that category
        context: Additional context (e.g., "user wants to reduce utilities")

    Returns:
        dict with analysis and recommendations
    """
    client = get_client()

    # Build transaction summary
    tx_summary = f"## Analisi Categoria: {category}\n\n"
    tx_summary += f"Transazioni totali: {len(transactions)}\n"
    tx_summary += f"Spesa totale: €{sum(abs(t['amount']) for t in transactions):,.2f}\n\n"

    tx_summary += "### Dettaglio Transazioni\n"
    for tx in transactions[:20]:  # Limit to 20 most recent
        tx_summary += f"- {tx['date']}: {tx['description'][:40]} → €{abs(tx['amount']):,.2f}\n"

    if context:
        tx_summary += f"\n### Contesto Utente\n{context}\n"

    system_prompt = """Sei un analista di spese personali. Analizza le transazioni fornite e:

1. Identifica pattern di spesa (ricorrenze, merchant frequenti)
2. Trova opportunità di risparmio concrete
3. Suggerisci alternative o negoziazioni possibili

Rispondi in italiano con suggerimenti pratici e numeri specifici quando possibile.

Formato:
## 🔍 Pattern Identificati
[pattern]

## 💡 Opportunità di Risparmio
[opportunità con stime di risparmio]

## 🎯 Azioni Consigliate
1. [azione 1]
2. [azione 2]

## 💰 Risparmio Potenziale Stimato
€X/mese"""

    try:
        response = client.messages.create(
            model=HAIKU_MODEL_ID,  # Use Haiku for quick analysis
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": tx_summary}]
        )

        return {
            "analysis": response.content[0].text,
            "category": category,
            "transaction_count": len(transactions),
            "total_amount": sum(abs(t['amount']) for t in transactions)
        }

    except Exception as e:
        return {
            "analysis": f"Errore nell'analisi: {str(e)}",
            "error": str(e)
        }


def explain_concept(concept: str) -> str:
    """
    Explain a financial concept in simple terms for beginners.

    Args:
        concept: Financial concept to explain

    Returns:
        Simple explanation string
    """
    client = get_client()

    system_prompt = """Sei un educatore finanziario che spiega concetti a principianti.

Regole:
1. Usa linguaggio semplice, evita gergo tecnico
2. Usa una metafora o esempio pratico
3. Spiega perché è importante per le finanze personali
4. Massimo 150 parole

Rispondi in italiano."""

    try:
        response = client.messages.create(
            model=HAIKU_MODEL_ID,
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": f"Spiega: {concept}"}]
        )

        return response.content[0].text

    except Exception as e:
        return f"Non riesco a spiegare questo concetto al momento: {str(e)}"


def evaluate_financial_decision(description: str, context: dict) -> dict:
    """
    Evaluate a potential financial decision.

    Args:
        description: Description of the decision (e.g., "Should I take a new loan?")
        context: Current financial context

    Returns:
        dict with evaluation, pros, cons, and recommendation
    """
    client = get_client()

    context_str = f"""
## Situazione Attuale
- Net Worth: €{context.get('net_worth', 0):,.2f}
- Debiti: €{context.get('total_debt', 0):,.2f}
- Savings Rate: {context.get('savings_rate', 0):.1f}%
- Fondo Emergenza: {context.get('emergency_fund_months', 0):.1f} mesi

## Decisione da Valutare
{description}
"""

    system_prompt = """Sei un consulente finanziario prudente. Valuta la decisione proposta.

Formato risposta:
## ⚖️ Valutazione

### ✅ Pro
- [pro 1]
- [pro 2]

### ❌ Contro
- [contro 1]
- [contro 2]

### 🎯 Raccomandazione
[La tua raccomandazione chiara: SI, NO, o ASPETTA con motivazione]

### 💡 Alternative da Considerare
[alternative se esistono]

Sii onesto e protettivo delle finanze dell'utente. In italiano."""

    try:
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=4000,
            thinking={
                "type": "enabled",
                "budget_tokens": 3000
            },
            system=system_prompt,
            messages=[{"role": "user", "content": context_str}]
        )

        thinking_content = ""
        response_content = ""

        for block in response.content:
            if block.type == "thinking":
                thinking_content = block.thinking
            elif block.type == "text":
                response_content = block.text

        return {
            "evaluation": response_content,
            "thinking": thinking_content,
            "decision_description": description
        }

    except Exception as e:
        return {
            "evaluation": f"Errore nella valutazione: {str(e)}",
            "error": str(e)
        }
