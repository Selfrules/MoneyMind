# Architettura MoneyMind v5.0

> **Mission**: Accompagnare Mattia verso la libertà finanziaria attraverso le 4 fasi: Diagnosi → Ottimizzazione → Sicurezza → Crescita
>
> Per dettagli completi: [MISSION.md](MISSION.md) | [GAP_ANALYSIS.md](GAP_ANALYSIS.md)

---

## Copertura Missione per Fase

| Fase | Coverage | Moduli Esistenti | Gap Critici |
|------|----------|------------------|-------------|
| **Diagnosi** | 40% | KPI, health score, categorizer, baseline | X-Ray dashboard, onboarding, debt composition |
| **Ottimizzazione** | 50% | action_planner, insight_engine, recurring_optimizer | Quick wins, impact calculator, money flow |
| **Sicurezza** | 65% | debt_planner, budget_generator, replanner | Journey map, emergency planner, what-if |
| **Crescita** | 10% | KPI history | FIRE calculator, post-debt plan, investment guide |

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 15 + React 19)                 │
│              TypeScript + Tailwind CSS v4 + shadcn/ui               │
│                        React Query for state                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │   Home   │ │  Money   │ │  Coach   │ │  Goals   │ │ Profile  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ REST API + SSE (streaming)
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI + Python)                     │
│                   Pydantic schemas + OpenAPI auto                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  /api/dash   │  │ /api/actions │  │  /api/chat   │  ...          │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   ANALYTICS   │     │    AI LAYER     │     │  CORE FINANCE   │
│ (analytics.py)│     │    (src/ai/)    │     │(src/core_finance)│
│               │     │                 │     │                 │
│ - KPIs        │     │ - categorizer   │     │ - baseline      │
│ - Health Score│     │ - advisor       │     │ - debt_planner  │
│ - Debt Calc   │     │ - insight_engine│     │ - budget_gen    │
│               │     │ - action_planner│     │ - replanner     │
│               │     │ - recurring_opt │     │                 │
└───────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                                ▼
                ┌───────────────────────────┐
                │     REPOSITORY LAYER      │
                │    (src/repositories/)    │
                │                           │
                │ - transaction_repository  │
                │ - debt_repository         │
                │ - budget_repository       │
                │ - recurring_repository    │
                │ - decision_repository     │
                │ - action_repository       │
                │ - baseline_repository     │
                └─────────────┬─────────────┘
                              │
                              ▼
                ┌───────────────────────────┐
                │      DATABASE LAYER       │
                │    (src/database.py)      │
                │                           │
                │   SQLite (moneymind.db)   │
                └───────────────────────────┘
```

## Legacy UI (Streamlit - deprecata)

```
┌─────────────────────────────────────────┐
│           STREAMLIT UI (app.py)         │
│             [DEPRECATA v5.0]            │
│  Mantenuta per compatibilità durante    │
│     la migrazione al nuovo frontend     │
└─────────────────────────────────────────┘
```

## Struttura Cartelle

```
MoneyMind/
├── frontend/                 # Next.js 15 application
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   │   ├── page.tsx      # Home tab
│   │   │   ├── money/        # Money tab
│   │   │   ├── coach/        # Coach tab (chat)
│   │   │   ├── goals/        # Goals tab
│   │   │   └── profile/      # Profile tab
│   │   ├── components/
│   │   │   ├── ui/           # shadcn components
│   │   │   ├── dashboard/    # Home tab components
│   │   │   ├── money/        # Money tab components
│   │   │   ├── coach/        # Chat components
│   │   │   └── bottom-nav.tsx
│   │   ├── hooks/            # React Query hooks
│   │   └── lib/              # API client, utils
│   ├── package.json
│   └── tailwind.config.ts
│
├── backend/                  # FastAPI application
│   └── app/
│       ├── main.py           # Entry point, CORS, routers
│       ├── core/
│       │   └── config.py     # Pydantic Settings
│       ├── api/
│       │   ├── deps.py       # Dependency injection (DB)
│       │   └── routes/       # API endpoints
│       │       ├── dashboard.py
│       │       ├── actions.py
│       │       ├── insights.py
│       │       ├── transactions.py
│       │       ├── budgets.py
│       │       └── chat.py
│       ├── schemas/          # Pydantic models
│       └── services/         # Business logic adapters
│
├── app.py                    # [LEGACY] Streamlit entry point
├── src/
│   ├── database.py           # Schema SQLite v4.0 + CRUD functions
│   ├── analytics.py          # KPI calculation, health score
│   ├── styles.py             # [LEGACY] Streamlit design system
│   ├── utils.py              # Helper functions
│   │
│   ├── ai/                   # Claude AI integration
│   │   ├── categorizer.py    # Hybrid categorization (100+ patterns)
│   │   ├── advisor.py        # Financial coach (Opus 4.5)
│   │   ├── insight_engine.py # Proactive insights generation
│   │   ├── action_planner.py # Daily actions (Full Auto mode)
│   │   ├── recurring_optimizer.py # Recurring expense suggestions
│   │   └── reporter.py       # Monthly reports (Sonnet)
│   │
│   ├── core_finance/         # Business logic (pure functions)
│   │   ├── baseline.py       # 3-month baseline calculator
│   │   ├── debt_planner.py   # Avalanche/Snowball payment plans
│   │   ├── budget_generator.py # Auto-budget from debt plan
│   │   └── replanner.py      # Monthly re-planning engine
│   │
│   ├── repositories/         # Data access layer
│   │   ├── base.py           # Abstract repository base
│   │   └── *_repository.py   # Entity repositories
│   │
│   └── parsers/              # Bank data importers
│       ├── revolut.py
│       └── illimity.py
│
├── data/
│   └── moneymind.db          # SQLite database file
│
├── docs/                     # Project documentation
│   ├── architecture.md       # This file
│   ├── tech_stack.md
│   ├── project_status.md
│   ├── changelog.md
│   └── lessons_learned.md
│
└── misc/                     # Legacy/reference docs
```

## API Endpoints

### Core Endpoints (Implementati)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard` | KPIs, health score, month summary |
| GET | `/api/actions/today` | Daily actions (1-3 prioritized) |
| POST | `/api/actions/{id}/complete` | Mark action complete |
| GET | `/api/insights` | Active insights |
| POST | `/api/insights/{id}/read` | Mark insight as read |

### Money Tab Endpoints (In Progress)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/transactions` | Paginated list with filters |
| GET | `/api/budgets/{month}` | Monthly budget by category |
| GET | `/api/recurring` | Recurring expenses |
| GET | `/api/trends` | 6-month trend data |

### Coach Tab Endpoints (Planned)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/chat/history` | Chat history |
| POST | `/api/chat` | Send message (SSE streaming) |
| DELETE | `/api/chat/session` | Start new session |

### Goals/Profile Endpoints (Planned)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/debts` | Debt list |
| GET | `/api/goals` | Financial goals |
| GET | `/api/profile` | User profile |
| POST | `/api/transactions/import` | Import CSV/XLSX |

## Flusso Dati

### 1. Frontend → Backend → Database
```
React Component → useQuery hook → fetch(/api/...) → FastAPI route → Repository → SQLite
```

### 2. Import Transazioni
```
CSV/XLSX Upload → /api/transactions/import → Parser → Deduplication (SHA256) → DB
```

### 3. Categorizzazione
```
Transazione → Rule-based patterns (95% hit) → [Se fallisce] → Claude Haiku → DB
```

### 4. Analytics Pipeline
```
DB Transactions → analytics.py → KPIs, Health Score → /api/dashboard → React UI
```

### 5. AI Insights
```
Financial Snapshot → insight_engine.py → Prioritized Insights → Daily Actions → UI
```

### 6. Debt Planning
```
Debts + Income → debt_planner.py → Monthly Plan → budget_generator.py → Budget
```

### 7. Coach Chat (SSE Streaming)
```
User message → POST /api/chat → advisor.py (Opus 4.5) → SSE stream → React UI
```

## Pattern Architetturali

### Repository Pattern
Separa la logica di accesso dati dalla business logic. Ogni entità ha un repository dedicato che astrae le query SQL.

```python
# Esempio d'uso
repo = TransactionRepository()
transactions = repo.get_by_category(category_id, month)
```

**Beneficio**: Permette futura migrazione da SQLite a PostgreSQL/API senza modificare la business logic.

### Service Layer (core_finance/)
Contiene pure functions che calcolano senza side effects. Separato da UI e database.

```python
# Esempio
from core_finance.baseline import BaselineCalculator
calc = BaselineCalculator()
baseline = calc.calculate_3mo_baseline("2026-01")
```

**Beneficio**: Testabile, riutilizzabile, potenzialmente esponibile come API.

### Hybrid AI Strategy
Combina rule-based patterns (veloce, economico) con Claude AI (fallback intelligente).

```python
# categorizer.py flow
1. Match against 100+ regex patterns → 95% success rate
2. If no match → Claude Haiku batch categorization → 5% remaining
```

**Beneficio**: Costi API ridotti del ~95%, latenza minimizzata.

## Database Schema (v4.0)

Tabelle principali:
- `transactions` - Transazioni normalizzate da tutte le banche
- `categories` - 19+ categorie con icone e colori
- `budgets` - Budget mensili per categoria (manual + auto-generated)
- `debts` - Debiti attivi con tassi e piani
- `decisions` - Tracking decisioni utente e impatto
- `daily_actions` - Task giornalieri generati da AI
- `recurring_expenses` - Pattern spese ricorrenti
- `baseline_snapshots` - Medie storiche per comparazione
- `debt_monthly_plans` - Piano pagamenti mensile per debito
- `insights` - Insight generati con severity e status

Per schema completo SQL: vedi `src/database.py`

## Frontend Architecture (Next.js)

### Tech Stack
- **Framework**: Next.js 15 con App Router
- **React**: v19 (React Server Components support)
- **Styling**: Tailwind CSS v4 + shadcn/ui components
- **State**: React Query (TanStack Query v5)
- **Icons**: Lucide React
- **TypeScript**: Strict mode

### Design System
- **Theme**: Dark theme (#0A0A0A background)
- **Accent**: Emerald green (#10B981)
- **Mobile-first**: Max-width 448px, bottom tab navigation
- **Components**: Card-based UI, progress bars, badges

### Component Structure
```
components/
├── ui/                    # shadcn base components
│   ├── button.tsx
│   ├── card.tsx
│   ├── badge.tsx
│   └── progress.tsx
├── dashboard/             # Home tab
│   ├── freedom-score.tsx  # Health score circular display
│   ├── kpi-cards.tsx      # Grid of 4 KPI cards
│   ├── daily-actions.tsx  # Action items with complete/skip
│   └── month-summary.tsx  # Income/expenses/savings
├── money/                 # Money tab (in progress)
│   ├── transactions-list.tsx
│   ├── budget-progress.tsx
│   └── trend-chart.tsx
├── coach/                 # Coach tab (planned)
│   ├── chat-messages.tsx
│   └── chat-input.tsx
└── bottom-nav.tsx         # 5-tab navigation
```

### Data Flow
```
useQuery hook → API fetch → Backend → Response → UI State → Render
     │                                              │
     └─── Automatic cache invalidation ────────────┘
```

## Interazione Componenti

### Home Tab Flow
```
useDashboard() + useTodayActions() →
  ├── FreedomScore (health_score)
  ├── MonthSummary (month_summary)
  ├── DailyActions (actions)
  └── KPICards (kpis)
```

### Money Tab Flow (In Progress)
```
Tab selection →
  ├── Transactions: useTransactions() → TransactionsList
  ├── Budget: useBudgets(month) → BudgetProgress
  ├── Trends: useTrends() → TrendChart
  └── Ricorrenti: useRecurring() → RecurringList
```

### Coach Tab Flow (Planned)
```
User message →
  useMutation(/api/chat) →
    SSE stream →
      Real-time message updates
```

### Goals Tab Flow (Planned)
```
useDebts() + useGoals() →
  ├── DebtFreedomCard (total debt, payoff date)
  ├── DebtList (ordered by strategy)
  └── Timeline (milestones)
```

---

## Componenti Target (da GAP_ANALYSIS.md)

### Sprint 1-2: Diagnosi + Ottimizzazione (P0)

| Componente | Descrizione | Moduli Impattati |
|------------|-------------|------------------|
| **Financial X-Ray Dashboard** | Report diagnosi one-page | `analytics.py`, nuovo endpoint `/api/xray` |
| **Onboarding Wizard** | Questionario 5-step | Nuovo modulo `onboarding.py`, frontend wizard |
| **Quick Wins Detector** | Scan abbonamenti ottimizzabili | `recurring_optimizer.py`, nuovo endpoint |
| **Impact Calculator** | "Taglia €X → accelera payoff Y" | `debt_planner.py`, frontend component |
| **Money Flow Breakdown** | Essenziali/Debiti/Wants/Disponibile | `analytics.py`, Sankey diagram |

### Sprint 3: Sicurezza (P1)

| Componente | Descrizione | Moduli Impattati |
|------------|-------------|------------------|
| **Journey Map** | Visualizzazione 3 fasi con milestone | Nuovo modulo `journey.py`, timeline UI |
| **Emergency Fund Planner** | Piano accelerazione con target | `goals.py`, nuovo endpoint |
| **What-If Scenarios** | Simulatore job loss, bonus | Nuovo modulo `scenarios.py` |
| **Risk Dashboard** | Alert metriche in peggioramento | `insight_engine.py` enhancement |

### Sprint 4-5: Crescita + Coaching (P2)

| Componente | Descrizione | Moduli Impattati |
|------------|-------------|------------------|
| **FIRE Calculator** | Calcolo data Financial Independence | Nuovo modulo `fire_calculator.py` |
| **Post-Debt Plan** | Redirect €550/mese liberati | `debt_planner.py` enhancement |
| **Investment Basics** | Guida ETF/PAC Italia | Contenuto statico + AI advisor |
| **Advisor Persona** | Coaching personalizzato per fase | `advisor.py` enhancement |
| **Monthly Letter** | Narrativa "il mese di Mattia" | `reporter.py` enhancement |

---

## Architettura Target

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 15 + React 19)                 │
│              TypeScript + Tailwind CSS v4 + shadcn/ui               │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    NEW: COACHING LAYER                        │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │   │
│  │  │ Financial   │ │  Journey    │ │   FIRE      │             │   │
│  │  │ X-Ray       │ │  Map        │ │ Calculator  │             │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │   Home   │ │  Money   │ │  Coach   │ │  Goals   │ │ Profile  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ REST API + SSE
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI + Python)                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                 NEW: MISSION-ORIENTED ENDPOINTS               │   │
│  │  /api/xray    /api/quickwins   /api/journey   /api/fire      │   │
│  │  /api/impact  /api/scenarios   /api/letter                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  /api/dash   │  │ /api/actions │  │  /api/chat   │  ...          │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   ANALYTICS   │     │    AI LAYER     │     │  CORE FINANCE   │
│               │     │    (src/ai/)    │     │(src/core_finance)│
│ + xray.py     │     │ + advisor       │     │ + fire_calc     │
│ + scenarios   │     │   (enhanced)    │     │ + journey       │
│               │     │ + nudges        │     │ + scenarios     │
└───────────────┘     └─────────────────┘     └─────────────────┘
```
