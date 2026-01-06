# MoneyMind

**Personal Finance Dashboard con AI**

| Campo | Valore |
|-------|--------|
| Versione | 1.0 |
| Data | 3 Gennaio 2025 |
| Autore | Mattia De Luca |
| Target | Uso personale |

---

## Executive summary

MoneyMind è una dashboard finanziaria personale che gira in locale su macchina Windows. Ogni settimana l'utente carica i CSV delle sue due banche (Revolut e Illimity), l'app li normalizza in un database locale, categorizza automaticamente le transazioni usando Claude API, e mostra dove vanno i soldi. Una volta al mese genera un report con insights e suggerimenti per ottimizzare le spese.

### Perché questo progetto

GoCardless ha chiuso le nuove registrazioni. Le API bancarie dirette richiedono licenze AISP (6-18 mesi, €15k+). L'unica via praticabile per un progetto personale è l'import manuale dei CSV — ma con un layer intelligente che trasforma questo workflow in qualcosa di utile e non tedioso.

---

## Il problema

- **Frammentazione dei dati:** Due conti su due banche diverse, nessuna vista unificata
- **Categorizzazione manuale:** Revolut ha categorie ma sono imprecise, Illimity non ha nulla
- **Zero insights:** Nessun modo di sapere quanto si spende per categoria, trend, anomalie
- **Nessun budget:** Impossibile impostare limiti e ricevere avvisi

---

## La soluzione

Un'applicazione web locale (Streamlit) che:

1. **Importa e normalizza** i CSV di Revolut (formato custom) e Illimity (Excel)
2. **Deduplica automaticamente** le transazioni già importate (basandosi su hash)
3. **Categorizza con Claude** le transazioni non ancora categorizzate
4. **Mostra dashboard** con spese per categoria, trend temporali, saldi
5. **Genera report mensile** con analisi AI e suggerimenti per risparmiare

---

## Stack tecnologico

| Componente | Tecnologia | Motivazione |
|------------|------------|-------------|
| UI | Streamlit | Sviluppo rapido, componenti pronti |
| Database | SQLite | File locale, zero setup |
| AI | Claude API | Categorizzazione e insights |
| Charts | Plotly | Integrato in Streamlit, interattivo |
| Parsing | Pandas | Gestisce CSV, Excel, Parquet |

**Perché Streamlit?** Si sviluppa in poche ore, ha componenti per file upload, charts, e tabelle già pronti. Non serve scrivere frontend. Perfetto per un progetto da completare in un giorno.

---

## Data model

### Tabella: transactions

| Campo | Tipo | Note |
|-------|------|------|
| \`id\` | TEXT PK | Hash SHA256 (dedup) |
| \`date\` | DATE | Data transazione |
| \`description\` | TEXT | Descrizione originale |
| \`amount\` | REAL | Positivo=entrata, negativo=uscita |
| \`category_id\` | INTEGER FK | Riferimento a categories |
| \`bank\` | TEXT | revolut / illimity |
| \`account_type\` | TEXT | current / savings |
| \`type\` | TEXT | CARD_PAYMENT, TRANSFER, etc. |
| \`balance\` | REAL | Saldo dopo transazione |
| \`created_at\` | DATETIME | Timestamp import |

### Tabella: categories

| Campo | Tipo | Note |
|-------|------|------|
| \`id\` | INTEGER PK | Autoincrement |
| \`name\` | TEXT | Nome categoria |
| \`icon\` | TEXT | Emoji |
| \`color\` | TEXT | Hex color per UI |

### Tabella: budgets

| Campo | Tipo | Note |
|-------|------|------|
| \`id\` | INTEGER PK | Autoincrement |
| \`category_id\` | INTEGER FK | Categoria |
| \`amount\` | REAL | Limite mensile |
| \`month\` | TEXT | YYYY-MM |

### SQL Schema

\`\`\`sql
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    icon TEXT,
    color TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    date DATE NOT NULL,
    description TEXT,
    amount REAL NOT NULL,
    category_id INTEGER,
    bank TEXT NOT NULL,
    account_type TEXT,
    type TEXT,
    balance REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    month TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    UNIQUE(category_id, month)
);
\`\`\`

---

## Flusso di import

### Revolut (CSV)

**File:** \`transactions_YYYYMMDD.parquet\` (ma è un CSV, non un vero Parquet)

**Colonne disponibili:** \`tx_id\`, \`account\`, \`timestamp\`, \`amount\`, \`fee\`, \`balance\`, \`currency\`, \`description\`, \`category\`, \`tags\`, \`note\`, \`type\`, \`product\`

| Campo Revolut | Campo DB | Trasformazione |
|---------------|----------|----------------|
| \`timestamp\` | \`date\` | \`datetime.fromtimestamp()\` |
| \`description\` | \`description\` | Diretto |
| \`amount\` | \`amount\` | Diretto |
| \`account\` | \`account_type\` | REV_CUR→current, REV_SAV→savings |
| \`type\` | \`type\` | Diretto |
| \`balance\` | \`balance\` | Diretto |
| - | \`bank\` | Hardcoded: 'revolut' |

**Tipi di transazione Revolut:**
- TRANSFER (2371 occorrenze)
- CARD_PAYMENT (1098)
- TOPUP (40)
- ATM (30)
- CARD_REFUND (15)
- REV_PAYMENT (1)
- CHARGE (1)

**Account types Revolut:**
- REV_CUR (conto corrente)
- REV_SAV (conto risparmio)
- ILL_CUR (già integrato da Illimity)

### Illimity (Excel)

**File:** \`illimity.xlsx\`

**Header alla riga 16 (0-indexed: skiprows=16)**

**Colonne:** \`Data operazione\`, \`Tipologia\`, \`Causale\`, \`Stato\`, \`Entrate\`, \`Uscite\`, \`Valuta\`, \`Rapporto\`

| Campo Illimity | Campo DB | Trasformazione |
|----------------|----------|----------------|
| \`Data operazione\` | \`date\` | \`pd.to_datetime()\` |
| \`Causale\` | \`description\` | Diretto |
| \`Entrate\`/\`Uscite\` | \`amount\` | Entrate positive, Uscite negative |
| \`Tipologia\` | \`type\` | Mapping: Bonifico→TRANSFER, etc. |
| - | \`bank\` | Hardcoded: 'illimity' |
| - | \`account_type\` | Hardcoded: 'current' |

**Tipologie Illimity:**
- Mandato sdd (33 occorrenze)
- Bonifico Italia (18)
- Bonifico istantaneo altri paesi (16)
- Bonifico altri paesi (10)
- Bonifico istantaneo (9)

### Logica di deduplicazione

\`\`\`python
import hashlib

def generate_transaction_id(date, amount, description, bank):
    """Genera hash univoco per deduplicazione."""
    raw = f"{date}|{amount}|{description}|{bank}"
    return hashlib.sha256(raw.encode()).hexdigest()
\`\`\`

---

## Categorizzazione AI

Ogni transazione importata viene processata da Claude per assegnare una categoria. Il sistema usa un prompt che conosce il contesto personale per categorizzare in modo intelligente.

### Categorie predefinite

| Categoria | Icona | Esempi |
|-----------|-------|--------|
| Stipendio | 💰 | Accredito competenze |
| Affitto | 🏠 | Bonifico affitto |
| Utenze | 💡 | Luce, gas, internet |
| Spesa | 🛒 | Supermercato, alimentari |
| Ristoranti | 🍕 | Ristoranti, delivery |
| Trasporti | 🚗 | Benzina, parcheggi, treno |
| Salute | 💊 | Farmacia, visite mediche |
| Palestra | 🏋️ | 21 Lab, abbonamenti sport |
| Abbonamenti | 📱 | Netflix, Spotify, etc. |
| Shopping | 🛍️ | Abbigliamento, elettronica |
| Psicologo | 🧠 | Sedute terapia |
| Gatti | 🐱 | Cibo, veterinario |
| Viaggi | ✈️ | Hotel, voli, escursioni |
| Caffè | ☕ | Bar, colazioni |
| Barbiere | 💈 | Taglio capelli |
| Trasferimenti | 🔄 | Tra conti, risparmi |
| Altro | 📦 | Non categorizzabile |

### Prompt di categorizzazione

\`\`\`python
CATEGORIZATION_PROMPT = """Sei un assistente finanziario. Categorizza questa transazione.

Transazione:
- Descrizione: {description}
- Importo: {amount} EUR
- Data: {date}
- Tipo: {type}

Categorie disponibili: Stipendio, Affitto, Utenze, Spesa, Ristoranti, Trasporti, Salute, Palestra, Abbonamenti, Shopping, Psicologo, Gatti, Viaggi, Caffè, Barbiere, Trasferimenti, Altro

Contesto: L'utente è un PM che vive a Reggio Emilia, va in palestra al 21 Lab, ha gatti.

Rispondi SOLO con il nome della categoria, nient'altro."""
\`\`\`

### Batch categorization

Per ottimizzare i costi API, le transazioni vengono categorizzate in batch:

\`\`\`python
BATCH_CATEGORIZATION_PROMPT = """Sei un assistente finanziario. Categorizza queste transazioni.

Transazioni:
{transactions_list}

Categorie disponibili: Stipendio, Affitto, Utenze, Spesa, Ristoranti, Trasporti, Salute, Palestra, Abbonamenti, Shopping, Psicologo, Gatti, Viaggi, Caffè, Barbiere, Trasferimenti, Altro

Rispondi in formato JSON:
{{"results": [{{"id": "hash1", "category": "NomeCategoria"}}, ...]}}"""
\`\`\`

---

## Dashboard

### Pagina: Overview (Home)

- **Card saldi:** Saldo totale, saldo Revolut, saldo Illimity
- **Chart entrate/uscite:** Grafico a barre mensile (ultimi 6 mesi)
- **Donut categorie:** Distribuzione spese per categoria (mese corrente)
- **Lista ultime transazioni:** Le 20 transazioni più recenti

### Pagina: Transazioni

- **Tabella completa:** Tutte le transazioni con filtri per data, categoria, banca, tipo
- **Modifica categoria:** Click su categoria per cambiarla manualmente
- **Export:** Scarica CSV filtrato

### Pagina: Budget

- **Setup budget:** Imposta limite mensile per ogni categoria
- **Progress bar:** Quanto hai speso vs budget per categoria
- **Alert:** Warning quando superi 80%, rosso quando superi 100%

### Pagina: Report mensile

- **Riepilogo mese:** Entrate totali, uscite totali, risparmio
- **Top 5 spese:** Le transazioni più costose del mese
- **Confronto mese precedente:** +/- per ogni categoria
- **Analisi AI:** Claude genera insights e suggerimenti personalizzati

### Pagina: Import

- **File uploader:** Drag & drop per Revolut CSV e Illimity Excel
- **Preview:** Mostra transazioni che verranno importate (esclude duplicati)
- **Conferma:** Bottone per avviare import + categorizzazione AI
- **Progress:** Barra progresso durante categorizzazione

---

## Report mensile AI

Il primo del mese (o on-demand), il sistema genera un report usando Claude.

### Prompt per report mensile

\`\`\`python
MONTHLY_REPORT_PROMPT = """Sei un financial advisor personale. Analizza le transazioni di questo mese e genera un report.

Contesto utente:
- PM in una azienda tech
- Vive a Reggio Emilia
- Va in palestra (21 Lab)
- Obiettivo: risparmiare e ottimizzare le spese

Transazioni del mese:
{transactions_json}

Budget impostati:
{budgets_json}

Spese per categoria:
{spending_by_category}

Genera un report con:
1. Riepilogo (entrate, uscite, risparmio)
2. Analisi per categoria (cosa è andato bene/male rispetto al budget)
3. Anomalie (spese insolite o picchi)
4. 3 suggerimenti concreti per risparmiare il mese prossimo
5. Un obiettivo specifico per il mese prossimo

Tono: diretto, pratico, senza giri di parole. Come un amico che ti dice le cose come stanno."""
\`\`\`

---

## Struttura progetto

\`\`\`
moneymind/
├── app.py                 # Entry point Streamlit
├── requirements.txt       # Dipendenze Python
├── .env                   # ANTHROPIC_API_KEY
├── data/
│   └── moneymind.db       # SQLite database
├── src/
│   ├── __init__.py
│   ├── database.py        # Schema e funzioni DB
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── revolut.py     # Parser CSV Revolut
│   │   └── illimity.py    # Parser Excel Illimity
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── categorizer.py # Categorizzazione Claude
│   │   └── reporter.py    # Report mensile Claude
│   └── utils.py           # Helper functions
├── pages/
│   ├── 1_📊_Transactions.py
│   ├── 2_💰_Budget.py
│   ├── 3_📥_Import.py
│   └── 4_📈_Report.py
└── tests/
    └── test_parsers.py    # Test unitari
\`\`\`

---

## Dipendenze

\`\`\`txt
streamlit>=1.28.0
pandas>=2.0.0
openpyxl>=3.1.0
plotly>=5.18.0
anthropic>=0.18.0
python-dotenv>=1.0.0
\`\`\`

---

## Setup locale

\`\`\`bash
# 1. Crea ambiente virtuale
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Configura API key
echo ANTHROPIC_API_KEY=sk-ant-xxx > .env

# 4. Lancia app
streamlit run app.py

# App disponibile su http://localhost:8501
\`\`\`

---

## Considerazioni tecniche

### Privacy

Tutti i dati restano sul computer locale. Il database SQLite è un file locale. L'unico dato che esce è il testo delle transazioni inviato a Claude per categorizzazione — nessun dato bancario sensibile (IBAN, numeri conto) viene mai trasmesso.

### Costi Claude API

Stimando ~200 transazioni/mese, con categorizzazione batch (10 transazioni per chiamata), servono ~20 chiamate/mese. A ~\$0.003/1k token input e ~\$0.015/1k token output, il costo mensile è stimato < \$1.

### Deduplicazione

Ogni transazione viene hashata (SHA256 di data + importo + descrizione + banca). L'hash viene salvato nel DB. All'import, le transazioni con hash già presenti vengono ignorate. Questo permette di ricaricare lo stesso file senza creare duplicati.

### Fallback categorizzazione

Se Claude non risponde o dà errore, la transazione viene categorizzata come "Altro". L'utente può sempre modificare manualmente dalla pagina Transazioni.

### Rate limiting

Implementare retry con exponential backoff per le chiamate Claude API:

\`\`\`python
import time
from anthropic import RateLimitError

def call_claude_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.messages.create(...)
        except RateLimitError:
            wait_time = 2 ** attempt
            time.sleep(wait_time)
    return None  # Fallback to "Altro"
\`\`\`

---

## File di esempio per test

### Revolut CSV (prime righe)

\`\`\`csv
tx_id,account,timestamp,amount,fee,balance,currency,description,category,tags,note,type,product
362ac81ca1ced650...,REV_SAV,1722497571,0.7,0.0,2.91,EUR,EUR Risparmio,Spesa,Spesa,,TRANSFER,Savings
edd98aeaa79c83fe...,REV_CUR,1722511809,-18.54,0.0,156.32,EUR,OnlyFans,Spesa,Spesa,,CARD_PAYMENT,Current
\`\`\`

### Illimity Excel (struttura)

- Righe 1-15: Metadata (intestazione report, info conto)
- Riga 16: Header colonne
- Righe 17+: Dati transazioni

\`\`\`
Data operazione | Tipologia | Causale | Stato | Entrate | Uscite | Valuta | Rapporto
2025-07-31 | Bonifico istantaneo altri paesi | Trasferimento | Eseguito | | 240.00 | EUR | T252550576960
\`\`\`
