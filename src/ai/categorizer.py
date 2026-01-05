"""
AI-powered transaction categorizer using Claude API.

Features:
- Rule-based pre-categorization for known patterns (savings, utilities, loans)
- AI categorization via Claude for complex transactions
- Batch processing for efficiency
"""

import json
import os
import re
import time
from typing import List, Dict, Optional

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
    "Caffe",
    "Barbiere",
    "Trasferimenti",
    "Finanziamenti",
    "Risparmi Automatici",
    "Intrattenimento",
    "Regali",
    "Altro",
]

# Model configuration
MODEL = "claude-3-5-haiku-20241022"

# Retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF = 1  # seconds

# ============================================================================
# RULE-BASED CATEGORIZATION PATTERNS
# ============================================================================

# Patterns for automatic categorization (case-insensitive)
# These are matched BEFORE sending to AI to save API calls

SAVINGS_PATTERNS = [
    r"accredita.*risparmio",  # Revolut roundups
    r"risparmio.*eur",
    r"trasferisci.*risparmio",
]

UTILITY_PROVIDERS = [
    "octopus energy",
    "hera",
    "iren",
    "enel",
    "eni",
    "a2a",
    "sorgenia",
    "engie",
    "eon",
    "edison",
    "acea",
    "tim",
    "vodafone",
    "wind",
    "fastweb",
    "iliad",
]

LOAN_PROVIDERS = [
    "agos",
    "findomestic",
    "compass",
    "santander consumer",
    "cofidis",
    "fiditalia",
    "sella personal",
    "younited",
    "creditis",
    "prestitalia",
]

# Known recurring loan payment codes (Illimity SDD with long numeric IDs)
# These are identified by the pattern and consistent monthly amounts
LOAN_PAYMENT_PATTERNS = [
    r"^20221\d{20,}",  # Illimity SDD codes starting with 20221... (loan installments)
    r"^pr\.\s*\d{8}",  # PR. codes (e.g., PR. 77260688)
    r"bonifici\s+clienti",  # Loan disbursement from Agos via Illimity
]

# Utility payment codes (Hera S.P.A. for gas, water, waste)
UTILITY_PAYMENT_PATTERNS = [
    r"^200010338561",  # Hera S.P.A. SDD code
]

SALARY_PATTERNS = [
    r"accredito\s+competenze",
    r"accredito\s+mens",
    r"stipendio",
    r"competenze\s+mese",
]

SUBSCRIPTION_PATTERNS = [
    r"netflix",
    r"spotify",
    r"amazon prime",
    r"prime video",
    r"disney\+",
    r"youtube premium",
    r"apple music",
    r"google one",
    r"google workspace",
    r"github",
    r"chatgpt",
    r"openai",
    r"anthropic",
    r"claude",
    r"notion",
    r"figma",
    r"slack",
    r"zoom",
    r"microsoft 365",
    r"steam",
    r"gog\.com",
    r"linkedin",
    r"make\b",
    r"adobe",
    r"canva",
    r"dropbox",
    r"icloud",
    r"xbox",
    r"playstation",
    r"twitch",
    r"patreon",
    r"substack",
    r"medium",
    r"onlyfans",
    r"elevenlabs",
    r"midjourney",
    r"replicate",
    r"runway",
    r"paypal",
    r"excalidraw",
    r"^google$",  # Google subscription (storage, etc.)
    r"register\.it",
    r"squarespace",
    r"whoop",
    r"aruba\.it",
    r"audible",
    r"odealo",
    r"nexi",  # Card fee
    r"wise",  # Service fee
    r"canone\s*piano",  # Revolut plan fee
    r"gamma",  # AI slides tool
    r"vtsup",  # Dating site subscription
]

# Shopping patterns
SHOPPING_PATTERNS = [
    r"amazon(?!\s*prime)",  # Amazon but not Amazon Prime (subscription)
    r"apple\b",
    r"zalando",
    r"asos",
    r"h&m",
    r"zara",
    r"ikea",
    r"decathlon",
    r"unieuro",
    r"mediaworld",
    r"euronics",
    r"nespresso",
    r"aliexpress",
    r"ebay",
    r"wish",
    r"shein",
    r"gutteridge",  # Clothing
    r"soncini",  # Clothing shop
    r"floriba",  # Shop
    r"sonosystem",  # Electronics
    r"ethical\s*grace",  # Shop
]

# Restaurant/Food delivery patterns
RESTAURANT_PATTERNS = [
    r"just\s*eat",
    r"deliveroo",
    r"glovo",
    r"uber\s*eats",
    r"ristorante",
    r"pizzeria",
    r"trattoria",
    r"osteria",
    r"sushi",
    r"mcdonald",
    r"burger\s*king",
    r"kfc",
    r"domino",
    r"la\s*piadineria",
    r"old\s*wild\s*west",
    r"roadhouse",
    r"alice\s*pizza",
    r"spontini",
    r"eataly",
    r"lar\s*e\s*gola",
    r"l\s*isola\s*dei",
    r"lisola\s*dei",
    r"dispensa\s*emilia",
    r"doppio\s*malto",
    r"officina\s*della\s*senape",
    r"sedimento",
    r"la\s*stria",
    r"miky\s*2",
    r"piada\s*mare",
    r"birreria",
    r"tramvai",
    r"alternativo",
    r"bottega\s*moline",
    r"box\s*13\s*14",
    r"circolo\s*culturale",
    r"pizza\s*luciano",
    r"tenuta\s*dei\s*sapori",
    r"enoteca",
    r"drogheria",
    r"terra\s*di\s*piada",
    r"panini\s*di\s*mir",
    r"giustospirito",
    r"la\s*brace",
    r"sapore\s*di\s*mare",
    r"leglisecafe",
    r"fermento\s*in\s*villa",
    r"liquida\s*snc",
    r"bivio\s*enoteca",
    r"civico\s*12",
    r"ris8\s*dai",
    r"societa\s*agricola",
    r"societ.\s*agricola",
    r"abraciami",  # Restaurant
    r"chimon",  # Restaurant
]

# Bar/Cafe patterns
CAFE_PATTERNS = [
    r"\bbar\b",
    r"caff[eè]",
    r"starbucks",
    r"autogrill",
    r"gelat",
    r"pasticceria",
    r"gelateria",
    r"panificio",
    r"forno\b",
    r"buonristoro",
    r"il convio",
    r"tentazioni",
    r"guardiola",
    r"la\s*crema\s*di",
    r"phonzie",
    r"pompi\s*ginger",
    r"blue\s*hush",
    r"alleria",
    r"gafiubar",  # Pub San Lucido
]

# Veterinary/Pets patterns
PETS_PATTERNS = [
    r"veterinar",
    r"clinica.*animal",
    r"pet\s*shop",
    r"arcaplanet",
    r"zooplus",
    r"maxizoo",
    r"isola.*tesori",
    r"zarpas",
    r"arca\s*di\s*no[eè]",
    r"arcacat",  # Cat shop
]

# Transport patterns
TRANSPORT_PATTERNS = [
    r"trenitalia",
    r"italo",
    r"uber(?!\s*eats)",
    r"taxi",
    r"mytaxi",
    r"free\s*now",
    r"atm\s*milano",
    r"atc\s*bologna",
    r"seta",
    r"tper",
    r"eni\s*station",
    r"q8",
    r"ip\s*station",
    r"tamoil",
    r"autostrad",
    r"telepass",
    r"parcheggio",
    r"parking",
    r"parkagent",
    r"af\s*petroli",
    r"benzin",
    r"carburante",
]

# Health/Pharmacy patterns
HEALTH_PATTERNS = [
    r"farmacia",
    r"parafarmacia",
    r"medico",
    r"dottore",
    r"ospedale",
    r"clinica(?!.*veterinar)",
    r"laboratorio\s*analisi",
    r"dentista",
    r"oculista",
    r"ottico",
    r"estetista",
    r"simona\s*barbaglia",  # Estetista
]

# Barber/Hair patterns
BARBER_PATTERNS = [
    r"barber",
    r"parrucchier",
    r"hair",
    r"anymore\s*style",
    r"salone\s*bellezza",
]

# Internal transfers (between own accounts)
INTERNAL_TRANSFER_PATTERNS = [
    r"pagamento\s*da\s*mattia",
    r"prelievo\s*da\s*pocket",
    r"prelievo\s*di\s*contanti",
    r"prelievo\s*atm",
    r"trasferisci\s*a",
]

# Buy now pay later / Revolut financing
BNPL_PATTERNS = [
    r"paga\s*in\s*3",
    r"paga\s*in\s*4",
    r"klarna",
    r"scalapay",
    r"afterpay",
    r"repayment",
    r"personal\s*loan",  # Revolut personal loan
]

# Supermarket/Grocery patterns
GROCERY_PATTERNS = [
    r"conad",
    r"coop\b",
    r"esselunga",
    r"carrefour",
    r"lidl",
    r"eurospin",
    r"aldi",
    r"pam\b",
    r"despar",
    r"md\s*discount",
    r"penny\s*market",
    r"supermercato",
    r"market",
    r"alimentari",
    r"macelleria",
    r"9810\s*spilamberto",  # Local shop
]

PSYCHOLOGIST_PATTERNS = [
    r"unobravo",
    r"psicologo",
    r"psicologa",
    r"psicoterapia",
    r"serenis",
    r"mindwork",
]

GYM_PATTERNS = [
    r"21\s*lab",
    r"palestra",
    r"fitness",
    r"gym",
    r"mcfit",
    r"virgin active",
]

# Travel patterns
TRAVEL_PATTERNS = [
    r"booking\.com",
    r"hotel",
    r"airbnb",
    r"ryanair",
    r"easyjet",
    r"vueling",
    r"wizzair",
    r"alitalia",
    r"ita\s*airways",
    r"bagno\s*\w+",  # Beach establishments (Bagno Sabrina, Bagno Garden, etc.)
    r"bagni\s*\d+",  # Bagni 29 30 31, etc.
    r"stabilimento",
    r"ombrellone",
    r"camping",
    r"ostello",
    r"hostel",
    r"b&b",
    r"bed\s*and\s*breakfast",
    r"agriturismo",
    r"trainline",
    r"the\s*social\s*hub",  # Hostel chain
]

# Entertainment patterns
ENTERTAINMENT_PATTERNS = [
    r"bowling",
    r"cinema",
    r"kinema",
    r"xceed",  # Nightclub ticketing
    r"dice\b",  # Event ticketing
    r"komodo",
    r"chibagni",
    r"bp\s*private\s*club",
    r"seminatore",  # PayPal transfer for entertainment
]

# Gifts patterns
GIFTS_PATTERNS = [
    r"regalo",
    r"gift",
    r"sp\s*creative\s*lab",  # Gift purchase
]


def _match_pattern(text: str, patterns: List[str]) -> bool:
    """Check if text matches any of the regex patterns."""
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True
    return False


def _match_provider(text: str, providers: List[str]) -> bool:
    """Check if text contains any of the provider names."""
    text_lower = text.lower()
    for provider in providers:
        if provider in text_lower:
            return True
    return False


def _categorize_by_rules(transaction: dict) -> Optional[str]:
    """
    Apply rule-based categorization for known patterns.

    Returns category name if matched, None otherwise.
    """
    description = str(transaction.get("description", "")).lower().strip()
    tx_type = str(transaction.get("type", "")).upper()
    amount = transaction.get("amount", 0)

    # Salary detection (Illimity ACCREDITO COMPETENZE)
    if _match_pattern(description, SALARY_PATTERNS):
        return "Stipendio"

    # Revolut savings roundups (always small negative amounts with specific description)
    if _match_pattern(description, SAVINGS_PATTERNS):
        return "Risparmi Automatici"

    # Savings account transfers (type TRANSFER with savings-related description)
    if tx_type == "TRANSFER" and "risparmio" in description:
        return "Risparmi Automatici"

    # Utility providers (by name)
    if _match_provider(description, UTILITY_PROVIDERS):
        return "Utenze"

    # Utility payments (by SDD code - Hera S.P.A.)
    if _match_pattern(description, UTILITY_PAYMENT_PATTERNS):
        return "Utenze"

    # Loan/financing providers (by name)
    if _match_provider(description, LOAN_PROVIDERS):
        return "Finanziamenti"

    # Loan payments (Illimity SDD with numeric codes - recurring fixed amounts)
    if _match_pattern(description, LOAN_PAYMENT_PATTERNS):
        return "Finanziamenti"

    # Subscription services
    if _match_pattern(description, SUBSCRIPTION_PATTERNS):
        return "Abbonamenti"

    # Psychologist
    if _match_pattern(description, PSYCHOLOGIST_PATTERNS):
        return "Psicologo"

    # Gym
    if _match_pattern(description, GYM_PATTERNS):
        return "Palestra"

    # Veterinary/Pets - check before generic shopping
    if _match_pattern(description, PETS_PATTERNS):
        return "Gatti"

    # Restaurants and food delivery
    if _match_pattern(description, RESTAURANT_PATTERNS):
        return "Ristoranti"

    # Bars and cafes
    if _match_pattern(description, CAFE_PATTERNS):
        return "Caffe"

    # Supermarkets and groceries
    if _match_pattern(description, GROCERY_PATTERNS):
        return "Spesa"

    # Transport
    if _match_pattern(description, TRANSPORT_PATTERNS):
        return "Trasporti"

    # Health/Pharmacy
    if _match_pattern(description, HEALTH_PATTERNS):
        return "Salute"

    # Barber/Hair salon
    if _match_pattern(description, BARBER_PATTERNS):
        return "Barbiere"

    # Travel (hotels, flights, beach, etc.)
    if _match_pattern(description, TRAVEL_PATTERNS):
        return "Viaggi"

    # Entertainment (bowling, cinema, events)
    if _match_pattern(description, ENTERTAINMENT_PATTERNS):
        return "Intrattenimento"

    # Gifts
    if _match_pattern(description, GIFTS_PATTERNS):
        return "Regali"

    # Buy now pay later (Revolut Paga in 3, repayments)
    if _match_pattern(description, BNPL_PATTERNS):
        return "Finanziamenti"

    # Internal transfers (between own accounts, ATM withdrawals)
    if _match_pattern(description, INTERNAL_TRANSFER_PATTERNS):
        return "Trasferimenti"

    # Shopping (check after more specific categories)
    if _match_pattern(description, SHOPPING_PATTERNS):
        return "Shopping"

    # Transfers between own accounts (Illimity bonifici to Revolut)
    if "trasferimento" in description and amount < 0:
        return "Trasferimenti"

    # TRANSFER type with negative amount typically means inter-account transfer
    if tx_type == "TRANSFER" and amount < -100:
        return "Trasferimenti"

    return None


# ============================================================================
# AI CATEGORIZATION
# ============================================================================

def _build_prompt(transactions: List[dict]) -> str:
    """Build the categorization prompt for a batch of transactions."""
    transactions_list = "\n".join(
        f"- ID: {t['id'][:16]}..., Descrizione: {t['description']}, "
        f"Importo: {t['amount']:.2f}€, Data: {t['date']}, Tipo: {t['type']}"
        for t in transactions
    )

    categories_str = ", ".join(CATEGORIES)

    return f"""Sei un assistente finanziario. Categorizza queste transazioni.

Transazioni:
{transactions_list}

Categorie disponibili: {categories_str}

Contesto sull'utente:
- PM in una azienda tech a Reggio Emilia
- Va in palestra al 21 Lab
- Ha gatti (spese veterinario, cibo, accessori)
- Usa Unobravo per psicologo
- Octopus Energy per la luce

Regole importanti:
- "Risparmi Automatici" = trasferimenti automatici al salvadanaio/risparmio (piccoli importi)
- "Finanziamenti" = rate prestiti (Agos, Findomestic, Compass, etc.)
- "Utenze" = bollette (luce, gas, acqua, internet, telefono)
- "Abbonamenti" = servizi digitali ricorrenti (Netflix, Spotify, etc.)
- "Trasferimenti" = bonifici tra propri conti

Rispondi SOLO in formato JSON:
{{"results": [{{"id": "hash_completo", "category": "NomeCategoria"}}, ...]}}"""


def _call_claude_with_retry(client: anthropic.Anthropic, prompt: str) -> dict:
    """Call Claude API with exponential backoff retry logic."""
    backoff = INITIAL_BACKOFF

    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=2048,
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

        except anthropic.APIError:
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
    batch_size: int = 15
) -> Dict[str, str]:
    """
    Categorize a list of transactions using rules + Claude AI.

    First applies rule-based categorization for known patterns,
    then uses Claude API for remaining transactions.

    Args:
        transactions: List of transaction dicts with keys:
            - id: unique identifier (hash)
            - description: transaction description
            - amount: transaction amount
            - date: transaction date
            - type: transaction type
        batch_size: Number of transactions to process per API call

    Returns:
        Dictionary mapping transaction_id to category_name
    """
    if not transactions:
        return {}

    results = {}
    needs_ai = []

    # Phase 1: Apply rule-based categorization
    for tx in transactions:
        category = _categorize_by_rules(tx)
        if category:
            results[tx["id"]] = category
        else:
            needs_ai.append(tx)

    # If all categorized by rules, return early
    if not needs_ai:
        return results

    # Phase 2: Use AI for remaining transactions
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        # Fallback to "Altro" if no API key
        for tx in needs_ai:
            results[tx["id"]] = "Altro"
        return results

    client = anthropic.Anthropic(api_key=api_key)

    # Process in batches
    for i in range(0, len(needs_ai), batch_size):
        batch = needs_ai[i:i + batch_size]

        try:
            prompt = _build_prompt(batch)
            response = _call_claude_with_retry(client, prompt)

            # Extract results from response
            for item in response.get("results", []):
                transaction_id = item.get("id")
                category = item.get("category")

                # Handle truncated IDs in response
                matching_tx = None
                for tx in batch:
                    if tx["id"].startswith(transaction_id) or transaction_id.startswith(tx["id"][:16]):
                        matching_tx = tx
                        break

                if matching_tx:
                    # Validate category
                    if category in CATEGORIES:
                        results[matching_tx["id"]] = category
                    else:
                        results[matching_tx["id"]] = "Altro"

            # Handle any transactions not in response
            for tx in batch:
                if tx["id"] not in results:
                    results[tx["id"]] = "Altro"

        except Exception:
            # On error, default all transactions in batch to "Altro"
            for t in batch:
                results[t["id"]] = "Altro"

    return results
