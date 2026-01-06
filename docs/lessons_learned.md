# Lessons Learned - MoneyMind

Knowledge base delle best practice scoperte durante lo sviluppo.

---

## Categorizzazione

### Pattern Rule-Based Prima di AI
- **Problema**: Ogni chiamata API costa e aggiunge latenza
- **Soluzione**: 100+ pattern regex che coprono 95%+ delle transazioni
- **Risultato**: Solo ~5% delle transazioni richiede Claude Haiku
- **Costi**: Da ~$1/mese a ~$0.05/mese per categorizzazione

### Batch vs Single Categorization
- **Problema**: Categorizzare 1 transazione alla volta = troppe API calls
- **Soluzione**: Batch di 10 transazioni per chiamata
- **Risultato**: 10x riduzione chiamate API

### Pattern Troppo Generici
- **Problema**: Pattern come `bar` matchava anche "Barbara", "barbecue"
- **Soluzione**: Usare word boundaries `\bbar\b`
- **Risultato**: Eliminati falsi positivi

---

## Architettura

### Repository Pattern
- **Problema**: Query SQL sparse in tutto il codice
- **Soluzione**: Repository per ogni entità
- **Risultato**: Facilita testing, futura migrazione DB, single source of truth

### Separare Core Finance da UI
- **Problema**: Logica di calcolo mescolata a Streamlit
- **Soluzione**: `src/core_finance/` con pure functions
- **Risultato**: Riutilizzabile, testabile, potenzialmente esponibile come API

### Service Layer Pattern
- **Problema**: UI che chiama direttamente database
- **Soluzione**: UI → Service (analytics, core_finance) → Repository → DB
- **Risultato**: Layers ben definiti, responsabilità chiare

---

## AI Integration

### Extended Thinking per Decisioni Critiche
- **Contesto**: Daily actions e insights richiedono ragionamento complesso
- **Soluzione**: Claude Opus 4.5 con extended thinking
- **Risultato**: Suggerimenti più contestuali e personalizzati

### Multi-Model Strategy
- **Contesto**: Non tutte le task richiedono Opus
- **Soluzione**: Haiku per batch, Sonnet per reports, Opus per advisor
- **Risultato**: Costi ottimizzati (~$10/mese target)

---

## Database

### Indici Critici
- **Problema**: Dashboard lenta con molte transazioni
- **Soluzione**: Indici su `date`, `category_id`, `status`
- **Risultato**: Query sotto 100ms

### Schema Estensibile
- **Problema**: v1.0 schema troppo rigido per feature v4.0
- **Soluzione**: Tabelle separate per ogni concetto (decisions, actions, recurring)
- **Risultato**: Facile aggiungere feature senza ALTER TABLE invasivi

---

## UX/UI

### Mobile-First
- **Contesto**: App usata principalmente da telefono
- **Soluzione**: Max-width 480px, bottom tab navigation, touch targets grandi
- **Risultato**: Esperienza native-like su mobile

### Dark Theme Default
- **Contesto**: Uso serale frequente
- **Soluzione**: Dark theme con accent emerald (#10B981)
- **Risultato**: Meno affaticamento visivo, look moderno

---

## Workflow Development

### Plan Mode First
- **Problema**: Saltare direttamente al codice causa rework
- **Soluzione**: Sempre plan mode per feature complesse
- **Risultato**: Meno refactoring, scope chiaro

### Serena Memories per Context
- **Problema**: Perdere contesto tra sessioni
- **Soluzione**: Session memories con key findings
- **Risultato**: Ripresa lavoro più veloce

---

## Anti-Pattern da Evitare

| Anti-Pattern | Problema | Soluzione |
|--------------|----------|-----------|
| SQL inline | Difficile manutenzione | Repository pattern |
| Hardcoded categories | Non scalabile | DB-driven categories |
| Single model AI | Costi alti | Multi-model strategy |
| Monolithic app.py | File troppo grande | Moduli separati per tab |
| Categorizzazione real-time | Latenza UX | Batch + background processing |

---

## Template per Nuove Lesson

```markdown
### [Titolo Breve]
- **Problema**: Descrizione del problema incontrato
- **Soluzione**: Come l'abbiamo risolto
- **Risultato**: Benefici ottenuti
```
