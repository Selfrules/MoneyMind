"""AI Reporter module for generating monthly financial reports using Claude."""

import json
import os
from typing import List

from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Monthly report prompt template
MONTHLY_REPORT_PROMPT = """Sei un financial advisor personale. Analizza le transazioni di questo mese e genera un report.

Contesto utente:
- PM in una azienda tech
- Vive a Reggio Emilia
- Va in palestra (21 Lab)
- Obiettivo: risparmiare e ottimizzare le spese

Transazioni del mese:
{transactions_json}

Budget impostati:
{budgets_json}

Spese per categoria:
{spending_by_category}

Genera un report con:
1. Riepilogo (entrate, uscite, risparmio)
2. Analisi per categoria (cosa è andato bene/male rispetto al budget)
3. Anomalie (spese insolite o picchi)
4. 3 suggerimenti concreti per risparmiare il mese prossimo
5. Un obiettivo specifico per il mese prossimo

Tono: diretto, pratico, senza giri di parole. Come un amico che ti dice le cose come stanno."""


def generate_monthly_report(
    transactions: List[dict],
    budgets: List[dict],
    spending_by_category: dict
) -> str:
    """
    Generate a monthly financial report using Claude AI.

    Args:
        transactions: List of transaction dictionaries for the month.
        budgets: List of budget dictionaries with category limits.
        spending_by_category: Dictionary mapping categories to total spending.

    Returns:
        Markdown-formatted report string, or error message if API call fails.
    """
    try:
        # Get API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return "**Errore**: ANTHROPIC_API_KEY non trovata. Configura la variabile d'ambiente nel file .env"

        # Initialize Anthropic client
        client = Anthropic(api_key=api_key)

        # Format data as JSON strings for the prompt
        transactions_json = json.dumps(transactions, indent=2, ensure_ascii=False, default=str)
        budgets_json = json.dumps(budgets, indent=2, ensure_ascii=False, default=str)
        spending_json = json.dumps(spending_by_category, indent=2, ensure_ascii=False, default=str)

        # Build the prompt with actual data
        prompt = MONTHLY_REPORT_PROMPT.format(
            transactions_json=transactions_json,
            budgets_json=budgets_json,
            spending_by_category=spending_json
        )

        # Call Claude API
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Extract and return the report text
        return message.content[0].text

    except Exception as e:
        # Handle errors gracefully
        error_type = type(e).__name__
        return f"**Errore durante la generazione del report**: {error_type} - {str(e)}"
