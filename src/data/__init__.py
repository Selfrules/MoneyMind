"""
Data module for MoneyMind.

Contains static data, mappings, and configuration data.
"""

from .transaction_mappings import (
    map_transaction_description,
    get_readable_description,
    enrich_transaction,
    TRANSACTION_MAPPINGS
)

__all__ = [
    'map_transaction_description',
    'get_readable_description',
    'enrich_transaction',
    'TRANSACTION_MAPPINGS',
]
