# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MoneyMind v4.0 is an AI-First, Mobile-Native, Freedom-Focused personal finance coach built with Streamlit. It transforms from a passive tracker to a **directive assistant** that actively helps users reduce debt payoff time and increase monthly savings through concrete daily actions.

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
Mobile-first SPA architecture with 5 main tabs:

- **Home** - Freedom Score, Plan vs Actual comparison, Daily Actions (1-3 high-impact tasks), AI Insights, Scenario Comparison
- **Money** - Sub-tabs: Transactions, Budget, Trends, **Ricorrenti** (recurring expenses with optimization suggestions)
- **Coach** - AI chat with Claude Opus 4.5, context-aware responses, decision tracking
- **Goals** - Debt freedom tracker (Avalanche/Snowball), timeline visualization, emergency fund goals
- **Profile** - User info, financial health KPIs, impact stories from past decisions

### Core Modules (`src/`)

#### Database Layer
- `database.py` - SQLite with extended v4.0 schema. Context manager pattern (`get_db_context()`). 19 default Italian categories.

#### Analytics & Finance Engine (`src/core_finance/`)
- `baseline.py` - 3-month baseline calculator, current vs baseline comparison
- `debt_planner.py` - Monthly payment plans, scenario comparison (current vs MoneyMind), on-track status
- `budget_generator.py` - Auto-generate budgets from debt plan, 50/30/20 rule adapted for debt phase
- `replanner.py` - Monthly re-planning based on actual vs planned spending

#### Repository Pattern (`src/repositories/`)
- `base.py` - Abstract repository base class
- `transaction_repository.py`, `debt_repository.py`, `budget_repository.py`
- `recurring_repository.py`, `decision_repository.py`, `action_repository.py`
- `baseline_repository.py`

#### AI Layer (`src/ai/`)
- `categorizer.py` - **Hybrid categorization** with 100+ rule-based patterns (95% hit rate), Claude Haiku fallback
- `advisor.py` - Financial coach with Claude Opus 4.5 extended thinking
- `insight_engine.py` - Proactive insights (spending anomalies, optimization opportunities)
- `action_planner.py` - Daily action generation (Full Auto mode)
- `recurring_optimizer.py` - Smart suggestions for recurring expense optimization

#### Bank Parsers (`src/parsers/`)
- `revolut.py` - Italian format, Legacy format, SHA256 IDs
- `illimity.py` - XLSX exports, Italian transaction type mapping

### Categorization Rules (`src/ai/categorizer.py`)

**100+ patterns organized by category:**

| Category | Key Patterns |
|----------|-------------|
| Risparmi Automatici | `accredita.*risparmio`, Revolut roundups |
| Stipendio | `accredito competenze`, `accredito mens` |
| Utenze | Octopus, Hera, Iren, Enel, TIM, Vodafone, Iliad |
| Finanziamenti | Agos, Findomestic, `personal loan`, `paga in 3`, repayment |
| Abbonamenti | Netflix, Spotify, GitHub, ChatGPT, Notion, Whoop, Audible, Nexi, Wise |
| Ristoranti | JustEat, Deliveroo, pizzeria, trattoria, enoteca, birreria, 35+ local patterns |
| Caffe | `\bbar\b`, gelateria, pasticceria, panificio, 18+ local patterns |
| Spesa | Conad, Coop, Esselunga, Lidl, macelleria |
| Shopping | Amazon, Zalando, IKEA, Gutteridge, 20+ patterns |
| Viaggi | Booking, Airbnb, hotel, Trainline, bagno (beach), bowling, cinema |
| Trasporti | Trenitalia, Italo, Uber, Telepass, parcheggio, benzina |
| Gatti | Arcaplanet, Zooplus, veterinario, Arcacat |
| Psicologo | Unobravo, Serenis |
| Palestra | 21 Lab, McFit, Virgin Active |

## Database Schema (v4.0)

```sql
-- Core tables (existing)
categories(id, name, icon, color)
transactions(id, date, description, amount, category_id, bank, account_type, type, balance, is_recurring, recurring_expense_id)
budgets(id, category_id, amount, month, source, auto_generated)
user_profile(id, income_type, monthly_net_income, risk_tolerance, financial_knowledge, coaching_style)
debts(id, name, type, original_amount, current_balance, interest_rate, monthly_payment, payment_day, start_date, is_active)
goals(id, name, type, target_amount, current_amount, priority, status, target_date)
insights(id, type, category, severity, title, message, action_text, is_read, is_dismissed)
kpi_history(id, month, net_worth, total_debt, savings_rate, dti_ratio, emergency_fund_months)
chat_history(id, session_id, role, content, tokens_used)

-- New v4.0 tables
decisions(id, decision_date, type, category_id, debt_id, recurring_expense_id, amount, description, status, expected_impact_monthly, expected_impact_payoff_days, actual_impact_monthly, actual_impact_verified, verification_date, insight_id)

debt_monthly_plans(id, month, debt_id, planned_payment, extra_payment, actual_payment, order_in_strategy, strategy_type, projected_payoff_date, status)

recurring_expenses(id, pattern_name, category_id, frequency, avg_amount, last_amount, trend_percent, first_occurrence, last_occurrence, occurrence_count, provider, is_essential, is_active, optimization_status, optimization_suggestion, estimated_savings_monthly, confidence_score)

transaction_recurring_links(transaction_id, recurring_expense_id, match_confidence)

daily_actions(id, action_date, priority, title, description, action_type, impact_type, estimated_impact_monthly, estimated_impact_payoff_days, status, completed_at, decision_id, insight_id, recurring_expense_id, debt_id, category_id)

baseline_snapshots(id, snapshot_month, category_id, avg_spending_3mo, avg_income_3mo, avg_savings_3mo, projected_payoff_months, projected_payoff_date)
```

## Design System

Mobile-first dark theme with emerald green (#10B981) accent.

**Colors** (`src/styles.py`):
- Background: #0A0A0A (primary), #141414 (cards), #1E1E1E (tertiary)
- Text: #FAFAFA (primary), #A1A1AA (secondary), #71717A (muted)
- Semantic: income (#22C55E), expense (#EF4444), warning (#F59E0B), accent (#10B981)

**Layout**: Centered, collapsed sidebar, fixed bottom tab navigation.

## Key Patterns

- **Session state**: `active_tab`, `chat_messages`, `money_subtab`
- **Data loading**: `load_dashboard_data()` cached function
- **Custom components**: HTML via `st.markdown(unsafe_allow_html=True)`
- **Amount convention**: Positive = income, Negative = expense
- **KPI fallback**: Uses `user_profile.monthly_net_income` when transaction income < 50% of expected
- **Financial phases**: "Debt Payoff" or "Wealth Building"

## Financial Health Score

Calculated in `analytics.py:calculate_financial_health_score()`:
- Savings Rate (25 pts): 20%+ = 25, 10% = 15, 0% = 0
- DTI Ratio (25 pts): <20% = 25, <36% = 15, >50% = 0
- Emergency Fund (25 pts): 6+ months = 25, 3 = 15, 0 = 0
- Net Worth Trend (25 pts): Positive = 25, Flat = 10, Negative = 0

Grades: A (80+), B (65+), C (50+), D (35+), F (<35)

## Adding New Features

### New Categorization Rules
Edit `src/ai/categorizer.py` - add patterns to appropriate `*_PATTERNS` list.

### New Database Tables
1. Add CREATE TABLE to SCHEMA_SQL in `database.py`
2. Add CRUD functions following existing patterns
3. Optionally add repository class in `src/repositories/`

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
│   │   ├── categorizer.py    # Transaction categorization (100+ patterns)
│   │   ├── advisor.py        # AI coach (Opus 4.5)
│   │   ├── insight_engine.py # Proactive insights
│   │   ├── action_planner.py # Daily action generation
│   │   ├── recurring_optimizer.py # Recurring expense optimization
│   │   └── reporter.py       # Monthly reports (Sonnet)
│   ├── core_finance/
│   │   ├── baseline.py       # Baseline calculator
│   │   ├── debt_planner.py   # Debt payment planning
│   │   ├── budget_generator.py # Auto budget generation
│   │   └── replanner.py      # Monthly re-planning
│   ├── repositories/
│   │   ├── base.py           # Abstract base
│   │   ├── transaction_repository.py
│   │   ├── debt_repository.py
│   │   ├── budget_repository.py
│   │   ├── recurring_repository.py
│   │   ├── decision_repository.py
│   │   ├── action_repository.py
│   │   └── baseline_repository.py
│   └── parsers/
│       ├── revolut.py        # Revolut CSV parser
│       └── illimity.py       # Illimity XLSX parser
└── misc/
    └── pages_backup_v2/      # Old multi-page structure (archived)
```
