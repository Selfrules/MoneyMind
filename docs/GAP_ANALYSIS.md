# Gap Analysis - MoneyMind vs Mission

> **Analisi critica**: Confronto tra stato attuale dell'app e requisiti della missione verso la libertà finanziaria.
>
> Ultimo aggiornamento: 2026-01-06

---

## Executive Summary

| Fase | Copertura Attuale | Gap Severity | Priorità |
|------|-------------------|--------------|----------|
| **Diagnosi** | 40% | 🔴 Critico | P0 |
| **Ottimizzazione (0-90g)** | 50% | 🔴 Critico | P0 |
| **Sicurezza (3-24m)** | 65% | 🟡 Alto | P1 |
| **Crescita (2+ anni)** | 10% | 🔴 Critico | P2 |

**Conclusione**: MoneyMind ha solide fondamenta tecniche (categorizzazione 99.9%, strategie debiti, baseline) ma manca di **coaching proattivo** e **visione lungo termine**. L'app osserva ma non guida attivamente verso la libertà finanziaria.

---

## FASE 1: DIAGNOSI

### Cosa Funziona Bene (40% coverage)

| Feature | Status | File/Modulo |
|---------|--------|-------------|
| Calcolo KPI (net worth, savings rate, DTI, emergency fund) | ✅ | `analytics.py` |
| Financial Health Score (A-F) con breakdown | ✅ | `analytics.py` |
| Categorizzazione transazioni (100+ pattern) | ✅ | `ai/categorizer.py` |
| 99.9% accuracy (2/1717 in "Altro") | ✅ | - |
| Baseline calculator (medie 3 mesi) | ✅ | `core_finance/baseline.py` |
| Snapshot finanziario mensile | ✅ | `analytics.py` |

### Gap Critici

| Gap | Descrizione | Impatto sulla Missione |
|-----|-------------|------------------------|
| **Nessun report diagnosi completo** | Manca "radiografia finanziaria" one-page che mostri situazione complessiva | Utente non ha visione d'insieme, non sa da dove partire |
| **Nessun onboarding guidato** | Manca questionario iniziale (paure, motivazioni, literacy finanziaria, obiettivi) | App non conosce l'utente, consigli generici |
| **Nessuna analisi comportamentale** | Manca: spese impulso vs pianificate, pattern stagionali, giorni critici | Non identifica vere cause dei problemi |
| **Nessun debt composition analysis** | Manca: interesse pagato vs principale, debt burden % su reddito | Non mostra il costo reale dei debiti |
| **Nessun cash flow statement** | Manca: entrate - uscite - debiti = disponibile per saving/investing | Confusione su margine reale |

### Azioni Richieste

1. **Financial X-Ray Dashboard** - Report diagnosi automatico one-page
2. **Onboarding Wizard** - Questionario 5-step per profilo completo
3. **Debt Cost Visualization** - Quanto costa ogni debito in interessi
4. **Cash Flow Breakdown** - Essenziali / Debiti / Wants / Disponibile

---

## FASE 2: OTTIMIZZAZIONE (0-90 giorni)

### Cosa Funziona Bene (50% coverage)

| Feature | Status | File/Modulo |
|---------|--------|-------------|
| Action planner (1-3 azioni giornaliere) | ✅ | `ai/action_planner.py` |
| Insight engine (anomalie, budget overrun) | ✅ | `ai/insight_engine.py` |
| Recurring expense tracker | ✅ | `recurring_repository.py` |
| Suggerimenti ottimizzazione ricorrenti | ✅ | `ai/recurring_optimizer.py` |
| Budget generator (50/30/20 adattato) | ✅ | `core_finance/budget_generator.py` |
| Monthly replanning | ✅ | `core_finance/replanner.py` |

### Gap Critici

| Gap | Descrizione | Impatto sulla Missione |
|-----|-------------|------------------------|
| **Nessun modulo "Quick Wins"** | Manca: abbonamenti inutilizzati, tariffe rinegoziabili, script pronti per disdetta | Utente non sa da dove iniziare l'ottimizzazione |
| **Nessuna prioritizzazione tagli** | Manca: effort vs impact matrix per spese | Utente taglia a caso, si frustra |
| **Nessun "Where's my money going?"** | Manca: breakdown visivo Essenziali/Debiti/Wants/Disponibile | Confusione su dove vanno i soldi |
| **Nessun impact calculator** | Manca: "se tagli €50/mese → payoff 2 mesi prima, risparmi €X interessi" | Manca motivazione immediata per agire |
| **Nessun tracking comportamentale** | Manca: celebrazione piccole vittorie, streak, momentum | Utente si demotiva |
| **Nessun reminder system** | Manca: notifiche per scadenze, azioni da completare | Azioni dimenticate |

### Azioni Richieste

1. **Quick Wins Detector** - Scan automatico abbonamenti ottimizzabili
2. **Impact Calculator** - "Taglia €X → accelera payoff di Y giorni"
3. **Money Flow Sankey** - Visualizzazione dove vanno i soldi
4. **Victory Celebrations** - Riconoscimento progressi (badge, streak)
5. **Action Reminders** - Sistema notifiche per azioni pending

---

## FASE 3: SICUREZZA (3-24 mesi)

### Cosa Funziona Bene (65% coverage)

| Feature | Status | File/Modulo |
|---------|--------|-------------|
| Strategie debt payoff (Avalanche/Snowball) | ✅ | `analytics.py` |
| Priority ordering debiti | ✅ | `debt_repository.py` |
| Monthly payment plans (planned vs actual) | ✅ | `core_finance/debt_planner.py` |
| Goals tracking (emergency fund, debt targets) | ✅ | `database.py` |
| Scenario comparison (current vs MoneyMind) | ✅ | `analytics.py` |
| Baseline vs actual comparison | ✅ | `core_finance/baseline.py` |

### Gap Critici

| Gap | Descrizione | Impatto sulla Missione |
|-----|-------------|------------------------|
| **Nessuna roadmap fasi visualizzata** | Manca: Phase 1 (0-6m) → Phase 2 (6-18m) → Phase 3 (18-36m) con milestone | Utente non vede il percorso completo |
| **Nessun piano accelerazione emergency fund** | Manca: quanto serve? dove tenerlo? quando prioritizzare vs debiti? | Confusione su sicurezza finanziaria |
| **Nessun trade-off analyzer** | Manca: debito vs emergency fund? quale prima? quanto allocare? | Decisioni sub-ottimali |
| **Nessun "what if" calculator** | Manca: se perdo lavoro? se ricevo bonus? se aumento stipendio? | Non prepara agli imprevisti |
| **Nessun risk monitoring** | Manca: alert DTI crescente, savings rate in calo, spese fuori controllo | Rischi non intercettati in tempo |
| **Nessun debt payoff progress bar** | Manca: visualizzazione % completamento per ogni debito | Manca soddisfazione visiva |

### Azioni Richieste

1. **Journey Map** - Visualizzazione 3 fasi con milestone e date target
2. **Emergency Fund Planner** - Piano accelerazione con target dinamico
3. **What-If Scenarios** - Simulatore job loss, bonus, aumento
4. **Risk Dashboard** - Alert automatici per metriche in peggioramento
5. **Debt Progress Bars** - Visualizzazione avanzamento per debito

---

## FASE 4: CRESCITA (2+ anni)

### Cosa Funziona Bene (10% coverage)

| Feature | Status | File/Modulo |
|---------|--------|-------------|
| Calcolo data payoff debiti | ✅ | `analytics.py` |
| Tracking savings rate | ✅ | `analytics.py` |
| KPI history (trend net worth) | ✅ | `database.py` |

### Gap Critici (Quasi Totale Assenza)

| Gap | Descrizione | Impatto sulla Missione |
|-----|-------------|------------------------|
| **Nessun FIRE calculator** | Manca: "quando sarò FI?" (25x spese annuali), coast FIRE, barista FIRE | Nessuna visione lungo termine |
| **Nessun piano post-debiti** | Manca: dove redirigere €550/mese pagamenti liberati? | App diventa inutile dopo payoff |
| **Nessuna guida investimenti** | Manca: dove investire? ETF? PAC? previdenza complementare? | Soldi restano fermi sul conto |
| **Nessun coaching anti-lifestyle-inflation** | Manca: prevenzione inflazione stile di vita post-debiti | Rischio ricaduta nei debiti |
| **Nessuna integrazione obiettivi vita** | Manca: casa, pensione, famiglia, legacy, sabbatico | Solo debiti, non vita reale |
| **Nessun net worth projection** | Manca: "se continuo così, tra 5/10/20 anni avrò..." | Nessuna motivazione lungo termine |

### Azioni Richieste

1. **FIRE Calculator** - Calcolo data Financial Independence
2. **Post-Debt Redirect Plan** - Dove vanno i €550/mese liberati
3. **Investment Basics** - Guida ETF/PAC per contesto italiano
4. **Life Goals Integration** - Casa, pensione, famiglia nel piano
5. **Net Worth Projector** - Proiezione patrimonio futuro

---

## GAP TRASVERSALI (Architettura)

### Coaching & Accountability

| Gap | Descrizione | Impatto |
|-----|-------------|---------|
| **Nessun advisor persona** | Consigli generici, non personalizzati al profilo/fase dell'utente | Coaching poco efficace |
| **Nessun decision tracking** | Non impara cosa funziona per l'utente specifico | Non migliora nel tempo |
| **Nessuna accountability** | App osserva passivamente, non motiva attivamente | Utente abbandona |
| **Nessun nudge proattivo** | Non previene errori in tempo reale (es. spesa anomala) | Intervento sempre tardivo |

### Visualizzazione

| Gap | Descrizione | Impatto |
|-----|-------------|---------|
| **Nessun net worth waterfall** | Non mostra composizione patrimonio (assets vs liabilities) | Confusione su stato reale |
| **Nessun progress bar debiti** | Manca soddisfazione visiva di "sto avanzando" | Demotivazione |
| **Nessun trend chart significativo** | Grafici esistenti ma non legati a decisioni | Dati senza azione |

### Reporting

| Gap | Descrizione | Impatto |
|-----|-------------|---------|
| **Nessuna monthly letter** | Dati senza narrativa, manca "il mese di Mattia" | Distacco emotivo |
| **Nessuna impact verification** | Azioni suggerite ma mai verificate se hanno funzionato | Non si impara |
| **Nessun year-in-review** | Manca retrospettiva annuale | Nessuna celebrazione grandi progressi |

---

## Priorità di Implementazione

### P0 - Critici (Sprint 1-2)

| Feature | Fase | Effort | Impact |
|---------|------|--------|--------|
| Financial X-Ray Dashboard | Diagnosi | M | Alto |
| Onboarding Wizard | Diagnosi | M | Alto |
| Quick Wins Detector | Ottimizzazione | M | Alto |
| Impact Calculator | Ottimizzazione | S | Alto |
| Money Flow Breakdown | Ottimizzazione | S | Alto |

### P1 - Importanti (Sprint 3)

| Feature | Fase | Effort | Impact |
|---------|------|--------|--------|
| Journey Map | Sicurezza | M | Alto |
| Emergency Fund Planner | Sicurezza | S | Medio |
| What-If Scenarios | Sicurezza | M | Medio |
| Risk Dashboard | Sicurezza | S | Medio |

### P2 - Strategici (Sprint 4-5)

| Feature | Fase | Effort | Impact |
|---------|------|--------|--------|
| FIRE Calculator | Crescita | M | Alto |
| Post-Debt Plan | Crescita | S | Alto |
| Investment Basics | Crescita | M | Medio |
| Advisor Persona | Coaching | L | Alto |
| Monthly Letter | Reporting | M | Medio |

---

## Metriche di Validazione

### Come Sappiamo che i Gap Sono Chiusi

| Gap | Metrica di Successo |
|-----|---------------------|
| Financial X-Ray | Utente comprende situazione in < 30 secondi |
| Quick Wins | 3+ ottimizzazioni implementate nei primi 30 giorni |
| Impact Calculator | Decisioni prese con consapevolezza impatto |
| Journey Map | Utente sa in quale fase è e cosa viene dopo |
| FIRE Calculator | Utente ha data target per FI |
| Advisor Persona | Tasso completamento azioni > 70% |

---

## Riferimenti

- `docs/MISSION.md` - Definizione missione completa
- `misc/roadmap.md` - Roadmap implementazione
- `docs/architecture.md` - Architettura target
- `misc/IMPLEMENTATION_PLAN_V4.md` - Piano implementazione v4.0
