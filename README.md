# 💒 Gestionale Spese Matrimonio: Il Tuo Wedding Planner Personale

Dite addio a fogli di calcolo complicati e note sparse. Questa applicazione web completa è stata progettata per essere il centro di controllo definitivo per la pianificazione finanziaria e logistica del vostro matrimonio.

Costruita con un backend robusto in **Python/Flask** e un frontend dinamico in **JavaScript**, l'applicazione offre un'esperienza utente fluida e moderna, racchiusa in un design elegante "glassmorphism" con uno sfondo animato. È pensata per essere intuitiva per gli utenti finali e al tempo stesso chiara e manutenibile per gli sviluppatori.

---

## 📜 Indice

1.  [✨ Filosofia del Progetto](#-filosofia-del-progetto)
2.  [🚀 Funzionalità Chiave](#-funzionalità-chiave)
3.  [🛠️ Stack Tecnologico](#-stack-tecnologico)
4.  [🏁 Guida Rapida all'Installazione](#-guida-rapida-allinstallazione)
5.  [📖 Manuale d'Uso Dettagliato](#-manuale-duso-dettagliato)
    -   [Primo Avvio: Configurazione Iniziale](#primo-avvio-configurazione-iniziale)
    -   [La Dashboard Principale: Il Tuo Centro di Controllo](#la-dashboard-principale-il-tuo-centro-di-controllo)
    -   [Come Gestire Spese e Pagamenti](#come-gestire-spese-e-pagamenti-il-flusso-di-lavoro-principale)
    -   [Come Usare lo Scadenzario e il Calendario](#come-usare-lo-scadenzario-e-il-calendario)
    -   [Amministrazione: Gestire Categorie e Utenti](#amministrazione-gestire-categorie-e-utenti)
6.  [👨‍💻 Angolo dello Sviluppatore](#-angolo-dello-sviluppatore)
    -   [Struttura del Progetto](#struttura-del-progetto)
    -   [Avvio in Modalità Sviluppo](#avvio-in-modalità-sviluppo-con-debug)
    -   [Decisioni Architetturali](#decisioni-architetturali)
7.  [🛣️ Roadmap e Contributi](#-roadmap-e-contributi)
8.  [📜 Licenza](#-licenza)

---

## ✨ Filosofia del Progetto

L'obiettivo di questo gestionale è offrire uno strumento **centralizzato, bello e funzionale** che risolva i problemi pratici della pianificazione di un matrimonio:
-   **Chiarezza Finanziaria:** Distinguere nettamente tra *costi previsti* e *uscite di cassa effettive* (acconti, saldi).
-   **Visione Temporale:** Avere sempre sott'occhio le prossime scadenze e i pagamenti da effettuare.
-   **Semplicità d'Uso:** Fornire un'interfaccia che non richieda competenze tecniche per essere utilizzata.
-   **Robustezza e Universalità:** Essere un'applicazione stabile, sicura e funzionante su qualsiasi sistema operativo.

---

## 🚀 Funzionalità Chiave

-   📊 **Dashboard Riepilogativa:** Visione d'insieme con budget totale, costo previsto, importo già pagato e budget rimanente.
-   💸 **Gestione Spese e Acconti:** Tracciamento dettagliato dei pagamenti per ogni singola spesa.
-   🗓️ **Calendario Interattivo delle Scadenze:** Una vista mensile in stile "Vikunja" con tutti i task e le scadenze, con link diretti alle spese associate.
-   📋 **Scadenzario Dedicato:** Una pagina per gestire i compiti, segnarli come completati e monitorare le prossime scadenze.
-   🥧 **Grafico Dinamico:** Un grafico a torta per visualizzare la distribuzione percentuale dei costi previsti per categoria.
-   👥 **Gestione Utenti e Categorie:** Un'area amministrativa per personalizzare l'applicazione.
-   🔐 **Autenticazione Sicura:** Sistema di registrazione e login per proteggere i dati.
-   📦 **Pronto per la Produzione:** Utilizza il server WSGI **Waitress** per un'esecuzione robusta e compatibile con Windows, macOS e Linux.

---

## 🛠️ Stack Tecnologico

-   **Backend:**
    -   **Linguaggio:** Python 3
    -   **Framework:** Flask
    -   **Server WSGI di Produzione:** Waitress
    -   **Database:** SQLite 3 (integrato, non richiede installazioni separate)
-   **Frontend:**
    -   **Linguaggi:** HTML5, CSS3, JavaScript (vanilla)
    -   **Librerie Esterne:**
        -   **Chart.js:** Per la creazione di grafici interattivi.
        -   **FullCalendar:** Per la visualizzazione del calendario delle scadenze.

---

## 🏁 Guida Rapida all'Installazione

Segui questi passaggi per avviare l'applicazione in pochi minuti.

### Prerequisiti
-   [Python 3.8+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads)

### 1. Clona il Repository
```bash
git clone https://github.com/Badbug6/gestionale-spese-matrimonio.git
cd gestionale-spese-matrimonio
```

### 2. Crea e Attiva un Ambiente Virtuale
```bash
# Crea l'ambiente
python -m venv venv

# Attiva l'ambiente
# Su Windows (CMD):
venv\Scripts\activate
# Su macOS e Linux:
source venv/bin/activate
```

### 3. Installa le Dipendenze
Tutti i pacchetti necessari sono elencati nel file `requirements.txt`.
```bash
pip install -r requirements.txt
```

### 4. Avvia l'Applicazione
L'applicazione partirà di default in **modalità produzione** con il server Waitress.
```bash
python app.py
```
Vedrai un messaggio simile a: `>>> AVVIO IN MODALITÀ PRODUZIONE CON WAITRESS...`

Apri il tuo browser e vai all'indirizzo **`http://127.0.0.1:5001`**.

---

## 📖 Manuale d'Uso Dettagliato

### Primo Avvio: Configurazione Iniziale
Al primo avvio, l'applicazione non ha dati. Verrai guidato attraverso due passaggi obbligatori:
1.  **Creazione dell'Utente Amministratore:** Inserisci un nome utente e una password per il primo account, che avrà pieni poteri.
2.  **Impostazione del Budget:** Definisci l'importo totale che prevedi di spendere per il matrimonio.

Una volta completati, accederai alla dashboard principale.

### La Dashboard Principale: Il Tuo Centro di Controllo
La pagina principale è divisa in quattro sezioni:

1.  **Riepilogo Finanziario (in alto):**
    -   `Budget Totale`: La cifra che hai impostato all'inizio.
    -   `Pagato Finora`: La somma di tutti gli acconti e saldi che hai effettivamente pagato. Rappresenta l'uscita di cassa reale.
    -   `Costo Previsto`: La somma dei costi totali di tutte le spese che hai inserito.
    -   `Budget Rimanente`: La differenza tra il tuo `Budget Totale` e il `Costo Previsto`.

2.  **Aggiunta e Grafico (al centro):**
    -   **Aggiungi Spesa:** Usa questo form per inserire una nuova voce di costo (es. "Abito da sposa"). Inserisci il **costo totale previsto**, non un acconto.
    -   **Spese per Categoria:** Il grafico a torta si aggiorna dinamicamente per mostrarti come i costi previsti sono distribuiti.

3.  **Calendario Scadenze (metà pagina):**
    -   Questa vista mensile mostra tutti i compiti e le scadenze inserite nello "Scadenzario".
    -   Le scadenze completate sono in **verde**.
    -   Se una scadenza è collegata a una spesa, **puoi cliccarci sopra** per essere reindirizzato alla pagina di dettaglio di quella spesa.

4.  **Dettaglio Spese (in basso):**
    -   Questa tabella elenca tutte le spese inserite. Per ogni spesa, mostra il costo previsto, quanto hai già pagato e quanto resta da pagare.

### Come Gestire Spese e Pagamenti (Il flusso di lavoro principale)
1.  **Aggiungi una Spesa:** Inserisci una nuova voce di spesa con il suo **costo totale**. Esempio: `Descrizione: Fotografo`, `Costo Totale Previsto: 2000`.
2.  **Vai al Dettaglio:** Nella tabella in basso, trova la spesa "Fotografo" e clicca sull'icona a forma di block-notes (📋).
3.  **Registra un Pagamento:** Nella pagina di dettaglio, vedrai che il "Totale Pagato" è zero. Usa il form "Registra un Acconto/Pagamento" per inserire il primo pagamento. Esempio: `Importo Pagato: 500`, `Data: ...`, `Note: Caparra`.
4.  **Verifica l'Aggiornamento:** Torna alla dashboard. Vedrai che il "Pagato Finora" generale è aumentato di 500, e nella tabella la riga del fotografo mostrerà `Pagato: € 500.00`, `Rimanente: € 1500.00`.

### Come Usare lo Scadenzario e il Calendario
1.  **Crea una Scadenza:** Clicca sul link "Scadenzario" nella navigazione.
2.  Usa il form per aggiungere un compito, come "Scegliere le bomboniere". Imposta una data di scadenza.
3.  **Associa a una Spesa (Opzionale):** Se hai già creato la spesa "Bomboniere", puoi associarla dal menu a tendina.
4.  **Visualizza sul Calendario:** Torna alla home. Vedrai l'evento "Scegliere le bomboniere" nel calendario. Se l'hai associato, cliccandoci sopra andrai alla pagina di dettaglio della spesa "Bomboniere".
5.  **Completa un Compito:** Nello scadenzario, clicca sul cerchio (⚪) per segnare il compito come completato (✔). L'evento nel calendario diventerà verde.

### Amministrazione: Gestire Categorie e Utenti
Nei link in alto, puoi accedere a due pagine amministrative:
-   **Gestisci Categorie:** Aggiungi, rinomina o elimina le categorie di spesa. Non puoi eliminare una categoria se è già utilizzata da una spesa.
-   **Gestisci Utenti:** Visualizza tutti gli utenti registrati.

---

## 👨‍💻 Angolo dello Sviluppatore

### Struttura del Progetto
```
.
├── app.py              # File principale con la logica Flask e le route
├── requirements.txt    # Elenco delle dipendenze Python
├── README.md           # Questo file
├── wedding.db          # Il file del database SQLite (creato al primo avvio)
├── static/
│   └── style.css       # Il foglio di stile principale
└── templates/
    ├── index.html      # Pagina principale (Dashboard)
    ├── scadenzario.html# Pagina di gestione dei compiti
    ├── spesa_detail.html # Pagina di dettaglio per registrare acconti
    ├── categories.html # Pagina di gestione categorie
    ├── manage_users.html # Pagina di gestione utenti
    └── ... (altri template per login, register, setup, etc.)
```

### Avvio in Modalità Sviluppo (con Debug)
Per attivare il debugger di Flask, imposta la variabile d'ambiente `FLASK_DEBUG` a `true` prima di avviare l'app.
-   **macOS/Linux:** `export FLASK_DEBUG=true && python app.py`
-   **Windows (CMD):** `set FLASK_DEBUG=true && python app.py`
-   **Windows (PowerShell):** `$env:FLASK_DEBUG="true"; python app.py`

### Decisioni Architetturali
-   **Flask:** Scelto per la sua leggerezza e flessibilità, ideale per progetti che partono piccoli ma possono crescere.
-   **SQLite:** Selezionato perché è un database self-contained che non richiede un server separato, rendendo l'installazione e la distribuzione estremamente semplici.
-   **Waitress:** Adottato come server di produzione per la sua compatibilità cross-platform e la sua stabilità superiore rispetto al server di sviluppo di Flask.
-   **Vanilla JavaScript:** L'interazione dinamica sulla dashboard (aggiornamento UI, chiamate API) è gestita con JavaScript puro per mantenere il frontend leggero e senza dipendenze da framework complessi come React o Vue.

---

## 🛣️ Roadmap e Contributi

Questo progetto è un'ottima base, ma ci sono molte funzionalità che potrebbero essere aggiunte in futuro.

-   [ ] **Upload di File:** Caricare contratti/ricevute per ogni spesa.
-   [ ] **Notifiche via Email:** Inviare un promemoria via email per le scadenze imminenti.
-   [ ] **Internazionalizzazione (i18n):** Tradurre l'interfaccia in altre lingue.
-   [ ] **Test Unitari e di Integrazione:** Aumentare la copertura dei test per garantire la stabilità del codice.

I contributi sono benvenuti! Sentiti libero di aprire una issue o inviare una pull request.

---

## 📜 Licenza
Questo progetto è rilasciato sotto la **Licenza MIT**.