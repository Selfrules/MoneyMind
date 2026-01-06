# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Mission

> **MoneyMind accompagna Mattia verso la libertà finanziaria** attraverso un consulente AI esperto che analizza, pianifica e guida con azioni concrete quotidiane.

**Le 4 Fasi verso la Libertà Finanziaria**:
1. **Diagnosi** - Fotografare situazione attuale (KPI, health score, categorizzazione)
2. **Ottimizzazione (0-90g)** - Liberare margine, quick wins, taglio spese
3. **Sicurezza (3-24m)** - Stabilità: debiti a 0, fondo emergenza 3-6 mesi
4. **Crescita (2+ anni)** - Costruire patrimonio e rendite passive (FIRE)

**KPI Non Negoziabili**:
- Risparmio mensile: aumento vs baseline 3 mesi precedenti
- Data uscita debiti: riduzione tempo vs "scenario continuo così"

Per dettagli completi: [docs/MISSION.md](docs/MISSION.md)

---

## Documentation Links

| Document | Purpose |
|----------|---------|
| [docs/MISSION.md](docs/MISSION.md) | Mission, 4 fasi, KPI target |
| [docs/GAP_ANALYSIS.md](docs/GAP_ANALYSIS.md) | Analisi gap attuali vs missione |
| [docs/architecture.md](docs/architecture.md) | System design, data flow diagrams, component interactions |
| [docs/tech_stack.md](docs/tech_stack.md) | Technology choices and rationale |
| [docs/project_status.md](docs/project_status.md) | Current state, backlog, where we left off |
| [docs/changelog.md](docs/changelog.md) | Version history (milestone releases) |
| [docs/lessons_learned.md](docs/lessons_learned.md) | Best practices discovered |

---

## Project Overview

MoneyMind v7.0 is an AI-First, Mobile-Native, Freedom-Focused personal finance coach. It transforms from a passive tracker to a **directive assistant** that actively helps users reduce debt payoff time and increase monthly savings through concrete daily actions.

**Architecture**: Next.js 15 frontend + FastAPI backend + existing Python business logic

**Key v7.0 Features**:
- Personalized benchmarks (based on YOUR 3-month average, not hardcoded values)
- Auto-detection of recurring expenses with confidence scoring
- Fixed vs Discretionary expense classification with daily budget remaining
- Enhanced subscription audit with recurring_type (subscription/financing/essential/service)

## Development Commands

```bash
# Start Backend (FastAPI on port 8001)
cd backend && uvicorn app.main:app --port 8001 --reload

# Start Frontend (Next.js on port 3000)
cd frontend && npm run dev

# Install Backend dependencies
pip install -r requirements.txt
pip install fastapi uvicorn pydantic-settings

# Install Frontend dependencies
cd frontend && npm install

# Legacy Streamlit (deprecato, solo per riferimento)
streamlit run app.py
```

## Environment Variables

Create a `.env` file with:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Architecture (v7.0)

### Frontend + Backend Separation

```
┌─────────────────────────────┐     REST API     ┌─────────────────────────────┐
│     FRONTEND (Next.js)      │ ───────────────► │     BACKEND (FastAPI)       │
│  TypeScript + React Query   │ ◄─────────────── │  Python + Pydantic          │
│  Tailwind CSS + shadcn/ui   │                  │  Imports from src/          │
│  localhost:3000             │                  │  localhost:8001             │
└─────────────────────────────┘                  └─────────────────────────────┘
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard` | KPIs, health score, month summary |
| GET | `/api/actions/today` | Daily actions (prioritized) |
| POST | `/api/actions/{id}/complete` | Mark action complete |
| GET | `/api/insights` | Active insights |
| GET | `/api/transactions` | Transactions with filters |
| GET | `/api/budgets/{month}` | Monthly budgets by category |
| GET | `/api/budgets/fixed-discretionary` | Fixed vs Discretionary budget breakdown (v7.0) |
| GET | `/api/report/full` | Full financial report |
| POST | `/api/chat` | AI coach chat (SSE streaming) |

### Frontend Structure

```
frontend/src/
├── app/                  # Next.js App Router
│   ├── page.tsx          # Home tab
│   ├── money/page.tsx    # Money tab
│   ├── coach/page.tsx    # Coach tab
│   ├── goals/page.tsx    # Goals tab
│   └── profile/page.tsx  # Profile tab
├── components/
│   ├── ui/               # shadcn components
│   ├── dashboard/        # Home tab components
│   │   ├── freedom-score.tsx
│   │   ├── kpi-cards.tsx
│   │   ├── daily-actions.tsx
│   │   └── month-summary.tsx
│   └── bottom-nav.tsx    # Tab navigation
├── hooks/
│   └── use-dashboard.ts  # React Query hooks
└── lib/
    ├── api.ts            # API client
    └── api-types.ts      # TypeScript interfaces
```

### Backend Structure

```
backend/app/
├── main.py               # FastAPI entry point
├── core/
│   └── config.py         # Pydantic Settings
├── api/
│   ├── deps.py           # Dependency injection (DB)
│   └── routes/
│       ├── dashboard.py
│       ├── actions.py
│       └── insights.py
└── schemas/
    ├── dashboard.py      # Response models
    ├── actions.py
    └── insights.py
```

### Core Python Modules (`src/`)

#### Database Layer
- `database.py` - SQLite with v4.0 schema. Context manager pattern (`get_db_context()`). 21 Italian categories.

#### Analytics & Finance Engine (`src/core_finance/`)
- `baseline.py` - 3-month baseline calculator
- `debt_planner.py` - Avalanche/Snowball payment plans
- `budget_generator.py` - Auto-generate budgets from debt plan
- `replanner.py` - Monthly re-planning engine
- `budget_classifier.py` - Fixed vs Discretionary expense classification (v7.0)
- `recurring_detector.py` - Auto-detection of recurring expenses (v7.0)
- `report_analyzer.py` - Full report with personalized benchmarks (v7.0)

#### Repository Pattern (`src/repositories/`)
- `base.py` - Abstract repository base class
- `transaction_repository.py`, `debt_repository.py`, `budget_repository.py`
- `recurring_repository.py`, `decision_repository.py`, `action_repository.py`

#### AI Layer (`src/ai/`)
- `categorizer.py` - Hybrid categorization (100+ patterns, 99.9% accuracy)
- `advisor.py` - Financial coach (Claude Opus 4.5)
- `insight_engine.py` - Proactive insights generation
- `action_planner.py` - Daily action generation
- `recurring_optimizer.py` - Recurring expense optimization

#### Bank Parsers (`src/parsers/`)
- `revolut.py` - Italian CSV format
- `illimity.py` - XLSX exports

## Design System

Mobile-first dark theme with emerald green (#10B981) accent.

**Colors** (defined in `frontend/src/app/globals.css`):
- Background: #0A0A0A (primary), #141414 (cards), #1E1E1E (tertiary)
- Text: #FAFAFA (primary), #A1A1AA (secondary), #71717A (muted)
- Semantic: income (#22C55E), expense (#EF4444), warning (#F59E0B), accent (#10B981)

**Components**: shadcn/ui (button, card, badge, progress, tabs)

## Key Patterns

### Frontend
- **State Management**: React Query with `useQuery` hooks
- **API Client**: Fetch-based in `lib/api.ts`
- **Type Safety**: TypeScript interfaces in `lib/api-types.ts`
- **Mobile-first**: Max-width 448px, bottom tab navigation

### Backend
- **Dependency Injection**: `get_db` in `api/deps.py`
- **Response Models**: Pydantic schemas in `schemas/`
- **Business Logic**: Import from `src/` (analytics, repositories, AI)

### Data Conventions
- **Amount convention**: Positive = income, Negative = expense
- **Financial phases**: "Debt Payoff" or "Wealth Building"
- **Health Score**: A (80+), B (65+), C (50+), D (35+), F (<35)

## Adding New Features

### New API Endpoint
1. Create Pydantic schema in `backend/app/schemas/`
2. Create route in `backend/app/api/routes/`
3. Register router in `backend/app/main.py`
4. Add TypeScript interface in `frontend/src/lib/api-types.ts`
5. Create React Query hook in `frontend/src/hooks/`

### New Frontend Component
1. Create component in `frontend/src/components/`
2. Import shadcn/ui primitives from `components/ui/`
3. Use React Query hook for data fetching

### New Categorization Rules
Edit `src/ai/categorizer.py` - add patterns to appropriate `*_PATTERNS` list.

### New Database Tables
1. Add CREATE TABLE to SCHEMA_SQL in `database.py`
2. Add CRUD functions following existing patterns
3. Add repository class in `src/repositories/`

## Categorization Rules (`src/ai/categorizer.py`)

**100+ patterns organized by category:**

| Category | Key Patterns |
|----------|-------------|
| Risparmi Automatici | `accredita.*risparmio`, Revolut roundups |
| Stipendio | `accredito competenze`, `accredito mens` |
| Utenze | Octopus, Hera, Iren, Enel, TIM, Vodafone, Iliad |
| Finanziamenti | Agos, Findomestic, `personal loan`, `paga in 3` |
| Abbonamenti | Netflix, Spotify, GitHub, ChatGPT, Notion, Whoop |
| Ristoranti | JustEat, Deliveroo, pizzeria, trattoria, 35+ patterns |
| Caffe | `\bbar\b`, gelateria, pasticceria, panificio |
| Spesa | Conad, Coop, Esselunga, Lidl, macelleria |
| Shopping | Amazon, Zalando, IKEA, Gutteridge |
| Viaggi | Booking, Airbnb, hotel, Trainline |
| Trasporti | Trenitalia, Italo, Uber, Telepass, benzina |
| Gatti | Arcaplanet, Zooplus, veterinario |
| Intrattenimento | cinema, teatro, concerti, eventi |
| Regali | regalo, gift, present |
| Contanti | ATM, prelievo, bancomat |

## Expense Classification (v7.0)

**Fixed Expenses** (must pay):
- Affitto, Utenze, Finanziamenti, Salute, Cura Personale, Trasporti, Spesa, Gatti, Contanti

**Discretionary Expenses** (can reduce):
- Ristoranti, Caffe, Shopping, Abbonamenti, Viaggi, Intrattenimento, Regali

**Recurring Types**:
- `subscription` - Netflix, Spotify (easily cancellable)
- `financing` - Agos, loans (contract locked)
- `essential` - Utilities, rent (necessary)
- `service` - Cleaning, maintenance (regular service)

## Database Schema (v4.0)

See `src/database.py` for complete schema. Key tables:
- `transactions` - Normalized transactions from all banks
- `categories` - 21 categories with icons and colors
- `budgets` - Monthly budgets by category
- `debts` - Active debts with rates and plans
- `daily_actions` - AI-generated daily tasks
- `insights` - Proactive insights with severity
- `recurring_expenses` - Pattern-detected recurring expenses

## File Organization

See [docs/architecture.md](docs/architecture.md) for complete folder structure and component interactions.
