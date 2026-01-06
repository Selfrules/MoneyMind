# MoneyMind – Roadmap orientata al valore

> **Mission**: Accompagnare Mattia verso la libertà finanziaria attraverso le 4 fasi: Diagnosi → Ottimizzazione → Sicurezza → Crescita
>
> Documentazione: [MISSION.md](../docs/MISSION.md) | [GAP_ANALYSIS.md](../docs/GAP_ANALYSIS.md)

Obiettivo: trasformare MoneyMind in un **assistente direttivo** che ti fa uscire dai debiti più in fretta e aumenta il risparmio mensile, non solo tracciare spese.

---

## Le 4 Fasi verso la Libertà Finanziaria

| Fase | Periodo | Obiettivo | Coverage Attuale |
|------|---------|-----------|------------------|
| **1. Diagnosi** | Iniziale | Fotografare situazione attuale | 40% 🔴 |
| **2. Ottimizzazione** | 0-90 giorni | Liberare margine, quick wins | 50% 🔴 |
| **3. Sicurezza** | 3-24 mesi | Stabilità: debiti a 0, fondo emergenza | 65% 🟡 |
| **4. Crescita** | 2+ anni | Costruire patrimonio e rendite | 10% 🔴 |

---

## KPI di outcome (non negoziabili)

- **Risparmio medio mensile**: aumento di almeno +€200/mese rispetto alla baseline (calcolata sui 3 mesi precedenti).
- **Data stimata uscita debiti**: riduzione del tempo stimato di payoff di almeno 6 mesi rispetto allo scenario "continuo così".

Tutte le funzionalità sotto devono esistere SOLO se spingono direttamente uno di questi due KPI.

---

## Sprint Roadmap (Mission-Aligned)

### Sprint 1: Diagnosi Completa (P0 - 🔴 Critico)
| Feature | Fase | Impatto |
|---------|------|---------|
| Financial X-Ray Dashboard | Diagnosi | Utente comprende situazione in 30 sec |
| Onboarding Wizard | Diagnosi | App conosce l'utente, personalizza |
| Debt Composition Analysis | Diagnosi | Mostra costo reale debiti |

### Sprint 2: Quick Wins (P0 - 🔴 Critico)
| Feature | Fase | Impatto |
|---------|------|---------|
| Quick Wins Detector | Ottimizzazione | 3+ ottimizzazioni in 30 giorni |
| Impact Calculator | Ottimizzazione | Motivazione immediata per agire |
| Money Flow Breakdown | Ottimizzazione | Chiarezza su dove vanno i soldi |

### Sprint 3: Safety Roadmap (P1 - 🟡 Alto)
| Feature | Fase | Impatto |
|---------|------|---------|
| Journey Map | Sicurezza | Utente vede percorso completo |
| Emergency Fund Planner | Sicurezza | Piano concreto per sicurezza |
| What-If Scenarios | Sicurezza | Preparazione agli imprevisti |

### Sprint 4: Wealth Building (P2 - 🔴 Critico)
| Feature | Fase | Impatto |
|---------|------|---------|
| FIRE Calculator | Crescita | Data target per FI |
| Post-Debt Plan | Crescita | App utile dopo payoff |
| Investment Basics | Crescita | Soldi investiti, non fermi |

### Sprint 5: Coaching Excellence
| Feature | Fase | Impatto |
|---------|------|---------|
| Advisor Persona | Coaching | Tasso completamento azioni >70% |
| Monthly Letter | Reporting | Dati con narrativa emozionale |
| Progress Celebrations | Coaching | Motivazione e retention |

---

## PILLAR 1 – Piano debiti + budget auto‑generato

### 1.1 Setup finanziario guidato (wizard iniziale)

- Creare un flusso step‑by‑step che raccoglie: entrate mensili, elenco debiti (o import da DB), spese essenziali minime e livello di aggressività verso i debiti.
- Calcolare la baseline: risparmio medio mensile attuale e data di payoff stimata se tutto resta uguale.

### 1.2 Motore di piano debiti (Avalanche/Snowball “vincolato”)

- Usare un algoritmo Avalanche/Snowball per generare un **piano mensile di pagamento debiti** con importi per ciascun debito, timeline e interessi stimati.
- Visualizzare sempre il confronto tra: “scenario attuale” vs “scenario MoneyMind” (mesi in meno, interessi risparmiati, data target).

### 1.3 Budget auto‑generato per categoria

- Generare automaticamente il **budget mensile per categoria** partendo da:
  - piano debiti (prioritario),
  - spese essenziali,
  - regole tipo 50/30/20 adattate alla fase “Debt Payoff”.
- Permettere micro‑aggiustamenti manuali per categoria, con feedback immediato sull’impatto su risparmio e data di payoff.

### 1.4 Aggiornamento mensile del piano (re‑planning)

- A fine mese, ricalcolare il piano in base alle spese effettive: se hai speso più o meno del previsto, il sistema aggiusta debiti e budget e mostra cosa è cambiato.
- Evidenziare chiaramente se sei **on track / in ritardo / in anticipo** rispetto alla data target di uscita dai debiti.

---

## PILLAR 2 – Insight → decisione → azione → verifica

### 2.1 Modello “Insight operativo”

Per ogni insight critico, usare questo formato:

- **Problema:** es. “Ristoranti +65% rispetto al budget e +40% rispetto alla media degli ultimi 3 mesi”.
- **Raccomandazione concreta:** es. “Taglia 80€ dai ristoranti questo mese e spostali sul debito X”.
- **Azione proposta:** 1–3 passi pratici (es. “riduci cene fuori a 1 a settimana”, “pianifica 2 sessioni di batch cooking”).
- **Impatto stimato:** quanto anticipa la data di payoff o quanto aumenta il risparmio mensile.

### 2.2 Daily Action Plan (1–3 task al giorno)

- In Home, sezione “**Oggi**” con massimo 3 task ad alto impatto ordinati per impatto sui KPI (es. “Rivedi abbonamenti > 15€/mese”, “Conferma aumento rata di 20€ su debito X”).
- Ogni task deve essere spuntabile e salvare una **decisione** nel DB (accettata/rifiutata/rimandata).

### 2.3 Tracking delle decisioni e dei risultati

- Aggiungere una tabella `decisions` che memorizza: data, tipo decisione (taglio spesa, aumento rata, cambio fornitore), importo, categoria/debito coinvolto.
- Collegare periodicamente le decisioni ai risultati, es. “Da quando hai cambiato gestore luce, Utenze –18% rispetto al trimestre precedente”.

### 2.4 Insight prioritizzati (no overload)

- Implementare una coda di insight con severità (alto/medio/basso) e **limitare il numero di insight attivi** per evitare overload cognitivo.
- Mostrare solo quelli con impatto evidente sui due KPI core; gli altri restano in “later / nice to know”.

---

## PILLAR 3 – Ricorrenze, abbonamenti, utenze

### 3.1 Identificazione automatica spese ricorrenti

- Analizzare le transazioni per trovare spese con pattern mensile/trimestrale (abbonamenti, utenze, palestre, assicurazioni).
- Taggare queste transazioni come **ricorrenti** e mostrarle in una sezione dedicata (“Spese ricorrenti”).

### 3.2 Schede per ogni ricorrenza

Per ogni abbonamento/utenza/prestito ricorrente:

- Mostrare: costo medio, trend 6 mesi, percentuale sul reddito, impatto sul budget.
- Calcolare cosa succede se lo cancelli, riduci o rinegozi (impatto su risparmio e data di payoff).

### 3.3 Suggerimenti di ottimizzazione concreti

- Usare l’AI per generare **strategie specifiche** per ogni ricorrenza (es. “Downgrade piano Netflix”, “Passa a offerta luce X”, “Accorpa polizze, target risparmio 15€/mese”).
- Per ogni suggerimento creare un task nel Daily Action Plan, con stato “fatto / non fattibile / rimandato”.

### 3.4 Misurare l’effetto dei cambi

- Collegare le decisioni sulle ricorrenze ai dati successivi, es. “Cambio gestore luce: risparmio medio 22€/mese negli ultimi 3 mesi”.

---

## FOUNDATION – Categorizzazione, UX e architettura

### F.1 Categorizzazione Macro/Micro orientata al piano

- Estendere le categorie a **macro_categoria** / **micro_categoria** solo se utilizzate dal motore di piano (budget, insight, ricorrenze).
- Semplificare le macro categorie enfatizzando “Essenziali / Non Essenziali / Debiti / Risparmi” invece di decine di etichette poco operative.

### F.2 UX essenziale e direttiva

- Home deve rispondere a tre domande:
  1) “Sto andando meglio o peggio rispetto al mese scorso?”
  2) “Sono on track per uscire dai debiti?”
  3) “Cosa devo fare oggi?”.
- Ridurre grafici non necessari e mantenere solo quelli che supportano decisioni (timeline debiti, risparmio mensile, spese ricorrenti).

### F.3 Architettura pronta per backend futuro

- Mantenere SQLite locale ma introdurre un layer di accesso dati (repository) per poter passare a DB remoto senza cambiare la logica core.
- Separare moduli:
  - `core_finance` (calcoli di piano, budget, debiti),
  - `ai_layer` (prompting, generazione insight),
  - `ui_layer` (Streamlit).
- Definire funzioni pure che in futuro possano diventare endpoint API (es. `get_daily_actions()`, `recompute_debt_plan()`, `get_recurrent_expenses_summary()`).

---

## Posticipato (non core, fase 2+)

- Tracking investimenti dettagliato (portafoglio, asset allocation, P&L).
- App mobile / PWA / backend remoto.
- Gamification complessa, badge, score social.

Queste aree entrano solo dopo che MoneyMind dimostra, sui tuoi dati reali, di migliorare **risparmio mensile e tempo di uscita dai debiti** in modo misurabile.

---

## Validazione Gap Closure

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

- [docs/MISSION.md](../docs/MISSION.md) - Missione completa
- [docs/GAP_ANALYSIS.md](../docs/GAP_ANALYSIS.md) - Dettaglio gap
- [docs/architecture.md](../docs/architecture.md) - Architettura target
- [docs/todo.md](../docs/todo.md) - Task list prioritizzata
