# MoneyMind v4.0 - Piano di Implementazione Completo

## Vision
Trasformare MoneyMind da **tracker passivo** a **assistente direttivo** che:
- Riduce attivamente il tempo di uscita dai debiti
- Aumenta il risparmio mensile rispetto alla baseline
- Guida l'utente con **azioni concrete quotidiane**

## KPI di Outcome (Non Negoziabili)
1. **Risparmio medio mensile**: +X €/mese vs baseline (3 mesi precedenti)
2. **Data uscita debiti**: Riduzione tempo stimato vs "scenario continuo così"

---

## Configurazione Scelta
- **Daily Actions**: Full Auto (AI genera 1-3 task/giorno automaticamente)
- **AI Strategy**: Claude Opus Premium (~$10/mese) con extended thinking
- **Optimization**: Smart Suggestions con alternative concrete e stime risparmio
- **Notifications**: In-app badge su Home tab con contatore azioni pending
- **Implementation Strategy**: Database First (schema completo → logica → UI)

---

## EPICA 1: Schema Database & Repository Pattern
**Obiettivo**: Fondamenta dati per tutte le feature della roadmap

### Task 1.1: Nuove Tabelle Core
**Files**: `src/database.py`

```sql
-- Decisioni utente con tracking impatto
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_date DATE NOT NULL,
    type TEXT NOT NULL,  -- 'taglio_spesa', 'aumento_rata', 'cambio_fornitore', 'cancella_abbonamento'
    category_id INTEGER,
    debt_id INTEGER,
    recurring_expense_id INTEGER,
    amount REAL,
    description TEXT,
    status TEXT DEFAULT 'pending',  -- 'pending', 'accepted', 'rejected', 'postponed', 'completed'
    expected_impact_monthly REAL,
    expected_impact_payoff_days INTEGER,
    actual_impact_monthly REAL,
    actual_impact_verified BOOLEAN DEFAULT 0,
    verification_date DATE,
    insight_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (debt_id) REFERENCES debts(id),
    FOREIGN KEY (insight_id) REFERENCES insights(id)
);

-- Piano debiti mensile
CREATE TABLE debt_monthly_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL,
    debt_id INTEGER NOT NULL,
    planned_payment REAL NOT NULL,
    extra_payment REAL DEFAULT 0,
    actual_payment REAL,
    order_in_strategy INTEGER,
    strategy_type TEXT DEFAULT 'avalanche',
    projected_payoff_date DATE,
    status TEXT DEFAULT 'planned',  -- 'planned', 'on_track', 'behind', 'ahead', 'completed'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (debt_id) REFERENCES debts(id),
    UNIQUE(month, debt_id)
);

-- Spese ricorrenti identificate
CREATE TABLE recurring_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    frequency TEXT NOT NULL,  -- 'monthly', 'quarterly', 'annual'
    avg_amount REAL,
    last_amount REAL,
    trend_percent REAL,  -- % change over 6 months
    first_occurrence DATE,
    last_occurrence DATE,
    occurrence_count INTEGER DEFAULT 0,
    provider TEXT,
    is_essential BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    optimization_status TEXT DEFAULT 'not_reviewed',
    optimization_suggestion TEXT,
    estimated_savings_monthly REAL,
    confidence_score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Link transazioni → ricorrenze
CREATE TABLE transaction_recurring_links (
    transaction_id TEXT NOT NULL,
    recurring_expense_id INTEGER NOT NULL,
    match_confidence REAL,
    PRIMARY KEY (transaction_id, recurring_expense_id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (recurring_expense_id) REFERENCES recurring_expenses(id)
);

-- Daily actions (task giornalieri)
CREATE TABLE daily_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_date DATE NOT NULL,
    priority INTEGER DEFAULT 1,
    title TEXT NOT NULL,
    description TEXT,
    action_type TEXT,  -- 'review_subscription', 'increase_payment', 'cut_category', 'confirm_budget'
    impact_type TEXT,  -- 'savings', 'payoff_acceleration', 'budget_control'
    estimated_impact_monthly REAL,
    estimated_impact_payoff_days INTEGER,
    status TEXT DEFAULT 'pending',
    completed_at DATETIME,
    decision_id INTEGER,
    insight_id INTEGER,
    recurring_expense_id INTEGER,
    debt_id INTEGER,
    category_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (decision_id) REFERENCES decisions(id),
    FOREIGN KEY (insight_id) REFERENCES insights(id)
);

-- Baseline mensili per comparazione
CREATE TABLE baseline_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_month TEXT NOT NULL,
    category_id INTEGER,
    avg_spending_3mo REAL,
    avg_income_3mo REAL,
    avg_savings_3mo REAL,
    projected_payoff_months INTEGER,
    projected_payoff_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(snapshot_month, category_id)
);

-- Indici critici
CREATE INDEX idx_decisions_status ON decisions(status);
CREATE INDEX idx_decisions_date ON decisions(decision_date);
CREATE INDEX idx_debt_plans_month ON debt_monthly_plans(month);
CREATE INDEX idx_recurring_active ON recurring_expenses(is_active);
CREATE INDEX idx_daily_actions_date ON daily_actions(action_date, status);
CREATE INDEX idx_baseline_month ON baseline_snapshots(snapshot_month);
```

**Estensioni tabelle esistenti**:
```sql
ALTER TABLE budgets ADD COLUMN source TEXT DEFAULT 'manual';
ALTER TABLE budgets ADD COLUMN auto_generated BOOLEAN DEFAULT 0;
ALTER TABLE transactions ADD COLUMN is_recurring BOOLEAN DEFAULT 0;
ALTER TABLE transactions ADD COLUMN recurring_expense_id INTEGER;
```

### Task 1.2: CRUD Functions per Nuove Tabelle
**Files**: `src/database.py`

Funzioni da implementare:
- `add_decision()`, `update_decision()`, `get_decisions()`, `get_pending_decisions()`
- `create_debt_monthly_plan()`, `update_plan_actual()`, `get_plan_for_month()`
- `add_recurring_expense()`, `update_recurring()`, `get_active_recurring()`
- `link_transaction_to_recurring()`, `get_transactions_for_recurring()`
- `create_daily_action()`, `complete_action()`, `get_today_actions()`
- `save_baseline_snapshot()`, `get_baseline_for_month()`

### Task 1.3: Repository Pattern Layer
**Files**: `src/repositories/__init__.py`, `src/repositories/base.py`, etc.

```
src/repositories/
├── __init__.py
├── base.py                    # Abstract repository base
├── transaction_repository.py  # Transaction domain methods
├── debt_repository.py         # Debt + monthly plans
├── budget_repository.py       # Budget with auto-generation
├── recurring_repository.py    # Recurring expenses
├── decision_repository.py     # Decision lifecycle
└── action_repository.py       # Daily actions
```

---

## EPICA 2: Core Finance Engine
**Obiettivo**: Motore di calcolo per piano debiti, budget auto-generato, baseline

### Task 2.1: Baseline Calculator
**Files**: `src/core_finance/baseline.py`

```python
class BaselineCalculator:
    def calculate_3mo_baseline(self, reference_month: str) -> dict:
        """Calcola medie 3 mesi precedenti per spending/income/savings."""

    def calculate_current_payoff_projection(self) -> dict:
        """Proiezione 'se continuo così' senza interventi."""

    def compare_to_baseline(self, current_month: str) -> dict:
        """Confronta mese corrente vs baseline."""
        # Returns: { better_worse: str, savings_delta: float, payoff_delta_days: int }
```

### Task 2.2: Debt Plan Generator
**Files**: `src/core_finance/debt_planner.py`

```python
class DebtPlanner:
    def generate_monthly_plan(self, month: str, strategy: str = 'avalanche',
                              extra_payment: float = 0) -> list[dict]:
        """Genera piano pagamenti mensile per ogni debito."""

    def calculate_scenario_comparison(self) -> dict:
        """Confronta scenario attuale vs scenario MoneyMind."""
        # Returns: {
        #   current_scenario: { months: int, interest: float, date: str },
        #   moneymind_scenario: { months: int, interest: float, date: str },
        #   months_saved: int, interest_saved: float
        # }

    def get_on_track_status(self, month: str) -> dict:
        """Calcola se on_track / behind / ahead vs piano."""

    def replan_month(self, month: str, actual_spending: dict) -> dict:
        """Ricalcola piano basato su spese effettive."""
```

### Task 2.3: Budget Auto-Generator
**Files**: `src/core_finance/budget_generator.py`

```python
class BudgetGenerator:
    def generate_from_debt_plan(self, month: str, debt_plan: list) -> list[dict]:
        """Genera budget per categoria partendo dal piano debiti."""
        # Priority: 1) Debt payments, 2) Essential spending, 3) 50/30/20 adapted

    def calculate_adjustment_impact(self, category_id: int,
                                    new_amount: float) -> dict:
        """Calcola impatto modifica budget su risparmio e data payoff."""

    def apply_rule_50_30_20_debt_phase(self, income: float,
                                        debt_payments: float) -> dict:
        """Applica regola 50/30/20 adattata per fase Debt Payoff."""
        # 50% needs, 20% wants, 30% savings+debt (instead of standard 50/30/20)
```

### Task 2.4: Recurring Expense Detector
**Files**: `src/core_finance/recurring_detector.py`

```python
class RecurringDetector:
    def detect_patterns(self, transactions: list) -> list[dict]:
        """Identifica pattern ricorrenti (mensili, trimestrali, annuali)."""
        # Algorithm: cluster by description similarity + amount variance + interval

    def extract_provider(self, description: str) -> str:
        """Estrae nome provider da descrizione transazione."""

    def calculate_confidence(self, pattern: dict) -> float:
        """Calcola confidence score del pattern (0-1)."""

    def link_transactions(self, recurring_id: int) -> int:
        """Collega transazioni esistenti al pattern ricorrente."""
```

---

## EPICA 3: AI Layer Potenziato
**Obiettivo**: Insight proattivi, azioni quotidiane, suggerimenti ottimizzazione

### Task 3.1: Insight Engine
**Files**: `src/ai/insight_engine.py`

```python
class InsightEngine:
    """Genera insight proattivi usando Claude Opus 4.5 con extended thinking."""

    def generate_daily_insights(self, snapshot: dict) -> list[dict]:
        """Genera 1-5 insight al giorno basati su anomalie e opportunità."""
        # Types: spending_anomaly, budget_overrun, recurring_opportunity,
        #        debt_acceleration, savings_increase

    def prioritize_insights(self, insights: list) -> list[dict]:
        """Prioritizza per impatto su KPI (risparmio, payoff)."""
        # Limita a max 3-5 attivi per evitare overload cognitivo

    def format_insight_operativo(self, raw_insight: dict) -> dict:
        """Formatta insight con: Problema, Raccomandazione, Azione, Impatto."""
```

### Task 3.2: Action Planner (Full Auto)
**Files**: `src/ai/action_planner.py`

```python
class ActionPlanner:
    """Genera 1-3 azioni quotidiane ad alto impatto automaticamente."""

    def generate_daily_actions(self, date: str = None) -> list[dict]:
        """Genera azioni del giorno basate su insights + stato finanziario."""
        # Uses Claude Opus 4.5 to select and prioritize

    def estimate_action_impact(self, action: dict) -> dict:
        """Stima impatto: €/mese risparmiati, giorni anticipati payoff."""

    def create_action_from_insight(self, insight: dict) -> dict:
        """Converte insight in azione concreta con passi pratici."""
```

### Task 3.3: Recurring Expense Optimizer (Smart Suggestions)
**Files**: `src/ai/recurring_optimizer.py`

```python
class RecurringOptimizer:
    """Suggerisce alternative concrete per ottimizzare spese ricorrenti."""

    def analyze_recurring_expense(self, recurring: dict,
                                   user_context: dict) -> dict:
        """Analizza ricorrenza e genera suggerimenti specifici."""
        # Uses Claude Opus with extended thinking + web search knowledge

    def generate_optimization_strategies(self, recurring: dict) -> list[dict]:
        """Genera strategie: downgrade, switch, cancel, renegotiate."""
        # Examples:
        # - "Downgrade Netflix a Basic: risparmio €8/mese"
        # - "Passa a Iliad 150GB: risparmio €12/mese vs Vodafone"
        # - "Cancella Adobe CC, usa Canva Free: risparmio €24/mese"

    def estimate_savings(self, current: dict, alternative: dict) -> float:
        """Stima risparmio mensile per ogni alternativa."""
```

### Task 3.4: Potenziamento Advisor Esistente
**Files**: `src/ai/advisor.py`

Modifiche:
1. **Connettere al Coach tab** (attualmente disconnesso)
2. **Aggiungere context delle decisioni** passate nel prompt
3. **Tracciare chat_history** nel database
4. **Follow-up su azioni** suggerite precedentemente
5. **Integrare con Daily Actions** per conferme e spiegazioni

---

## EPICA 4: UX Direttiva - Home Tab Riprogettata
**Obiettivo**: Home risponde a 3 domande + Daily Action Plan

### Task 4.1: Nuovi Componenti UI
**Files**: `src/styles.py`

```python
def plan_vs_actual_card(current: dict, baseline: dict, status: str) -> str:
    """Card comparazione: meglio/peggio vs mese scorso + on track status."""
    # Shows: "📈 +€127 vs baseline" or "📉 -€45 vs baseline"
    # Shows: "✅ On Track" or "⚠️ 2 settimane in ritardo"

def daily_action_task(action: dict) -> str:
    """Task checkabile con impatto stimato."""
    # Shows: checkbox + title + "Risparmia €15/mese" badge

def scenario_comparison_mini(current: dict, moneymind: dict) -> str:
    """Mini confronto scenario attuale vs MoneyMind."""
    # Shows: "Oggi: Debt-free Apr 2027" vs "Con MoneyMind: Nov 2026 (-5 mesi)"

def action_impact_badge(impact_monthly: float, impact_days: int) -> str:
    """Badge impatto: €X/mese o X giorni prima."""

def decision_confirmation_modal(action: dict) -> str:
    """Modal conferma decisione con Accept/Reject/Later."""
```

### Task 4.2: Home Tab Ristrutturata
**Files**: `app.py` - `render_home_tab()`

**In-App Badge**: Mostrare badge rosso con numero su tab Home quando ci sono azioni pending non completate.

Nuova struttura Home:
```
┌─────────────────────────────────────┐
│  👋 Ciao Marco!                     │
│  Il tuo percorso verso la libertà   │
├─────────────────────────────────────┤
│  🏆 Freedom Score: 62/100           │
│  ████████░░░░░  "Buon progresso!"   │
├─────────────────────────────────────┤
│  📊 QUESTO MESE VS BASELINE         │
│  ┌───────────┐  ┌───────────┐       │
│  │ +€127     │  │ ✅ On Track│       │
│  │ vs media  │  │ debt plan │       │
│  └───────────┘  └───────────┘       │
├─────────────────────────────────────┤
│  📅 OGGI - 3 Azioni ad Alto Impatto │
│  ☐ Rivedi abbonamento Netflix       │
│    → Risparmia €8/mese              │
│  ☐ Conferma +€20 su debito Agos     │
│    → 12 giorni prima debt-free      │
│  ☐ Controlla spese Ristoranti       │
│    → Budget sforato del 23%         │
├─────────────────────────────────────┤
│  📈 SCENARIO CONFRONTO              │
│  Attuale: Debt-free Apr 2027        │
│  MoneyMind: Nov 2026 (-5 mesi!)     │
│  [Vedi piano completo →]            │
├─────────────────────────────────────┤
│  💡 AI INSIGHT                      │
│  "Ristoranti +65% vs media..."      │
│  [Parla con Coach]                  │
└─────────────────────────────────────┘
```

### Task 4.3: Decision Tracking UI
**Files**: `app.py`

Quando utente completa azione:
1. Mostra modal conferma con Accept/Reject/Later
2. Salva in `decisions` table
3. Mostra feedback immediato ("Ottimo! Tracciamo l'impatto")
4. Aggiorna scenario comparison in tempo reale

---

## EPICA 5: Pillar 3 - Recurring Expenses Tab
**Obiettivo**: Sezione dedicata abbonamenti/utenze con ottimizzazioni

### Task 5.1: Money Tab - Sottotab "Ricorrenti"
**Files**: `app.py` - `render_money_tab()`

Aggiungere 4° sottotab: **📋 Transazioni | 💰 Budget | 📈 Trend | 🔄 Ricorrenti**

### Task 5.2: Recurring Expenses View
**Files**: `app.py` - `render_recurring_subtab()`

```
┌─────────────────────────────────────┐
│  🔄 SPESE RICORRENTI                │
│  Totale: €487/mese (18% reddito)    │
├─────────────────────────────────────┤
│  📱 ABBONAMENTI (€89/mese)          │
│  ┌───────────────────────────────┐  │
│  │ Netflix Premium    €17.99    │  │
│  │ 📈 +€2 vs 6 mesi fa          │  │
│  │ 💡 Downgrade a Basic: -€8    │  │
│  │ [Ottimizza]                  │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ Spotify Family     €17.99    │  │
│  │ → Stabile                    │  │
│  └───────────────────────────────┘  │
├─────────────────────────────────────┤
│  ⚡ UTENZE (€198/mese)              │
│  ┌───────────────────────────────┐  │
│  │ Octopus Energy     €85       │  │
│  │ 📉 -€12 vs 6 mesi fa         │  │
│  │ ✅ Già ottimizzato           │  │
│  └───────────────────────────────┘  │
├─────────────────────────────────────┤
│  🏦 FINANZIAMENTI (€200/mese)       │
│  │ Agos Prestito      €150      │  │
│  │ Illimity Rate      €50       │  │
│  │ [Gestiti in Goals]           │  │
└─────────────────────────────────────┘
```

### Task 5.3: Optimization Action Flow
Quando utente clicca "Ottimizza":
1. Mostra dettaglio ricorrenza con trend 6 mesi
2. AI genera 2-3 strategie concrete
3. Mostra impatto su risparmio e payoff date
4. Accept → crea Decision + Daily Action follow-up
5. Dopo 1-3 mesi: verifica impatto reale vs stimato

---

## EPICA 6: Coach Tab Potenziato
**Obiettivo**: Collegare AI Advisor + memory + decision tracking

### Task 6.1: Connettere Advisor Reale
**Files**: `app.py` - `generate_coach_response()`

Sostituire risposte hardcoded con:
```python
from ai.advisor import get_financial_advice

def generate_coach_response(question: str) -> str:
    context = build_rich_context()  # snapshot + debts + decisions + history
    return get_financial_advice(question, context, session_id)
```

### Task 6.2: Chat History Persistence
**Files**: `app.py`, `src/database.py`

- Salvare ogni messaggio in `chat_history`
- Caricare ultimi 10 messaggi nel context del prompt
- Permettere riferimenti a conversazioni precedenti

### Task 6.3: Decision Integration
Quando Coach suggerisce azione:
- Mostra bottone "Accetta suggerimento"
- Crea automaticamente Decision + Daily Action
- Follow-up nelle conversazioni successive

---

## EPICA 7: Wizard Setup Guidato
**Obiettivo**: Onboarding che raccoglie dati e crea piano iniziale

### Task 7.1: Wizard Flow
**Files**: `app.py` - nuovo `render_wizard()`

Steps:
1. **Benvenuto** - Spiega obiettivi MoneyMind
2. **Reddito** - Entrate mensili nette
3. **Debiti** - Import o inserimento manuale
4. **Spese Essenziali** - Stima minimo necessario
5. **Aggressività** - Quanto vuoi accelerare payoff? (1-5)
6. **Calcolo Baseline** - Mostra situazione attuale
7. **Generazione Piano** - Crea debt plan + budget
8. **Confronto Scenari** - "Senza MoneyMind: X | Con MoneyMind: Y"
9. **Conferma** - Attiva piano

### Task 7.2: Baseline Initialization
Durante wizard:
- Calcola 3-month baseline se ci sono transazioni
- Se no transazioni: usa stime utente
- Salva in `baseline_snapshots`
- Genera primo `debt_monthly_plan`

---

## EPICA 8: Monthly Re-Planning
**Obiettivo**: A fine mese, ricalcola piano basato su realtà

### Task 8.1: Re-Plan Engine
**Files**: `src/core_finance/replanner.py`

```python
class MonthlyReplanner:
    def analyze_month_performance(self, month: str) -> dict:
        """Confronta piano vs actual per ogni categoria e debito."""

    def generate_replan(self, month: str) -> dict:
        """Genera nuovo piano per mese successivo."""
        # Adjusts: budget amounts, debt extra payments, savings targets

    def explain_changes(self, old_plan: dict, new_plan: dict) -> str:
        """Spiega cosa è cambiato e perché (per UI)."""
```

### Task 8.2: Re-Plan UI
**Files**: `app.py`

A inizio mese (o su richiesta):
1. Mostra performance mese precedente
2. Highlight: on track / behind / ahead
3. Mostra proposta nuovo piano
4. Spiega impatti su payoff date
5. Conferma o aggiusta manualmente

---

## EPICA 9: Impact Verification System
**Obiettivo**: Misurare impatto reale delle decisioni

### Task 9.1: Impact Tracker
**Files**: `src/core_finance/impact_tracker.py`

```python
class ImpactTracker:
    def verify_decision_impact(self, decision_id: int) -> dict:
        """Dopo 1-3 mesi, confronta expected vs actual."""

    def generate_impact_stories(self) -> list[dict]:
        """Crea storie motivazionali: 'Cambiando X hai risparmiato Y'."""

    def calculate_cumulative_impact(self) -> dict:
        """Impatto totale di tutte le decisioni completate."""
```

### Task 9.2: Impact Stories UI
Nella Home o Profile:
```
🎉 I TUOI SUCCESSI
┌─────────────────────────────────────┐
│ ✅ Cambio gestore luce (3 mesi fa)  │
│    Risparmiato: €66 (€22/mese)      │
├─────────────────────────────────────┤
│ ✅ Downgrade Netflix (2 mesi fa)    │
│    Risparmiato: €16 (€8/mese)       │
├─────────────────────────────────────┤
│ 📊 TOTALE VERIFICATO: €82           │
│ 🎯 Debt-free anticipato: 18 giorni  │
└─────────────────────────────────────┘
```

---

## EPICA 10: Import & Categorization Restoration
**Obiettivo**: Ripristinare Import tab + categorizzazione AI

### Task 10.1: Import Tab
**Files**: `app.py` - nuovo `render_import_tab()` o in Profile

- Upload CSV/XLSX (Revolut, Illimity)
- Preview transazioni prima di import
- Categorizzazione AI automatica
- Review transazioni incerte (confidence < 0.8)
- Detect recurring patterns post-import

### Task 10.2: Categorization Feedback Loop
Quando utente corregge categoria:
- Salva correzione
- Aggiorna regole locali per pattern simili
- Feedback per migliorare AI prompt

---

## Priorità Implementazione (Database First Strategy)

### Fase 1: Fondamenta Database (Settimana 1-2)
**Obiettivo**: Schema completo prima di qualsiasi logica o UI

**Settimana 1**:
1. Task 1.1: Tutte le nuove tabelle SQL (`decisions`, `debt_monthly_plans`, `recurring_expenses`, `daily_actions`, `baseline_snapshots`)
2. Task 1.2: Funzioni CRUD complete per ogni nuova tabella
3. Estensioni tabelle esistenti (`budgets.source`, `transactions.is_recurring`)

**Settimana 2**:
4. Task 1.3: Repository pattern base (`base.py`, primi 3 repository)
5. Task 2.1: BaselineCalculator con salvataggio in `baseline_snapshots`
6. Task 2.2: DebtPlanner con salvataggio in `debt_monthly_plans`

### Fase 2: Core Logic + AI (Settimana 3-4)
**Obiettivo**: Motori di calcolo e AI funzionanti

**Settimana 3**:
7. Task 2.3: BudgetGenerator (auto-generazione da debt plan)
8. Task 3.1: InsightEngine (generazione insight con Opus)
9. Task 3.2: ActionPlanner (Full Auto daily actions)

**Settimana 4**:
10. Task 6.1-6.2: Coach collegato + chat history persistence
11. Repository completamento (decision, action, budget)

### Fase 3: UX Directive + Recurring (Settimana 5-6)
**Obiettivo**: UI completamente funzionale

**Settimana 5**:
12. Task 4.1: Nuovi componenti UI (plan_vs_actual, daily_action_task, badges)
13. Task 4.2-4.3: Home Tab ristrutturata con in-app badge
14. Task 2.4: RecurringDetector

**Settimana 6**:
15. Task 3.3: RecurringOptimizer (Smart Suggestions)
16. EPICA 5: Recurring Tab completa in Money
17. Task 6.3: Decision integration nel Coach

### Fase 4: Polish & Completeness (Settimana 7-8)
**Obiettivo**: Feature avanzate e UX polish

**Settimana 7**:
18. EPICA 7: Wizard Setup guidato
19. EPICA 8: Monthly Re-Planning
20. EPICA 9: Impact Verification + Impact Stories UI

**Settimana 8**:
21. EPICA 10: Import restoration con categorization
22. Testing end-to-end
23. Performance optimization
24. Bug fixing e polish finale

---

## File Critici da Modificare/Creare

### Modifiche a File Esistenti
- `src/database.py` - Nuove tabelle + CRUD
- `src/analytics.py` - Integrare con baseline calculator
- `src/styles.py` - Nuovi componenti UI
- `src/ai/advisor.py` - Potenziamento + connessione
- `src/ai/categorizer.py` - Feedback loop
- `app.py` - Home tab, Coach tab, Import, Recurring

### Nuovi File da Creare
```
src/
├── repositories/
│   ├── __init__.py
│   ├── base.py
│   ├── transaction_repository.py
│   ├── debt_repository.py
│   ├── budget_repository.py
│   ├── recurring_repository.py
│   ├── decision_repository.py
│   └── action_repository.py
├── core_finance/
│   ├── __init__.py
│   ├── baseline.py
│   ├── debt_planner.py
│   ├── budget_generator.py
│   ├── recurring_detector.py
│   ├── replanner.py
│   └── impact_tracker.py
└── ai/
    ├── insight_engine.py
    ├── action_planner.py
    └── recurring_optimizer.py
```

---

## Metriche di Successo

### Outcome Metrics (Non Negoziabili)
- [ ] Risparmio medio: misurabile vs baseline 3 mesi
- [ ] Data payoff: ridotta vs proiezione iniziale

### Feature Metrics
- [ ] Daily Actions generate rate: 1-3/giorno
- [ ] Decision acceptance rate: > 50%
- [ ] Impact verification accuracy: actual within 20% of estimated
- [ ] Recurring expenses identified: > 80% coverage
- [ ] User engagement: daily app opens

### Technical Metrics
- [ ] AI response time: < 5s per insight
- [ ] Monthly AI cost: ~$10 target
- [ ] Database queries: < 100ms for dashboards
- [ ] Mobile performance: FCP < 2s

---

## Rischi e Mitigazioni

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| AI costs exceed budget | Media | Alto | Caching, batching, Haiku fallback |
| Recurring detection accuracy | Alta | Medio | Manual review + feedback loop |
| User decision fatigue | Media | Alto | Limit 3 actions/day, smart prioritization |
| Baseline inaccurate (no data) | Media | Medio | Use estimates, improve with data |
| Scope creep | Alta | Alto | Strict adherence to roadmap KPIs |

---

## Note Implementative

### Pattern Architetturali
- **Repository Pattern**: Per future migrazione backend
- **Service Layer**: Core finance separato da UI
- **Event-Driven**: Decisions → Impact tracking
- **Caching**: Snapshot financial data (1h TTL)

### AI Strategy (Opus Premium)
- **Extended Thinking**: Per ogni insight e decisione complessa
- **Token Budget**: ~15K per request, ~$10/mese
- **Batching**: Insights generati 1x/giorno, non real-time
- **Context Injection**: Sempre includere decisioni passate + baseline

### UX Principles
- **Directive over Informative**: Ogni schermata guida azione
- **Impact First**: Mostrare sempre €/mese o giorni risparmiati
- **Progressive Disclosure**: Dettagli on-demand, summary by default
- **Mobile First**: 480px max-width, touch-optimized
