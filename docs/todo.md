# Todo - MoneyMind

> Aggiornato: 2026-01-06
>
> Priorità basata su [GAP_ANALYSIS.md](GAP_ANALYSIS.md) e [MISSION.md](MISSION.md)

---

## P0 - Sprint 1: Diagnosi Completa (🔴 Critico)

- [ ] **Financial X-Ray Dashboard**
  - Report diagnosi one-page
  - Cash flow breakdown: Essenziali/Debiti/Wants/Disponibile
  - Debt composition analysis (interesse vs principale)
  - Endpoint: `/api/xray`

- [ ] **Onboarding Wizard**
  - Questionario 5-step (paure, motivazioni, literacy)
  - Profilo utente completo
  - Prima diagnosi automatica

- [ ] **Debt Cost Visualization**
  - Quanto costa ogni debito in interessi totali
  - Burden % su reddito mensile

---

## P0 - Sprint 2: Quick Wins (🔴 Critico)

- [ ] **Quick Wins Detector**
  - Scan automatico abbonamenti ottimizzabili
  - Tariffe rinegoziabili identificate
  - Script pronti per disdetta/rinegoziazione

- [ ] **Impact Calculator**
  - "Taglia €X/mese → payoff Y giorni prima"
  - Risparmio interessi stimato
  - Motivazione immediata per agire

- [ ] **Money Flow Sankey**
  - Visualizzazione grafica flusso denaro
  - Dove vanno i soldi esattamente

- [ ] **Victory Celebrations**
  - Badge per traguardi raggiunti
  - Streak tracking
  - Riconoscimento progressi

---

## P1 - Sprint 3: Sicurezza (🟡 Alto)

- [ ] **Journey Map**
  - Visualizzazione 3 fasi con milestone
  - Phase 1 (0-6m) → Phase 2 (6-18m) → Phase 3 (18-36m)
  - Date target per ogni milestone

- [ ] **Emergency Fund Planner**
  - Target dinamico (3-6 mesi spese essenziali)
  - Piano accelerazione
  - Prioritizzazione vs debiti

- [ ] **What-If Scenarios**
  - Simulatore job loss
  - Simulatore bonus/aumento
  - Impatto su timeline

- [ ] **Risk Dashboard**
  - Alert DTI crescente
  - Alert savings rate in calo
  - Spese fuori controllo

- [ ] **Debt Progress Bars**
  - Visualizzazione % per ogni debito
  - Soddisfazione visiva avanzamento

---

## P2 - Sprint 4: Crescita (🔴 Critico)

- [ ] **FIRE Calculator**
  - Calcolo data Financial Independence
  - 25x spese annuali target
  - Coast FIRE, Barista FIRE options

- [ ] **Post-Debt Redirect Plan**
  - Dove vanno i €550/mese liberati
  - Allocazione ottimale: fondo emergenza, investimenti, consumi

- [ ] **Investment Basics**
  - Guida ETF/PAC per contesto italiano
  - Previdenza complementare
  - Dove iniziare

- [ ] **Net Worth Projector**
  - "Se continuo così, tra 5/10/20 anni avrò..."
  - Motivazione lungo termine

---

## P2 - Sprint 5: Coaching (🟡 Alto)

- [ ] **Advisor Persona**
  - Coaching personalizzato per fase
  - Stile adattato al profilo utente
  - Decision tracking per miglioramento

- [ ] **Monthly Financial Letter**
  - Narrativa "il mese di Mattia"
  - Dati con storytelling
  - Celebrazione progressi

- [ ] **Nudge Proattivi**
  - Prevenzione errori in tempo reale
  - Notifiche smart per azioni

- [ ] **Year-in-Review**
  - Retrospettiva annuale
  - Celebrazione grandi progressi

---

## In Progress (UI Migration)

- [ ] Money Tab
  - [ ] API `/api/transactions` - Lista con filtri
  - [ ] API `/api/budgets/{month}` - Budget mensile
  - [ ] API `/api/recurring` - Spese ricorrenti
  - [ ] Frontend components

- [ ] Goals Tab con Journey Map
  - [ ] API `/api/debts` - Lista debiti
  - [ ] API `/api/debts/timeline` - Timeline payoff
  - [ ] Frontend components

- [ ] Profile Tab
  - [ ] API `/api/profile` - Profilo utente
  - [ ] API `/api/reports/monthly/{month}` - Report
  - [ ] Frontend components

- [ ] Coach Tab
  - [ ] API `/api/chat` - SSE streaming
  - [ ] Frontend chat UI

---

## Backlog - Low Priority / Future

- [ ] PWA / Mobile app installabile
- [ ] Backend remoto (PostgreSQL)
- [ ] Investment tracking dettagliato
- [ ] Multi-utente

---

## Completed

- [x] Schema DB v4.0 completo - 2026-01-04
- [x] Repository pattern (7 repositories) - 2026-01-04
- [x] Core finance engine - 2026-01-04
- [x] AI layer potenziato - 2026-01-04
- [x] Categorizzazione 99.9% accuracy - 2026-01-05
- [x] Aggiunte categorie Intrattenimento + Regali - 2026-01-05
- [x] Home Tab POC (Next.js + FastAPI) - 2026-01-06
- [x] MISSION.md - Definizione missione - 2026-01-06
- [x] GAP_ANALYSIS.md - Analisi gap - 2026-01-06
- [x] Documentazione aggiornata - 2026-01-06

---

## Riferimenti

- [MISSION.md](MISSION.md) - Missione e 4 fasi
- [GAP_ANALYSIS.md](GAP_ANALYSIS.md) - Dettaglio gap
- [architecture.md](architecture.md) - Architettura target
- [project_status.md](project_status.md) - Stato corrente
