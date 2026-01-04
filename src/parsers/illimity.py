"""
Parser for Illimity bank Excel export files.

Illimity Excel file structure:
- Rows 1-15: Metadata (report header, account info)
- Row 16 (0-indexed: skiprows=16): Column headers
- Rows 17+: Transaction data

Columns: Data operazione, Tipologia, Causale, Stato, Entrate, Uscite, Valuta, Rapporto
"""

import hashlib
import re
from typing import List, Union, IO

import pandas as pd


def _generate_transaction_id(date: str, amount: float, description: str, bank: str) -> str:
    """Generate a unique transaction ID using SHA256 hash."""
    data = f"{date}|{amount}|{description}|{bank}"
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def _map_transaction_type(tipologia: str) -> str:
    """Map Illimity transaction types to standardized types."""
    if pd.isna(tipologia):
        return 'OTHER'

    tipologia_lower = tipologia.lower()

    if tipologia_lower == 'mandato sdd':
        return 'SDD'
    elif re.match(r'^bonifico', tipologia_lower):
        return 'TRANSFER'
    else:
        return 'OTHER'


def parse_illimity(file_path_or_buffer: Union[str, IO]) -> List[dict]:
    """
    Parse Illimity bank Excel export file.

    Args:
        file_path_or_buffer: Either a file path string or a file-like object
                            (e.g., from Streamlit file upload)

    Returns:
        List of transaction dictionaries with keys:
        - id: Unique transaction ID (SHA256 hash)
        - date: Transaction date
        - description: Transaction description (from Causale)
        - amount: Transaction amount (positive for Entrate, negative for Uscite)
        - category_id: Category ID (None - not available)
        - bank: Bank name ('illimity')
        - account_type: Account type ('current')
        - type: Transaction type (SDD, TRANSFER, OTHER)
        - balance: Account balance (None - not available in Illimity export)
    """
    # Read Excel file, skipping first 16 rows to get headers at row 16
    df = pd.read_excel(file_path_or_buffer, skiprows=16)

    # Filter only executed transactions
    df = df[df['Stato'] == 'Eseguito']

    transactions = []

    for _, row in df.iterrows():
        # Parse date
        date = pd.to_datetime(row['Data operazione'])
        date_str = date.strftime('%Y-%m-%d')

        # Get description from Causale
        description = str(row['Causale']) if pd.notna(row['Causale']) else ''

        # Calculate amount: Entrate (positive), Uscite (negative)
        entrate = row['Entrate'] if pd.notna(row['Entrate']) else 0
        uscite = row['Uscite'] if pd.notna(row['Uscite']) else 0
        amount = float(entrate) - float(uscite)

        # Map transaction type
        transaction_type = _map_transaction_type(row['Tipologia'])

        # Generate unique ID
        transaction_id = _generate_transaction_id(date_str, amount, description, 'illimity')

        transaction = {
            'id': transaction_id,
            'date': date_str,
            'description': description,
            'amount': amount,
            'category_id': None,
            'bank': 'illimity',
            'account_type': 'current',
            'type': transaction_type,
            'balance': None
        }

        transactions.append(transaction)

    return transactions
