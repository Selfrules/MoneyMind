# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MoneyMind v3.0 is a personal finance coach app built with Streamlit. It's an AI-First, Mobile-Native, Freedom-Focused financial dashboard that helps users track transactions, manage debts, set goals, and achieve financial freedom through personalized AI coaching.

## Development Commands

```bash
# Run the application
streamlit run app.py

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file with:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Architecture

### Single-Page App with Bottom Tab Navigation
The app uses a mobile-first SPA architecture with 5 main tabs:

- **Home** - Freedom Score card, quick stats (net worth, debt), current financial phase, AI insights, recent transactions
- **Money** - Sub-tabs for Transactions (monthly grouped list), Budget (progress bars), Trends (income vs expenses chart)
- **Coach** - AI chat interface with suggested questions, rule-based responses analyzing user's financial data
- **Goals** - Debt freedom tracker with Avalanche strategy, timeline visualization, future goals (emergency fund, custom)
- **Profile** - User info, financial health KPIs (savings rate, DTI ratio, emergency fund months), actions menu

### Core Modules (`src/`)
- `database.py` - SQLite database with extended schema for debts, goals, insights, KPI history, chat history. Uses context manager pattern (`get_db_context()`). Initializes 19 default Italian spending categories.
- `analytics.py` - Financial KPI calculations:
  - Net worth, savings rate, DTI ratio
  - Debt payoff strategies (Avalanche vs Snowball with projections)
  - Spending trends and anomaly detection
  - Financial health score (0-100 with grade A-F)
  - Budget recommendations (50/30/20 rule adapted for debt phase)
- `styles.py` - Complete design system with mobile-first CSS, component templates (freedom_score_card, metric_card, transaction_row, chat_bubble, debt_card, goal_progress_card, etc.)
- `utils.py` - Utility functions

### AI Integration (`src/ai/`)
- `categorizer.py` - Hybrid categorization system:
  - **Phase 1: Rule-based** - Pattern matching for known providers (~70% hit rate)
  - **Phase 2: Claude AI** - Haiku for remaining transactions in batches of 15
- `advisor.py` - AI Financial Advisor using Claude Opus 4.5:
  - Extended thinking mode for deep analysis
  - `get_financial_advice()` - Personalized advice with full financial context
  - `generate_monthly_coaching()` - Monthly report with KPI analysis and action plan
  - `analyze_spending_opportunity()` - Category-specific optimization suggestions
  - `explain_concept()` - Financial education in simple terms
  - `evaluate_financial_decision()` - Decision analysis with pros/cons
- `reporter.py` - Monthly report generation using Claude Sonnet

### Bank Parsers (`src/parsers/`)
- `revolut.py` - Auto-detects Italian format and Legacy format, generates SHA256 IDs
- `illimity.py` - Parses XLSX exports, maps Italian transaction types

### Categorization Rules (`src/ai/categorizer.py`)
- **Savings**: Revolut roundups ("Accredita EUR Risparmio") -> `Risparmi Automatici`
- **Utilities**: Octopus Energy, Hera, Iren, Enel -> `Utenze`
- **Loans**: Agos, Findomestic, Illimity SDD codes -> `Finanziamenti`
- **Subscriptions**: Netflix, Spotify, Prime Video, GitHub -> `Abbonamenti`
- **Salary**: "ACCREDITO COMPETENZE", "ACCREDITO MENS" -> `Stipendio`
- **Transfers**: "Trasferimento" descriptions -> `Trasferimenti`

## Database Schema

```sql
-- Categories (19 defaults including Finanziamenti, Risparmi Automatici)
categories(id, name, icon, color)

-- Transactions (SHA256 id for deduplication)
transactions(id, date, description, amount, category_id, bank, account_type, type, balance)

-- Budgets (per category per month)
budgets(id, category_id, amount, month)

-- User profile (singleton)
user_profile(id, income_type, monthly_net_income, risk_tolerance, financial_knowledge, coaching_style)

-- Debt tracking
debts(id, name, type, original_amount, current_balance, interest_rate, monthly_payment, payment_day, is_active)

-- Financial goals
goals(id, name, type, target_amount, current_amount, priority, status, target_date)

-- AI insights/alerts
insights(id, type, category, severity, title, message, action_text, is_read, is_dismissed)

-- Monthly KPI snapshots
kpi_history(id, month, net_worth, total_debt, savings_rate, dti_ratio, emergency_fund_months)

-- AI coach chat history
chat_history(id, session_id, role, content, tokens_used)
```

## Design System

Mobile-first dark theme with emerald green (#10B981) accent. Key color tokens in `src/styles.py`:
- Background: #0A0A0A (primary), #141414 (cards), #1E1E1E (tertiary)
- Text: #FAFAFA (primary), #A1A1AA (secondary), #71717A (muted)
- Semantic: income (#22C55E), expense (#EF4444), warning (#F59E0B), accent (#10B981)

Layout: Centered (not wide), collapsed sidebar, bottom tab navigation with fixed positioning.

## Key Patterns

- **Session state**: `active_tab` for navigation, `chat_messages` for coach history, `money_subtab` for Money tab
- **Data loading**: `load_dashboard_data()` cached function loads all data at once
- **Custom components**: HTML rendered via `st.markdown(unsafe_allow_html=True)` using template functions from styles.py
- **Amount convention**: Positive = income, negative = expense
- **Date format**: YYYY-MM-DD internally, localized display
- **Financial phases**: "Debt Payoff" (has debts) or "Wealth Building" (debt-free)

## Financial Health Score Algorithm

Calculated in `analytics.py:calculate_financial_health_score()`:
- **Savings Rate (25 pts)**: 20%+ = 25, 10% = 15, 0% = 0
- **DTI Ratio (25 pts)**: <20% = 25, <36% = 15, >50% = 0
- **Emergency Fund (25 pts)**: 6+ months = 25, 3 months = 15, 0 = 0
- **Net Worth Trend (25 pts)**: Positive = 25, Flat = 10, Negative = 0

Grades: A (80+), B (65+), C (50+), D (35+), F (<35)

## Debt Payoff Strategies

Both implemented in `analytics.py`:
- **Avalanche**: Highest interest rate first (saves most money)
- **Snowball**: Smallest balance first (psychological wins)

`compare_payoff_strategies()` returns total months, total interest, and recommendation.

## Adding New Features

### New Categorization Rules
Edit `src/ai/categorizer.py` - add to provider lists or pattern lists.

### New Database Tables
1. Add CREATE TABLE to SCHEMA_SQL in `database.py`
2. Add CRUD functions following existing patterns
3. Run `init_db()` to create tables

### New UI Components
1. Add template function in `styles.py` returning HTML string
2. Use `st.markdown(component_func(...), unsafe_allow_html=True)`

## File Organization

```
MoneyMind/
├── app.py                    # Main SPA with all tabs
├── CLAUDE.md                 # This file
├── requirements.txt
├── .env                      # API keys (not committed)
├── .streamlit/config.toml    # Streamlit theme config
├── data/
│   └── moneymind.db          # SQLite database
├── src/
│   ├── database.py           # DB schema and CRUD
│   ├── analytics.py          # KPIs, debt strategies, health score
│   ├── styles.py             # Design system and components
│   ├── utils.py              # Utilities
│   ├── ai/
│   │   ├── categorizer.py    # Transaction categorization
│   │   ├── advisor.py        # AI coach (Opus 4.5)
│   │   └── reporter.py       # Monthly reports (Sonnet)
│   └── parsers/
│       ├── revolut.py        # Revolut CSV parser
│       └── illimity.py       # Illimity XLSX parser
└── misc/
    └── pages_backup_v2/      # Old multi-page structure (archived)
```
