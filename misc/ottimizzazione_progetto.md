# Istruzioni per Audit e Ottimizzazione Progetto (Best Practices)

Sei incaricato di analizzare il progetto corrente e proporre un piano per allinearlo alle "Best Practices" di sviluppo con agenti AI, basandoti sui principi di Context Management, Progressive Disclosure e il sistema PSB (Plan, Setup, Build).

## OBIETTIVO
Trasformare il flusso di lavoro attuale per massimizzare l'efficienza, ridurre l'uso inutile di token e garantire una memoria persistente del progetto.

---

## FASE 1: AUDIT DELLA DOCUMENTAZIONE ("Memoria del Progetto")

Analizza la struttura attuale dei file e verifica la presenza dei seguenti documenti essenziali. Se mancano, aggiungili al piano di implementazione.

### 1. File `claude.md` (La Memoria Principale)
Verifica se esiste un file `claude.md` alla radice.
- **Best Practice:** Questo file deve essere conciso e contenere solo le informazioni critiche (obiettivi, stile di codice, regole di sicurezza). Non deve essere sovraccarico.
- **Azione:** Deve linkare a file esterni per i dettagli, invece di contenerli tutti.

### 2. Documentazione Esterna (Progressive Disclosure)
Verifica la presenza di questi file specifici per scaricare il contesto:
- **`architecture.md`:** Panoramica del design del sistema, struttura delle cartelle e interazione tra componenti.
- **`project_status.md`:** Deve tracciare le milestone, cosa è stato fatto e dove ci siamo interrotti (utile per riprendere il lavoro dopo una pausa).
- **`changelog.md`:** Lista delle modifiche e delle funzionalità aggiunte nel tempo.
- **`tech_stack.md`:** Definizioni esplicite delle tecnologie usate (es. framework, database, librerie) per evitare allucinazioni su stack non desiderati.

---

## FASE 2: AUDIT DELLE SPECIFICHE (Pianificazione)

Non scrivere codice senza una specifica chiara. Verifica se abbiamo risposto alle "Due Domande Critiche":
1. **Qual è l'obiettivo esatto del progetto?** (Prototipo vs Produzione).
2. **Quali sono le milestone di funzionalità?** (MVP, v1, v2).

**Azione:** Se queste informazioni non sono chiare nei file attuali, chiedimi di definire un **Project Spec Doc** che includa:
- **Product Requirements:** Chi è l'utente? Quale problema risolve?
- **Engineering Design:** Come lo costruiamo? (Schema DB, API design).

---

## FASE 3: AUDIT DEGLI STRUMENTI E SKILLS

### 1. Struttura a "Skills"
Invece di strumenti monolitici, verifica se possiamo organizzare le capacità complesse in **Skills** (cartelle contenenti `skill.md` e script dedicati).
- **Esempio:** Se il progetto richiede analisi dati complessa o gestione documenti, crea una skill dedicata che venga caricata nel contesto solo quando necessario.

### 2. Configurazione MCP e Plugin
Verifica se stiamo usando i server MCP (Model Context Protocol) appropriati per il progetto:
- Accesso al Database (es. PostgreSQL, SQLite).
- Accesso al Browser (es. Puppeteer/Playwright) per test end-to-end.
- Integrazione Git/GitHub per la gestione delle issue.

---

## FASE 4: DEFINIZIONE DEL WORKFLOW OPERATIVO

Stabilisci le seguenti regole per le sessioni future:

1. **Plan Mode First:** Ogni nuova funzionalità complessa deve iniziare in modalità planning per delineare i passaggi prima dell'esecuzione.
2. **Issue-Based Development:** Usare le GitHub Issues (o un file `todo.md` locale) come singola fonte di verità per i task.
3. **Automated Documentation:** Aggiornare automaticamente `architecture.md` e `project_status.md` al termine di ogni sessione significativa.
4. **Prevention & Reflection:** Se viene commesso un errore, aggiornare `claude.md` con una regola "Lesson Learned" per evitare di ripeterlo.

---

## OUTPUT RICHIESTO (IL TUO PIANO)

Basandoti su questo file, analizza la cartella corrente e restituisci un piano numerato:
1. Elenca i file di documentazione mancanti che creerai.
2. Elenca le informazioni che ti servono da me (es. Tech Stack preferito, Obiettivo MVP).
3. Proponi una struttura di cartelle aggiornata.
4. Definisci i primi 3 task operativi da eseguire.