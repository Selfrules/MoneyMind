"""
Revolut CSV parser for MoneyMind.

Parses Revolut export files (CSV format) and transforms them into
standardized transaction records for database insertion.
"""

import hashlib
from datetime import datetime
from io import StringIO
from typing import IO, List, Union

import pandas as pd


def _generate_transaction_id(date: datetime, amount: float, description: str, bank: str) -> str:
    """
    Generate a unique transaction ID using SHA256 hash.

    Args:
        date: Transaction date
        amount: Transaction amount
        description: Transaction description
        bank: Bank name

    Returns:
        SHA256 hash string of the combined fields
    """
    # Format date as ISO string for consistent hashing
    date_str = date.strftime("%Y-%m-%d %H:%M:%S")
    hash_input = f"{date_str}|{amount}|{description}|{bank}"
    return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()


def _map_account_type(account: str) -> str:
    """
    Map Revolut account codes to readable account types.

    Args:
        account: Revolut account code (e.g., 'REV_CUR', 'REV_SAV')

    Returns:
        Mapped account type string
    """
    account_mapping = {
        "REV_CUR": "current",
        "REV_SAV": "savings",
    }
    return account_mapping.get(account, account.lower())


def parse_revolut(file_path_or_buffer: Union[str, IO]) -> List[dict]:
    """
    Parse a Revolut CSV export file and return standardized transaction records.

    Args:
        file_path_or_buffer: Either a file path string or a file-like object
                            (e.g., from Streamlit's file_uploader)

    Returns:
        List of dictionaries containing transaction data ready for database insert.
        Each dict contains: id, date, description, amount, category_id, bank,
                          account_type, type, balance

    Raises:
        ValueError: If required columns are missing from the CSV
        pd.errors.EmptyDataError: If the file is empty
    """
    # Read CSV - handle both file paths and file-like objects
    if isinstance(file_path_or_buffer, str):
        df = pd.read_csv(file_path_or_buffer)
    else:
        # For file-like objects (e.g., Streamlit UploadedFile)
        # Need to handle potential bytes vs string content
        content = file_path_or_buffer.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        # Reset position if possible (for reusability)
        if hasattr(file_path_or_buffer, "seek"):
            file_path_or_buffer.seek(0)
        df = pd.read_csv(StringIO(content))

    # Validate required columns
    required_columns = {"timestamp", "account", "description", "amount", "type", "balance"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Transform data
    transactions = []
    bank = "revolut"

    for _, row in df.iterrows():
        # Convert Unix epoch timestamp to datetime
        date = datetime.fromtimestamp(row["timestamp"])

        # Map account type
        account_type = _map_account_type(row["account"])

        # Get values
        description = str(row["description"]) if pd.notna(row["description"]) else ""
        amount = float(row["amount"])
        tx_type = str(row["type"]) if pd.notna(row["type"]) else ""
        balance = float(row["balance"]) if pd.notna(row["balance"]) else None

        # Generate unique transaction ID
        tx_id = _generate_transaction_id(date, amount, description, bank)

        # Build transaction record
        transaction = {
            "id": tx_id,
            "date": date,
            "description": description,
            "amount": amount,
            "category_id": None,
            "bank": bank,
            "account_type": account_type,
            "type": tx_type,
            "balance": balance,
        }
        transactions.append(transaction)

    return transactions
