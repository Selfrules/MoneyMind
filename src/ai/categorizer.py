"""
AI-powered transaction categorizer using Claude API.
"""

import json
import os
import time
from typing import List

import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Available categories
CATEGORIES = [
    "Stipendio",
    "Affitto",
    "Utenze",
    "Spesa",
    "Ristoranti",
    "Trasporti",
    "Salute",
    "Palestra",
    "Abbonamenti",
    "Shopping",
    "Psicologo",
    "Gatti",
    "Viaggi",
    "Caffè",
    "Barbiere",
    "Trasferimenti",
    "Altro",
]

# Model configuration
MODEL = "claude-3-5-haiku-20241022"

# Retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF = 1  # seconds


def _build_prompt(transactions: List[dict]) -> str:
    """Build the categorization prompt for a batch of transactions."""
    transactions_list = "\n".join(
        f"- ID: {t['id']}, Descrizione: {t['description']}, "
        f"Importo: {t['amount']}, Data: {t['date']}, Tipo: {t['type']}"
        for t in transactions
    )

    categories_str = ", ".join(CATEGORIES)

    return f"""Sei un assistente finanziario. Categorizza queste transazioni.

Transazioni:
{transactions_list}

Categorie disponibili: {categories_str}

Contesto: L'utente è un PM che vive a Reggio Emilia, va in palestra al 21 Lab, ha gatti.

Rispondi in formato JSON:
{{"results": [{{"id": "hash1", "category": "NomeCategoria"}}, ...]}}"""


def _call_claude_with_retry(client: anthropic.Anthropic, prompt: str) -> dict:
    """Call Claude API with exponential backoff retry logic."""
    backoff = INITIAL_BACKOFF

    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract text content from response
            content = response.content[0].text

            # Parse JSON from response
            # Handle potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content.strip())

        except anthropic.RateLimitError:
            if attempt < MAX_RETRIES - 1:
                time.sleep(backoff)
                backoff *= 2
            else:
                raise

        except anthropic.APIError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(backoff)
                backoff *= 2
            else:
                raise

        except json.JSONDecodeError:
            if attempt < MAX_RETRIES - 1:
                time.sleep(backoff)
                backoff *= 2
            else:
                raise


def categorize_transactions(
    transactions: List[dict],
    batch_size: int = 10
) -> dict:
    """
    Categorize a list of transactions using Claude AI.

    Args:
        transactions: List of transaction dicts with keys:
            - id: unique identifier (hash)
            - description: transaction description
            - amount: transaction amount
            - date: transaction date
            - type: transaction type (entrata/uscita)
        batch_size: Number of transactions to process per API call

    Returns:
        Dictionary mapping transaction_id to category_name
    """
    if not transactions:
        return {}

    # Initialize client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

    client = anthropic.Anthropic(api_key=api_key)

    # Results dictionary
    results = {}

    # Process in batches
    for i in range(0, len(transactions), batch_size):
        batch = transactions[i:i + batch_size]

        try:
            prompt = _build_prompt(batch)
            response = _call_claude_with_retry(client, prompt)

            # Extract results from response
            for item in response.get("results", []):
                transaction_id = item.get("id")
                category = item.get("category")

                # Validate category
                if category in CATEGORIES:
                    results[transaction_id] = category
                else:
                    results[transaction_id] = "Altro"

        except Exception:
            # On error, default all transactions in batch to "Altro"
            for t in batch:
                results[t["id"]] = "Altro"

    return results
