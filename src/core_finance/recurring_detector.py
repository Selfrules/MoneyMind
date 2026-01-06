"""
Recurring Expense Auto-Detection Engine

Automatically detects recurring expense patterns from transaction history
and classifies them by type (subscription, financing, essential, service).
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database import (
    get_db_context, get_transactions, get_category_by_name,
    add_recurring_expense, update_recurring_expense,
    get_recurring_expenses, link_transaction_to_recurring
)


# ============================================================================
# Provider Classification Lists
# ============================================================================

FINANCING_PROVIDERS = [
    "agos", "findomestic", "compass", "santander consumer",
    "cofidis", "fiditalia", "sella personal", "klarna", "scalapay",
    "afterpay", "pagolight", "soisy", "younited", "creditras",
    "prestito personale", "finanziamento", "rata mensile",
    "personal loan", "paga in 3", "paga in 4", "buy now pay later"
]

ESSENTIAL_PROVIDERS = [
    # Utilities
    "hera", "enel", "eni", "a2a", "iren", "sorgenia", "edison",
    "octopus energy", "plenitude", "eon",
    # Telecom
    "tim", "vodafone", "iliad", "windtre", "fastweb", "ho mobile", "kena",
    # Housing
    "affitto", "condominio", "canone", "mutuo", "ipoteca",
    # Insurance
    "assicurazione", "polizza", "unipolsai", "generali", "allianz", "axa"
]

SUBSCRIPTION_PROVIDERS = [
    # Streaming
    "netflix", "spotify", "disney", "amazon prime", "youtube premium",
    "apple music", "dazn", "now tv", "paramount", "hbo", "crunchyroll",
    # Software/Tools
    "github", "chatgpt", "openai", "claude", "anthropic", "notion",
    "figma", "adobe", "canva", "dropbox", "google one", "icloud",
    "microsoft 365", "office 365", "zoom", "slack", "asana",
    # News/Content
    "medium", "substack", "patreon", "onlyfans",
    # Fitness
    "strava", "whoop", "fitbit", "peloton", "apple fitness",
    # Dating
    "tinder", "bumble", "hinge",
    # Gaming
    "playstation", "xbox", "nintendo", "steam", "epic games",
    # VPN/Security
    "nordvpn", "expressvpn", "1password", "bitwarden", "lastpass",
    # Financial
    "revolut", "wise", "n26", "nexi"
]

SERVICE_PROVIDERS = [
    "pulizie", "colf", "badante", "babysitter", "dog sitter",
    "giardiniere", "manutenzione", "personal trainer", "fisioterapista"
]


@dataclass
class RecurringPattern:
    """Detected recurring expense pattern."""
    provider: str
    description_pattern: str
    category_id: int
    category_name: str
    frequency: str  # 'weekly', 'monthly', 'quarterly', 'annual'
    avg_amount: float
    min_amount: float
    max_amount: float
    occurrence_count: int
    first_date: str
    last_date: str
    confidence: float
    recurring_type: str  # 'subscription', 'financing', 'essential', 'service'
    cancellability: str  # 'easy', 'medium', 'hard', 'locked'
    transactions: List[Dict]


class RecurringDetector:
    """
    Auto-detection engine for recurring expense patterns.

    Analyzes transaction history to find:
    - Same provider/description
    - Similar amounts (within tolerance)
    - Regular frequency (weekly, monthly, quarterly, annual)
    - Minimum occurrences for confidence
    """

    def __init__(self, amount_tolerance: float = 0.15, min_occurrences: int = 3):
        """
        Initialize the detector.

        Args:
            amount_tolerance: How much amounts can vary (0.15 = ±15%)
            min_occurrences: Minimum times pattern must appear
        """
        self.amount_tolerance = amount_tolerance
        self.min_occurrences = min_occurrences

    def detect_patterns(self, months: int = 6) -> List[RecurringPattern]:
        """
        Scan transactions from the last N months to find recurring patterns.

        Args:
            months: Number of months to analyze

        Returns:
            List of detected recurring patterns
        """
        # Get transactions for the analysis period
        start_date = (datetime.now() - timedelta(days=months * 30)).strftime("%Y-%m-%d")
        transactions = get_transactions({"start_date": start_date})

        # Only analyze expenses (negative amounts)
        expenses = [t for t in transactions if t["amount"] < 0]

        # Group by normalized description
        groups = self._group_by_description(expenses)

        # Analyze each group for recurring patterns
        patterns = []
        for key, txs in groups.items():
            if len(txs) >= self.min_occurrences:
                pattern = self._analyze_group(key, txs)
                if pattern:
                    patterns.append(pattern)

        # Sort by confidence and amount
        patterns.sort(key=lambda p: (-p.confidence, -p.avg_amount))

        return patterns

    def _normalize_description(self, description: str) -> str:
        """Normalize description for grouping."""
        if not description:
            return ""

        desc = description.lower()

        # Remove common prefixes/suffixes
        desc = re.sub(r'^(pagamento |acquisto |addebito |prelievo )', '', desc)
        desc = re.sub(r'( srl| spa| ltd| inc| gmbh)$', '', desc)

        # Remove dates, numbers, reference codes
        desc = re.sub(r'\d{2}/\d{2}/\d{4}', '', desc)
        desc = re.sub(r'\d{2}-\d{2}-\d{4}', '', desc)
        desc = re.sub(r'\b\d{6,}\b', '', desc)  # Reference numbers

        # Remove extra whitespace
        desc = ' '.join(desc.split())

        return desc.strip()

    def _extract_provider(self, description: str) -> str:
        """Extract provider name from description."""
        if not description:
            return "unknown"

        desc = description.lower()

        # Check known providers
        all_providers = (
            FINANCING_PROVIDERS + ESSENTIAL_PROVIDERS +
            SUBSCRIPTION_PROVIDERS + SERVICE_PROVIDERS
        )

        for provider in all_providers:
            if provider in desc:
                return provider.title()

        # Try to extract first meaningful word
        words = desc.split()
        for word in words:
            if len(word) > 3 and not word.isdigit():
                return word.title()

        return "Unknown"

    def _group_by_description(self, transactions: List[Dict]) -> Dict[str, List[Dict]]:
        """Group transactions by normalized description."""
        groups = defaultdict(list)

        for tx in transactions:
            normalized = self._normalize_description(tx.get("description", ""))
            if normalized:
                groups[normalized].append(tx)

        return groups

    def _analyze_group(self, key: str, transactions: List[Dict]) -> Optional[RecurringPattern]:
        """Analyze a group of transactions for recurring pattern."""
        if len(transactions) < self.min_occurrences:
            return None

        # Calculate amount statistics
        amounts = [abs(t["amount"]) for t in transactions]
        avg_amount = sum(amounts) / len(amounts)
        min_amount = min(amounts)
        max_amount = max(amounts)

        # Check amount variance - skip if too variable
        if max_amount > 0 and (max_amount - min_amount) / avg_amount > self.amount_tolerance * 2:
            return None

        # Analyze frequency
        dates = sorted([datetime.strptime(t["date"], "%Y-%m-%d") for t in transactions])
        frequency = self._detect_frequency(dates)

        if not frequency:
            return None

        # Calculate confidence score
        confidence = self._calculate_confidence(transactions, dates, frequency, amounts)

        if confidence < 0.5:
            return None

        # Extract provider and classify type
        provider = self._extract_provider(transactions[0].get("description", ""))
        recurring_type = self._classify_recurring_type(provider, transactions[0].get("description", ""))
        cancellability = self._determine_cancellability(recurring_type, provider)

        # Get category info
        category_id = transactions[0].get("category_id")
        category_name = transactions[0].get("category_name", "Altro")

        return RecurringPattern(
            provider=provider,
            description_pattern=key,
            category_id=category_id,
            category_name=category_name,
            frequency=frequency,
            avg_amount=round(avg_amount, 2),
            min_amount=round(min_amount, 2),
            max_amount=round(max_amount, 2),
            occurrence_count=len(transactions),
            first_date=dates[0].strftime("%Y-%m-%d"),
            last_date=dates[-1].strftime("%Y-%m-%d"),
            confidence=round(confidence, 2),
            recurring_type=recurring_type,
            cancellability=cancellability,
            transactions=transactions
        )

    def _detect_frequency(self, dates: List[datetime]) -> Optional[str]:
        """Detect the frequency of transactions."""
        if len(dates) < 2:
            return None

        # Calculate gaps between consecutive dates
        gaps = []
        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i-1]).days
            gaps.append(gap)

        avg_gap = sum(gaps) / len(gaps)

        # Classify frequency
        if avg_gap <= 10:  # ~weekly
            return "weekly"
        elif 20 <= avg_gap <= 45:  # ~monthly
            return "monthly"
        elif 80 <= avg_gap <= 100:  # ~quarterly
            return "quarterly"
        elif 350 <= avg_gap <= 380:  # ~annual
            return "annual"

        return None

    def _calculate_confidence(
        self,
        transactions: List[Dict],
        dates: List[datetime],
        frequency: str,
        amounts: List[float]
    ) -> float:
        """Calculate confidence score for the pattern."""
        confidence = 0.0

        # Factor 1: Number of occurrences (max 0.3)
        occ_score = min(len(transactions) / 6, 1.0) * 0.3
        confidence += occ_score

        # Factor 2: Amount consistency (max 0.3)
        avg = sum(amounts) / len(amounts)
        if avg > 0:
            variance = sum((a - avg) ** 2 for a in amounts) / len(amounts)
            cv = (variance ** 0.5) / avg  # Coefficient of variation
            amount_score = max(0, 1 - cv) * 0.3
            confidence += amount_score

        # Factor 3: Frequency consistency (max 0.3)
        expected_gap = {
            "weekly": 7,
            "monthly": 30,
            "quarterly": 91,
            "annual": 365
        }.get(frequency, 30)

        gaps = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
        if gaps:
            avg_gap = sum(gaps) / len(gaps)
            gap_error = abs(avg_gap - expected_gap) / expected_gap
            freq_score = max(0, 1 - gap_error) * 0.3
            confidence += freq_score

        # Factor 4: Provider recognition (max 0.1)
        provider = self._extract_provider(transactions[0].get("description", ""))
        if provider.lower() in [p.lower() for p in (FINANCING_PROVIDERS + ESSENTIAL_PROVIDERS + SUBSCRIPTION_PROVIDERS)]:
            confidence += 0.1

        return min(confidence, 1.0)

    def _classify_recurring_type(self, provider: str, description: str) -> str:
        """Classify the recurring expense type."""
        desc_lower = (description or "").lower()
        provider_lower = provider.lower()

        # Check financing first (contracts)
        for p in FINANCING_PROVIDERS:
            if p in provider_lower or p in desc_lower:
                return "financing"

        # Check essential
        for p in ESSENTIAL_PROVIDERS:
            if p in provider_lower or p in desc_lower:
                return "essential"

        # Check services
        for p in SERVICE_PROVIDERS:
            if p in provider_lower or p in desc_lower:
                return "service"

        # Check subscriptions
        for p in SUBSCRIPTION_PROVIDERS:
            if p in provider_lower or p in desc_lower:
                return "subscription"

        # Default to subscription for unknown recurring
        return "subscription"

    def _determine_cancellability(self, recurring_type: str, provider: str) -> str:
        """Determine how easy it is to cancel this expense."""
        if recurring_type == "financing":
            return "locked"  # Contract bound
        elif recurring_type == "essential":
            return "hard"  # Necessary expense
        elif recurring_type == "service":
            return "medium"  # Depends on relationship
        else:
            return "easy"  # Most subscriptions

    def save_patterns_to_db(self, patterns: List[RecurringPattern]) -> int:
        """
        Save detected patterns to the database as recurring expenses.

        Args:
            patterns: List of detected patterns

        Returns:
            Number of patterns saved
        """
        saved = 0

        # Get existing recurring expenses to avoid duplicates
        existing = get_recurring_expenses(active_only=False)
        existing_patterns = {r["pattern_name"].lower() for r in existing}

        for pattern in patterns:
            # Skip if already exists
            if pattern.provider.lower() in existing_patterns:
                continue

            try:
                recurring_id = add_recurring_expense({
                    "pattern_name": pattern.provider,
                    "category_id": pattern.category_id,
                    "frequency": pattern.frequency,
                    "avg_amount": pattern.avg_amount,
                    "min_amount": pattern.min_amount,
                    "max_amount": pattern.max_amount,
                    "last_amount": pattern.avg_amount,
                    "first_occurrence": pattern.first_date,
                    "last_occurrence": pattern.last_date,
                    "occurrence_count": pattern.occurrence_count,
                    "provider": pattern.provider,
                    "is_essential": 1 if pattern.recurring_type == "essential" else 0,
                    "confidence_score": pattern.confidence,
                })

                # Update with v7.0 fields
                update_recurring_expense(recurring_id, {
                    "recurring_type": pattern.recurring_type,
                    "cancellability": pattern.cancellability,
                    "auto_detected": 1
                })

                # Link transactions to this recurring expense
                for tx in pattern.transactions:
                    link_transaction_to_recurring(tx["id"], recurring_id, pattern.confidence)

                saved += 1

            except Exception as e:
                print(f"Error saving pattern {pattern.provider}: {e}")
                continue

        return saved


def run_detection(months: int = 6, save: bool = True) -> List[RecurringPattern]:
    """
    Run the recurring expense detection.

    Args:
        months: Number of months to analyze
        save: Whether to save patterns to database

    Returns:
        List of detected patterns
    """
    detector = RecurringDetector()
    patterns = detector.detect_patterns(months)

    if save and patterns:
        saved = detector.save_patterns_to_db(patterns)
        print(f"Detected {len(patterns)} patterns, saved {saved} new ones to database")

    return patterns


# CLI entry point
if __name__ == "__main__":
    print("Running recurring expense detection...")
    patterns = run_detection(months=6, save=True)

    print(f"\nDetected {len(patterns)} recurring patterns:\n")
    for p in patterns[:20]:  # Show top 20
        print(f"  {p.provider}: €{p.avg_amount:.2f}/{p.frequency}")
        print(f"    Type: {p.recurring_type} | Cancel: {p.cancellability} | Confidence: {p.confidence:.0%}")
        print(f"    Occurrences: {p.occurrence_count} | {p.first_date} - {p.last_date}")
        print()
