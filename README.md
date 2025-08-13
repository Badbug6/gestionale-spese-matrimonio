```markdown
💒 Gestionale Spese Matrimonio: Il Tuo Wedding Planner Personale

Dite addio a fogli di calcolo complicati e note sparse.
Questa applicazione web completa è stata progettata per essere il centro di controllo
definitivo per la pianificazione finanziaria, logistica e documentale del vostro matrimonio.

Costruita con un backend robusto in **Python/Flask** e un frontend dinamico in **JavaScript**, l'applicazione offre un'esperienza utente fluida e moderna,
racchiusa in un design elegante "glassmorphism" con uno sfondo animato.
È pensata per essere intuitiva per gli utenti finali e al tempo stesso chiara, testata e manutenibile per gli sviluppatori.


📜 Indice

1.  [✨ Filosofia del Progetto](#-filosofia-del-progetto)
2.  [🚀 Funzionalità Chiave](#-funzionalità-chiave)
3.  [🛠️ Stack Tecnologico](#-stack-tecnologico)
4.  [🏁 Guida Rapida all'Installazione](#-guida-rapida-allinstallazione)
5.  [📖 Manuale d'Uso Dettagliato](#-manuale-duso-dettagliato)
6.  [👨‍💻 Angolo dello Sviluppatore](#-angolo-dello-sviluppatore)
    -   [Struttura del Progetto](#struttura-del-progetto)
    -   [Avvio in Modalità Sviluppo](#avvio-in-modalità-sviluppo-con-debug)
    -   [Esecuzione dei Test](#esecuzione-dei-test)
7.  [🛣️ Roadmap e Contributi](#-roadmap-e-contributi)
8.  [📜 Licenza](#-licenza)

✨ Filosofia del Progetto

L'obiettivo di questo gestionale è offrire uno strumento **centralizzato, bello e proattivo** che risolva i problemi pratici della pianificazione di un matrimonio:
-   **Chiarezza Finanziaria:** Distinguere nettamente tra *costi previsti* e *uscite di cassa effettive*.
-   **Visione Temporale:** Avere sempre sott'occhio le prossime scadenze grazie a un calendario interattivo.
-   **Archiviazione Semplice:** Centralizzare tutti i documenti importanti (contratti, ricevute) legandoli direttamente alla spesa corrispondente.
-   **Automazione Intelligente:** Inviare promemoria automatici per non dimenticare mai un pagamento o un compito importante.
-   **Robustezza e Stabilità:** Garantire che le nuove modifiche non rompano le funzionalità esistenti grazie a una suite di test automatici.

🚀 Funzionalità Chiave

-   📊 **Dashboard Riepilogativa:** Visione d'insieme con budget totale, costo previsto, importo già pagato e rimanente.
-   💸 **Gestione Spese Unificata:** Ogni spesa ha una sua pagina dedicata per modificare i dettagli, tracciare tutti gli acconti e i pagamenti.
-   📄 **Gestione Allegati:** Carica, visualizza ed elimina file (contratti, ricevute) per ogni singola spesa, creando un archivio digitale centralizzato.
-   🗓️ **Calendario Interattivo delle Scadenze:** Una vista mensile con tutti i task e le scadenze, con link diretti alle spese associate.
-   🔔 **Promemoria Automatici via Email:** Un sistema intelligente che invia un'email stilizzata 7 giorni prima di una scadenza a tutti gli utenti registrati.
-   💡 **Pagamenti Intelligenti da Scadenze:** Possibilità di associare un importo a una scadenza (es. una rata). Completando la scadenza, il pagamento viene registrato automaticamente. L'azione è reversibile.
-   📈 **Grafici Dinamici con Switch:** Un pannello unificato nella dashboard permette di visualizzare con un click sia la **distribuzione dei costi per categoria** (grafico a torta) sia l'**andamento dei pagamenti nel tempo** (grafico a linee).
-   👥 **Gestione Multi-Utente:** Supporto per più utenti, ognuno con il proprio account e la propria email per le notifiche.
-   🔐 **Pannello di Amministrazione Completo:** Aree dedicate per gestire categorie, utenti e configurare le impostazioni di invio delle email (SMTP).
-   ✅ **Testato Automaticamente:** Una suite di test con **pytest** garantisce che le funzionalità critiche (come l'autenticazione) siano sempre funzionanti.
-   📦 **Pronto per la Produzione:** Utilizza il server WSGI **Waitress** per un'esecuzione robusta e cross-platform.

🛠️ Stack Tecnologico

-   **Backend:**
    -   **Linguaggio:** Python 3
    -   **Framework:** Flask
    -   **Server WSGI di Produzione:** Waitress
    -   **Database:** SQLite 3
    -   **Invio Email:** Flask-Mail
    -   **Task Scheduler:** APScheduler
-   **Frontend:**
    -   **Linguaggi:** HTML5, CSS3, JavaScript (vanilla)
    -   **Librerie:** Chart.js, FullCalendar
-   **Sviluppo & Testing:**
    -   **Test Framework:** pytest

🏁 Guida Rapida all'Installazione

### Prerequisiti
-   [Python 3.8+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads)

1. Clona il Repository
```bash
git clone https://github.com/Badbug6/gestionale-spese-matrimonio.git
cd gestionale-spese-matrimonio
```

2. Crea e Attiva un Ambiente Virtuale
```bash
python -m venv venv
# Su Windows (CMD): venv\Scripts\activate
# Su macOS/Linux: source venv/bin/activate
```

### 3. Installa le Dipendenze
```bash
pip install -r requirements.txt
```

### 4. Avvia l'Applicazione
```bash
python app.py
```
Apri il browser e vai all'indirizzo **`http://127.0.0.1:5001`**.

📖 Manuale d'Uso Dettagliato

Primo Avvio: Configurazione Iniziale
Al primo avvio, verrai guidato attraverso due passaggi obbligatori:
1.  **Creazione dell'Utente Amministratore:** Inserisci un nome utente, una **email valida** e una password. L'email è fondamentale per le notifiche.
2.  **Impostazione del Budget:** Definisci l'importo totale che prevedi di spendere.

Dopo il login, accedi alla dashboard.

Il Flusso di Lavoro Principale
1.  **Aggiungi una Spesa:** Dalla dashboard, inserisci una nuova voce con il suo **costo totale previsto** (es. `Fotografo`, `2000€`).
2.  **Gestisci la Spesa:** Clicca sulla spesa appena creata nella tabella in basso. Verrai reindirizzato alla sua **pagina di gestione unificata**.
3.  **In questa pagina puoi fare tutto:**
    -   **Modificare** i dettagli principali (descrizione, importo, categoria).
    -   **Aggiungere** acconti o saldi nel form "Gestione Pagamenti".
    -   **Eliminare** pagamenti inseriti per errore.
    -   **Caricare** file importanti (contratti, ricevute) nel pannello "Gestione Allegati".
    -   **Visualizzare** e scaricare gli allegati già presenti.

Usare lo Scadenzario e i Pagamenti Automatici
1.  **Crea una Scadenza:** Dalla pagina "Scadenzario", aggiungi un compito (es. "Pagare rata fotografo").
2.  **Imposta un Importo (Opzionale):** Nel campo "Importo Rata", inserisci la cifra corrispondente (es. `500`).
3.  **Associa alla Spesa:** Collega la scadenza alla spesa "Fotografo".
4.  **Completa la Scadenza:** Quando arriva il momento, vai nello scadenzario e clicca sul pulsante `✓`. L'applicazione **creerà automaticamente** un pagamento di 500€ nella pagina della spesa "Fotografo". Se cambi idea, ti basta cliccare di nuovo sul pulsante per annullare sia il completamento che il pagamento.

Amministrazione
L'amministratore può accedere a:
-   **Gestione Categorie:** Per personalizzare le categorie di spesa.
-   **Gestione Utenti:** Per visualizzare e aggiungere nuovi utenti.
-   **Impostazioni:** **(Fondamentale)** Per configurare le credenziali del server SMTP e abilitare l'invio delle email.

👨‍💻 Angolo dello Sviluppatore

Struttura del Progetto
```
.
├── app.py              # File principale con la logica Flask e le route
├── test_app.py         # Contiene i test automatici con pytest
├── requirements.txt    # Elenco delle dipendenze Python
├── README.md           # Questo file
├── wedding.db          # Il file del database (creato al primo avvio)
├── uploads/            # Cartella per i file caricati
├── static/
│   ├── style.css
│   └── script.js
└── templates/
    ├── index.html
    └── email/
        └── reminder.html
    └── ... (altri template)
```

Avvio in Modalità Sviluppo (con Debug)
Per attivare il debugger di Flask, imposta la variabile d'ambiente `FLASK_DEBUG` a `true`.
-   **macOS/Linux:** `export FLASK_DEBUG=true && python app.py`
-   **Windows (CMD):** `set FLASK_DEBUG=true && python app.py`

Esecuzione dei Test
Questo progetto utilizza **pytest**. Per eseguire la suite di test:
```bash
pytest
```

🛣️ Roadmap e Contributi
-   [ ] **Gestione Invitati:** Una nuova sezione per tracciare gli invitati, le conferme e la disposizione dei tavoli.
-   [ ] **Espandere la Copertura dei Test:** Aggiungere test per le API, la gestione delle spese e dei pagamenti.
-   [ ] **Internazionalizzazione (i18n):** Tradurre l'interfaccia in altre lingue.

I contributi sono benvenuti!


📜 Licenza
Questo progetto è rilasciato sotto la **Licenza MIT**.
