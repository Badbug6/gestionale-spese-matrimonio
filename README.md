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
    -   [La Dashboard Principale](#la-dashboard-principale)
    -   [Gestire Spese e Pagamenti](#gestire-spese-e-pagamenti)
    -   [Usare lo Scadenzario e il Calendario](#usare-lo-scadenzario-e-il-calendario)
    -   [Amministrazione: Categorie, Utenti e Impostazioni Email](#amministrazione-categorie-utenti-e-impostazioni-email)
6.  [👨‍💻 Angolo dello Sviluppatore](#-angolo-dello-sviluppatore)
7.  [🛣️ Roadmap e Contributi](#-roadmap-e-contributi)
8.  [📜 Licenza](#-licenza)

---

## ✨ Filosofia del Progetto

L'obiettivo di questo gestionale è offrire uno strumento **centralizzato, bello e proattivo** che risolva i problemi pratici della pianificazione di un matrimonio:
-   **Chiarezza Finanziaria:** Distinguere nettamente tra *costi previsti* e *uscite di cassa effettive* (acconti, saldi).
-   **Visione Temporale:** Avere sempre sott'occhio le prossime scadenze grazie a un calendario interattivo.
-   **Automazione Intelligente:** Inviare promemoria automatici per non dimenticare mai un pagamento o un compito importante.
-   **Semplicità d'Uso:** Fornire un'interfaccia che non richieda competenze tecniche per essere utilizzata.
-   **Robustezza e Universalità:** Essere un'applicazione stabile, sicura e funzionante su qualsiasi sistema operativo.

---

## 🚀 Funzionalità Chiave

-   📊 **Dashboard Riepilogativa:** Visione d'insieme con budget totale, costo previsto, importo già pagato e budget rimanente.
-   💸 **Gestione Spese Unificata:** Ogni spesa ha una sua pagina dedicata per modificare i dettagli e tracciare tutti gli acconti e i pagamenti.
-   🗓️ **Calendario Interattivo delle Scadenze:** Una vista mensile con tutti i task e le scadenze, con link diretti alle spese associate.
-   🔔 **Promemoria Automatici via Email:** Un sistema intelligente che invia un'email stilizzata a tutti gli utenti registrati 7 giorni prima di una scadenza.
-   🥧 **Grafico Dinamico:** Un grafico a torta per visualizzare la distribuzione percentuale dei costi previsti per categoria.
-   👥 **Gestione Multi-Utente:** Supporto per più utenti, ognuno con il proprio account e la propria email per le notifiche.
-   🔐 **Pannello di Amministrazione Completo:** Aree dedicate per gestire categorie, utenti e configurare le impostazioni di invio delle email (SMTP).
-   📦 **Pronto per la Produzione:** Utilizza il server WSGI **Waitress** per un'esecuzione robusta e compatibile con Windows, macOS e Linux.

---

## 🛠️ Stack Tecnologico

-   **Backend:**
    -   **Linguaggio:** Python 3
    -   **Framework:** Flask
    -   **Server WSGI di Produzione:** Waitress
    -   **Database:** SQLite 3 (integrato)
    -   **Invio Email:** Flask-Mail
    -   **Task Scheduler:** APScheduler
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

### 1. Clona il Repository```bash
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
Al primo avvio, verrai guidato attraverso due passaggi obbligatori:
1.  **Creazione dell'Utente Amministratore:** Inserisci un nome utente, una **email valida** e una password. L'email è fondamentale per ricevere le notifiche.
2.  **Impostazione del Budget:** Definisci l'importo totale che prevedi di spendere.

Una volta completati, effettua il login per accedere alla dashboard.

### La Dashboard Principale
È il tuo centro di controllo con il riepilogo finanziario, il form per aggiungere nuove spese, il grafico a torta e la tabella con l'elenco di tutte le spese inserite.

### Gestire Spese e Pagamenti
Il flusso di lavoro è stato semplificato:
1.  **Aggiungi una Spesa:** Dalla dashboard, inserisci una nuova voce con il suo **costo totale previsto** (es. `Fotografo`, `2000€`).
2.  **Gestisci la Spesa:** Clicca sulla spesa appena creata nella tabella in basso. Verrai reindirizzato alla sua **pagina di gestione unificata**.
3.  **In questa pagina puoi:**
    -   Modificare i dettagli principali (descrizione, importo totale, categoria).
    -   Visualizzare il riepilogo dei pagamenti (costo, pagato, residuo).
    -   Aggiungere nuovi acconti o saldi nel form dedicato.
    -   Consultare lo storico di tutti i pagamenti effettuati per quella spesa.

### Usare lo Scadenzario e il Calendario
1.  **Crea una Scadenza:** Dalla pagina "Scadenzario", aggiungi un compito (es. "Scegliere le bomboniere") con una data.
2.  **Associa a una Spesa (Opzionale):** Puoi collegare la scadenza a una spesa esistente per avere un link diretto.
3.  **Visualizza sul Calendario:** Il calendario nella pagina "Scadenzario" mostrerà tutti i tuoi impegni. Cliccando su un evento associato a una spesa, verrai portato alla sua pagina di gestione.
4.  **Completa un Compito:** Nella lista testuale dello scadenzario, clicca sul pulsante `✓` per segnare un compito come completato. L'evento nel calendario diventerà verde.

### Amministrazione: Categorie, Utenti e Impostazioni Email
L'amministratore ha accesso a tre pagine chiave dalla barra di navigazione:
-   **Gestione Categorie:** Aggiungi, rinomina o elimina le categorie di spesa in un'interfaccia a schede moderna e intuitiva.
-   **Gestione Utenti:** Visualizza tutti gli utenti registrati e aggiungine di nuovi.
-   **Impostazioni:** **(Passaggio Fondamentale)** Configura le credenziali del server SMTP per abilitare l'invio dei promemoria.
    -   Inserisci i dati del tuo provider di posta (es. `smtp.gmail.com`, porta `587`).
    -   **Nota per Gmail:** È necessario usare una **"Password per le app"**. Cerca "Google App Passwords" per crearne una.
    -   Usa i pulsanti di test per verificare che la configurazione sia corretta e per vedere un'anteprima dell'email di promemoria.

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
│   ├── style.css       # Il foglio di stile principale
│   └── script.js       # Logica JavaScript per la dashboard
└── templates/
    ├── index.html      # Pagina principale (Dashboard)
    ├── edit.html       # Pagina di gestione unificata per spese e pagamenti
    └── email/
        └── reminder.html # Template HTML per le email di promemoria
    └── ... (altri template)
```

### Avvio in Modalità Sviluppo (con Debug)
Per attivare il debugger di Flask, imposta la variabile d'ambiente `FLASK_DEBUG` a `true` prima di avviare l'app.
-   **macOS/Linux:** `export FLASK_DEBUG=true && python app.py`
-   **Windows (CMD):** `set FLASK_DEBUG=true && python app.py`
-   **Windows (PowerShell):** `$env:FLASK_DEBUG="true"; python app.py`

### Decisioni Architetturali
-   **Flask:** Scelto per la sua leggerezza e flessibilità.
-   **SQLite:** Selezionato perché è un database self-contained che non richiede un server separato.
-   **APScheduler:** Integrato per gestire l'esecuzione di compiti programmati (invio giornaliero dei reminder) in background.
-   **Flask-Mail:** Utilizzato per astrarre la complessità dell'invio di email tramite SMTP.
-   **Vanilla JavaScript:** L'interazione dinamica sulla dashboard è gestita con JavaScript puro per mantenere il frontend leggero.

---

## 🛣️ Roadmap e Contributi

-   [X] **Upload di File:** Caricare contratti/ricevute per ogni spesa.
-   [ ] **Gestione Invitati:** Una nuova sezione per tracciare gli invitati, le conferme e la disposizione dei tavoli.
-   [X] **Dashboard Migliorata:** Aggiungere più grafici (es. andamento dei pagamenti nel tempo).
-   [X] **Test Unitari e di Integrazione:** Aumentare la copertura dei test.

I contributi sono benvenuti! Sentiti libero di aprire una issue o inviare una pull request.

---

## 📜 Licenza
Questo progetto è rilasciato sotto la **Licenza MIT**.