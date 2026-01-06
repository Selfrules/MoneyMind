"""Import transactions API routes."""
import sys
from pathlib import Path
from io import BytesIO, StringIO
from collections import Counter

# Add project root to path for importing src modules
ROUTES_DIR = Path(__file__).parent  # routes/
API_DIR = ROUTES_DIR.parent  # api/
APP_DIR = API_DIR.parent  # app/
BACKEND_DIR = APP_DIR.parent  # backend/
PROJECT_DIR = BACKEND_DIR.parent  # MoneyMind/
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from typing import Optional

from app.schemas.import_transactions import (
    ImportResponse,
    ImportedTransaction,
)
from src.parsers.revolut import parse_revolut
from src.parsers.illimity import parse_illimity
from src.ai.categorizer import categorize_transactions
from src.database import (
    insert_transactions,
    get_categories,
    get_category_by_name,
    get_transactions,
)


router = APIRouter()


@router.post("/transactions/import", response_model=ImportResponse)
async def import_transactions_endpoint(
    file: UploadFile = File(...),
    bank: str = Query(..., description="Bank type: 'revolut' or 'illimity'"),
):
    """
    Import transactions from CSV (Revolut) or XLSX (Illimity).

    1. Parse file using appropriate parser
    2. Categorize transactions using rules + AI
    3. Insert into database (duplicates are skipped via SHA256 ID)
    4. Return import summary
    """
    try:
        # Validate bank type
        if bank not in ["revolut", "illimity"]:
            raise HTTPException(status_code=400, detail="Bank must be 'revolut' or 'illimity'")

        # Read file content
        content = await file.read()

        # Parse transactions based on bank type
        if bank == "revolut":
            # Revolut uses CSV - decode to string
            try:
                text_content = content.decode("utf-8")
            except UnicodeDecodeError:
                text_content = content.decode("latin-1")
            file_buffer = StringIO(text_content)
            transactions = parse_revolut(file_buffer)
        else:  # illimity
            # Illimity uses XLSX - use BytesIO
            file_buffer = BytesIO(content)
            transactions = parse_illimity(file_buffer)

        if not transactions:
            raise HTTPException(status_code=400, detail="No transactions found in file")

        total_parsed = len(transactions)

        # Get existing transaction IDs to count duplicates
        existing_filters = {
            "start_date": min(tx["date"] for tx in transactions),
            "end_date": max(tx["date"] for tx in transactions),
        }
        existing_txs = get_transactions(existing_filters) or []
        existing_ids = {tx["id"] for tx in existing_txs}

        # Count duplicates
        new_transactions = [tx for tx in transactions if tx["id"] not in existing_ids]
        duplicates_skipped = total_parsed - len(new_transactions)

        # Categorize transactions
        categories = get_categories()
        category_map = {cat["name"]: cat for cat in categories}

        # Get category assignments from categorizer
        categorization_results = categorize_transactions(new_transactions)

        # Apply categories to transactions
        categorized_count = 0
        for tx in new_transactions:
            tx_id = tx.get("id")
            category_name = categorization_results.get(tx_id)
            if category_name and category_name in category_map:
                tx["category_id"] = category_map[category_name]["id"]
                tx["category_name"] = category_name
                tx["category_icon"] = category_map[category_name].get("icon", "")
                categorized_count += 1
            else:
                # Default to "Altro" if no category found
                altro = category_map.get("Altro")
                if altro:
                    tx["category_id"] = altro["id"]
                    tx["category_name"] = "Altro"
                    tx["category_icon"] = altro.get("icon", "❓")

        # Insert transactions into database
        imported_count = 0
        if new_transactions:
            imported_count = insert_transactions(new_transactions)

        # Build category breakdown
        category_counts = Counter(tx.get("category_name", "Altro") for tx in new_transactions)
        categories_breakdown = dict(category_counts)

        # Build sample transactions (first 10)
        sample_transactions = [
            ImportedTransaction(
                id=tx["id"],
                date=tx["date"],
                description=tx.get("description", ""),
                amount=tx["amount"],
                category_name=tx.get("category_name"),
                category_icon=tx.get("category_icon"),
                bank=tx.get("bank", bank),
                type=tx.get("type"),
            )
            for tx in new_transactions[:10]
        ]

        return ImportResponse(
            success=True,
            total_parsed=total_parsed,
            categorized_count=categorized_count,
            imported_count=imported_count,
            duplicates_skipped=duplicates_skipped,
            categories_breakdown=categories_breakdown,
            sample_transactions=sample_transactions,
            message=f"Imported {imported_count} transactions from {bank}. {duplicates_skipped} duplicates skipped.",
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
