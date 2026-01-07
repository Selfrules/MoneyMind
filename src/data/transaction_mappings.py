"""
Transaction Description Mappings

Maps cryptic transaction descriptions (SEPA codes, bank references, etc.)
to human-readable names for better categorization and display.

Based on analysis of Illimity bank statements and financing documents.
"""

import re
from typing import Optional, Tuple

# Mapping of SEPA/SDD codes and bank references to readable names
# Format: (pattern, readable_name, suggested_category)
TRANSACTION_MAPPINGS = [
    # =====================================================================
    # FINANZIAMENTI (Loans/Financing)
    # =====================================================================

    # Findomestic - Prestito Personale Flessibile
    # Reference: Acceptance number 064574737, Monthly rate €152.60
    # Pattern: 202216820433692026643530190020...
    (
        r"20221682043369\d*",
        "Rata Findomestic",
        "Finanziamenti",
        152.60
    ),

    # Agos - Prestito Personale
    # Reference: Practice number 077260688, Base rate €81.00 (+ insurance = ~€93.90)
    (
        r"PR\.\s*77260688",
        "Rata Agos",
        "Finanziamenti",
        93.90  # Includes credit protection insurance
    ),
    (
        r"77260688",
        "Rata Agos",
        "Finanziamenti",
        93.90
    ),

    # Unknown financing - €103.81 monthly
    # Pattern: 202214930873012026643530190020...
    (
        r"20221493087301\d*",
        "Rata Finanziamento",
        "Finanziamenti",
        103.81
    ),

    # Unknown financing - €122.30 monthly (5th of month)
    # Pattern: 202218724931422026643530190020...
    (
        r"20221872493142\d*",
        "Rata Finanziamento 2",
        "Finanziamenti",
        122.30
    ),

    # =====================================================================
    # UTENZE (Utilities)
    # =====================================================================

    # Hera - Multiservizi (Gas, Water, Waste)
    # Customer code: 1007000323, Group contract: 200010338561
    (
        r"200010338561[-\d]*",
        "Bolletta Hera",
        "Utenze",
        None  # Variable amount
    ),
    (
        r"1007000323",
        "Bolletta Hera",
        "Utenze",
        None
    ),
    (
        r"HERA\s*(COMM|SPA|GROUP)",
        "Bolletta Hera",
        "Utenze",
        None
    ),

    # Octopus Energy - Electricity
    (
        r"Octopus\s*Energy.*Energia\s*Elettrica",
        "Octopus Energia Elettrica",
        "Utenze",
        None
    ),
    (
        r"Octopus\s*Energy",
        "Octopus Energy",
        "Utenze",
        None
    ),
    (
        r"A-D541F5FF",  # Customer reference code
        "Octopus Energy",
        "Utenze",
        None
    ),

    # =====================================================================
    # REVOLUT REPAYMENT
    # =====================================================================
    (
        r"(outstanding\s*partial\s*)?repayment.*revolut|revolut.*repayment",
        "Rata Revolut Credit",
        "Finanziamenti",
        175.90
    ),
    (
        r"revolut\s*credit",
        "Rata Revolut Credit",
        "Finanziamenti",
        175.90
    ),

    # =====================================================================
    # STIPENDIO (Salary)
    # =====================================================================
    (
        r"ACCREDITO\s*COMPETENZE\s*MESE",
        "Stipendio",
        "Stipendio",
        None
    ),
    (
        r"ACCREDITO\s*MENS\.\s*AGG",
        "Tredicesima/Quattordicesima",
        "Stipendio",
        None
    ),
]


def map_transaction_description(description: str) -> Tuple[Optional[str], Optional[str], Optional[float]]:
    """
    Map a cryptic transaction description to a human-readable name.

    Args:
        description: The original transaction description

    Returns:
        Tuple of (readable_name, suggested_category, expected_amount)
        Returns (None, None, None) if no mapping found
    """
    if not description:
        return None, None, None

    desc_upper = description.upper()

    for mapping in TRANSACTION_MAPPINGS:
        pattern, readable_name, category, expected_amount = mapping

        # Try regex match (case insensitive)
        if re.search(pattern, description, re.IGNORECASE):
            return readable_name, category, expected_amount

    return None, None, None


def get_readable_description(description: str) -> str:
    """
    Get a readable version of the transaction description.
    Falls back to original if no mapping found.

    Args:
        description: The original transaction description

    Returns:
        Human-readable description
    """
    readable_name, _, _ = map_transaction_description(description)
    return readable_name if readable_name else description


def enrich_transaction(transaction: dict) -> dict:
    """
    Enrich a transaction dict with mapped description and category hints.

    Args:
        transaction: Transaction dictionary with 'description' key

    Returns:
        Enriched transaction with additional keys:
        - 'mapped_description': Human-readable description
        - 'suggested_category': Category hint from mapping
        - 'expected_amount': Expected amount for this transaction type
    """
    description = transaction.get("description", "")
    readable_name, category, expected_amount = map_transaction_description(description)

    result = transaction.copy()
    if readable_name:
        result["mapped_description"] = readable_name
        result["suggested_category"] = category
        result["expected_amount"] = expected_amount

    return result


# Quick test
if __name__ == "__main__":
    test_descriptions = [
        "202216820433692026643530190020221682043369   DE LUCA MATTIA FILIP",
        "PR. 77260688/001/01 01/01/26",
        "200010338561-142500543517-412528018929",
        "Octopus Energy - A-D541F5FF - Energia Elettrica",
        "202214930873012026643530190020221493087301   DE LUCA MATTIA FILIP",
        "202218724931422026643530190020221872493142   DE LUCA MATTIA FILIP",
        "ACCREDITO COMPETENZE MESE DI NOVEMBRE 2025",
        "random transaction",
    ]

    print("Transaction Mapping Test:")
    print("=" * 60)
    for desc in test_descriptions:
        readable, category, amount = map_transaction_description(desc)
        if readable:
            print(f"'{desc[:50]}...'")
            print(f"  -> {readable} ({category}) €{amount or 'variable'}")
        else:
            print(f"'{desc[:50]}...' -> NO MAPPING")
        print()
