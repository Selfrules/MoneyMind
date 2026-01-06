# Changelog - MoneyMind

Questo file traccia le release milestone del progetto.

---

## v5.1 - 2026-01-06 (Mission Alignment)

**Definizione Missione e Gap Analysis**

Analisi critica dell'app rispetto alla missione di accompagnare Mattia verso la libertà finanziaria attraverso le 4 fasi.

### Nuova Documentazione
- **MISSION.md** - Definizione missione completa con 4 fasi (Diagnosi → Ottimizzazione → Sicurezza → Crescita)
- **GAP_ANALYSIS.md** - Analisi dettagliata gap attuali vs requisiti missione

### Gap Analysis Summary
| Fase | Coverage | Gap Severity |
|------|----------|--------------|
| Diagnosi | 40% | 🔴 Critico |
| Ottimizzazione | 50% | 🔴 Critico |
| Sicurezza | 65% | 🟡 Alto |
| Crescita | 10% | 🔴 Critico |

### Componenti Target Identificati
- **Sprint 1**: Financial X-Ray Dashboard, Onboarding Wizard
- **Sprint 2**: Quick Wins Detector, Impact Calculator
- **Sprint 3**: Journey Map, Emergency Fund Planner
- **Sprint 4**: FIRE Calculator, Post-Debt Plan
- **Sprint 5**: Advisor Persona, Monthly Letter

### Documentazione Aggiornata
- CLAUDE.md con sezione Mission
- architecture.md con architettura target
- project_status.md con gap analysis summary
- todo.md riprioritizzato
- roadmap.md integrato con 4 fasi

---

## v5.0 - 2026-01-06 (In Progress)

**UI Migration: Streamlit → Next.js + FastAPI**

Migrazione completa dell'interfaccia utente da Streamlit a un'architettura moderna con Next.js frontend e FastAPI backend.

### Nuova Architettura
- **Frontend**: Next.js 15 + React 19 + TypeScript
- **Backend**: FastAPI + Pydantic + Uvicorn
- **Styling**: Tailwind CSS v4 + shadcn/ui
- **State**: React Query (TanStack Query v5)

### Backend FastAPI
- Entry point con CORS e router modulari
- Pydantic Settings per configurazione
- Dependency injection per connessione DB
- OpenAPI documentation automatica (`/docs`)

### API Endpoints Implementati
- `GET /api/dashboard` - KPIs, health score, month summary
- `GET /api/actions/today` - Daily actions
- `POST /api/actions/{id}/complete` - Mark action complete
- `GET /api/insights` - Active insights

### Frontend Next.js
- App Router con 5 tab pages
- Design system dark theme (#0A0A0A + emerald #10B981)
- Bottom tab navigation mobile-first
- React Query hooks per API state

### Componenti Home Tab
- `FreedomScore` - Health score con breakdown
- `KPICards` - Grid 4 KPIs (saldo, debito, DTI, patrimonio)
- `DailyActions` - Action items con complete/skip
- `MonthSummary` - Entrate/uscite/risparmio mensile

### In Progress
- Money Tab (transazioni, budget, trend, ricorrenti)
- Goals Tab (debiti, obiettivi, timeline)
- Profile Tab (profilo, report, import)
- Coach Tab (chat AI con SSE streaming)

---

## v4.0 - 2026-01-05

**AI-First Finance Coach**

Trasformazione da tracker passivo ad assistente direttivo che aiuta a ridurre il tempo di uscita dai debiti e aumentare il risparmio mensile.

### Nuove Feature
- Schema database v4.0 con tabelle: `decisions`, `debt_monthly_plans`, `recurring_expenses`, `daily_actions`, `baseline_snapshots`
- Repository pattern completo per tutte le entità
- Core Finance Engine: `baseline.py`, `debt_planner.py`, `budget_generator.py`, `replanner.py`
- AI Layer potenziato: `insight_engine.py`, `action_planner.py`, `recurring_optimizer.py`
- Sistema categorizzazione ibrido con 100+ pattern (99.9% accuracy)

### Categorie Aggiunte
- Intrattenimento
- Regali

### Architettura
- Separazione in layers: UI → Analytics → AI → Core Finance → Repository → Database
- Design preparato per futura migrazione a backend remoto

---

## v1.0 - 2025-01-03

**Release Iniziale**

Dashboard finanziaria personale con import da Revolut e Illimity.

### Feature
- Import CSV Revolut (formato italiano)
- Import XLSX Illimity
- Categorizzazione AI con Claude
- Dashboard con KPIs e grafici
- Budget per categoria
- Report mensile AI

### Tech Stack
- Streamlit
- SQLite
- Claude API
- Pandas + Plotly

---

## Formato Changelog

Ogni release milestone include:
- **Versione**: Numero semantico (major.minor)
- **Data**: Data di completamento
- **Titolo**: Nome descrittivo della release
- **Cambiamenti**: Lista delle modifiche principali raggruppate per area
