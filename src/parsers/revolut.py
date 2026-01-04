"""
Revolut CSV parser for MoneyMind.

Parses Revolut export files (CSV format) and transforms them into
standardized transaction records for database insertion.

Supports two formats:
1. New Italian CSV format (account-statement): Tipo, Prodotto, Data di inizio, etc.
2. Legacy parquet/CSV format: timestamp, account, description, amount, etc.
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
        account: Revolut account code (e.g., 'REV_CUR', 'REV_SAV', 'Attuale', 'Risparmi')

    Returns:
        Mapped account type string
    """
    account_mapping = {
        # Legacy format
        "REV_CUR": "current",
        "REV_SAV": "savings",
        # New Italian format
        "Attuale": "current",
        "Risparmi": "savings",
    }
    return account_mapping.get(account, account.lower() if account else "current")


def _map_transaction_type(tipo: str) -> str:
    """
    Map Italian transaction types to standardized types.

    Args:
        tipo: Italian transaction type from CSV

    Returns:
        Standardized transaction type
    """
    type_mapping = {
        "Pagamento con carta": "CARD_PAYMENT",
        "Pagamento": "TRANSFER",  # Usually savings roundups
        "Ricarica": "TOPUP",
        "Prelievo": "ATM",
        "Rimborso su carta": "CARD_REFUND",
        "Addebita": "CHARGE",
        "LOAN_PAYMENT": "LOAN_PAYMENT",
        "LOAN": "LOAN",
    }
    return type_mapping.get(tipo, tipo.upper() if tipo else "OTHER")


def _detect_format(df: pd.DataFrame) -> str:
    """
    Detect which Revolut CSV format is being used.

    Args:
        df: DataFrame loaded from CSV

    Returns:
        'italian' for new format, 'legacy' for old format
    """
    italian_columns = {"Tipo", "Prodotto", "Data di inizio", "Descrizione", "Importo", "Saldo"}
    legacy_columns = {"timestamp", "account", "description", "amount", "type", "balance"}

    if italian_columns.issubset(set(df.columns)):
        return "italian"
    elif legacy_columns.issubset(set(df.columns)):
        return "legacy"
    else:
        # Check partial matches
        if "Tipo" in df.columns and "Importo" in df.columns:
            return "italian"
        elif "timestamp" in df.columns:
            return "legacy"
        raise ValueError(f"Unknown CSV format. Columns found: {list(df.columns)}")


def _parse_italian_format(df: pd.DataFrame) -> List[dict]:
    """
    Parse the new Italian CSV format from Revolut.

    Columns: Tipo, Prodotto, Data di inizio, Data di completamento, Descrizione, Importo, Costo, Valuta, State, Saldo
    """
    transactions = []
    bank = "revolut"

    for _, row in df.iterrows():
        # Skip non-completed transactions
        if pd.notna(row.get("State")) and row["State"] != "COMPLETATO":
            continue

        # Parse date from "Data di completamento" (when transaction was finalized)
        date_str = row.get("Data di completamento") or row.get("Data di inizio")
        if pd.isna(date_str):
            continue

        date = pd.to_datetime(date_str)

        # Map account type from Prodotto
        account_type = _map_account_type(row.get("Prodotto", ""))

        # Get values
        description = str(row["Descrizione"]) if pd.notna(row.get("Descrizione")) else ""
        amount = float(row["Importo"]) if pd.notna(row.get("Importo")) else 0.0
        tx_type = _map_transaction_type(row.get("Tipo", ""))
        balance = float(row["Saldo"]) if pd.notna(row.get("Saldo")) else None

        # Generate unique transaction ID
        tx_id = _generate_transaction_id(date, amount, description, bank)

        transaction = {
            "id": tx_id,
            "date": date.strftime("%Y-%m-%d"),  # Convert to ISO string for SQLite
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


def _parse_legacy_format(df: pd.DataFrame) -> List[dict]:
    """
    Parse the legacy parquet/CSV format from Revolut.

    Columns: timestamp, account, description, amount, type, balance, etc.
    """
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

        transaction = {
            "id": tx_id,
            "date": date.strftime("%Y-%m-%d"),  # Convert to ISO string for SQLite
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


def parse_revolut(file_path_or_buffer: Union[str, IO]) -> List[dict]:
    """
    Parse a Revolut CSV export file and return standardized transaction records.

    Automatically detects and handles both the new Italian CSV format and
    the legacy parquet/CSV format.

    Args:
        file_path_or_buffer: Either a file path string or a file-like object
                            (e.g., from Streamlit's file_uploader)

    Returns:
        List of dictionaries containing transaction data ready for database insert.
        Each dict contains: id, date, description, amount, category_id, bank,
                          account_type, type, balance

    Raises:
        ValueError: If required columns are missing or format is unrecognized
        pd.errors.EmptyDataError: If the file is empty
    """
    # Read CSV - handle both file paths and file-like objects
    if isinstance(file_path_or_buffer, str):
        df = pd.read_csv(file_path_or_buffer)
    else:
        # For file-like objects (e.g., Streamlit UploadedFile)
        content = file_path_or_buffer.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        # Reset position if possible (for reusability)
        if hasattr(file_path_or_buffer, "seek"):
            file_path_or_buffer.seek(0)
        df = pd.read_csv(StringIO(content))

    # Detect format and parse accordingly
    format_type = _detect_format(df)

    if format_type == "italian":
        return _parse_italian_format(df)
    else:
        return _parse_legacy_format(df)
