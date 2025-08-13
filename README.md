```markdown
# 💒 Gestionale Spese Matrimonio

### Il Tuo Wedding Planner Personale e Definitivo

Un'applicazione web completa per la pianificazione finanziaria, logistica e documentale del vostro matrimonio.

Costruita con **Python/Flask** e **JavaScript**,
offre un'esperienza utente moderna e un design elegante "glassmorphism", facile da usare e da mantenere.

---

### ✨ Funzionalità Chiave

-   **📊 Dashboard Centrale**
    Controllo totale su budget, spese e andamenti finanziari.

-   **💸 Gestione Spesa Completa**
    Traccia pagamenti, acconti e allegati in un'unica pagina per ogni spesa.

-   **📄 Archivio Documenti**
    Carica contratti e ricevute per ogni singola voce di costo.

-   **🗓️ Calendario Interattivo**
    Visualizza e gestisci tutte le tue scadenze in una comoda vista mensile.

-   **🔔 Email Reminder Automatici**
    Ricevi notifiche via email 7 giorni prima di ogni scadenza.

-   **💡 Pagamenti da Scadenze**
    Collega un importo a una scadenza per registrare pagamenti automatici.

-   **📈 Grafici Dinamici**
    Passa con un click dalla vista per categoria (torta) a quella temporale (linee).

-   **👥 Supporto Multi-Utente**
    Gestisci più utenti con notifiche email individuali.

-   **🔐 Pannello Admin**
    Amministra facilmente utenti, categorie e impostazioni email.

-   **✅ Codice Testato**
    Stabilità garantita da una suite di test automatici con **pytest**.

-   **📦 Pronto per la Produzione**
    Server WSGI **Waitress** integrato per la massima stabilità.

---

### 🛠️ Stack Tecnologico

-   **Backend:**
    -   Python 3, Flask
    -   Waitress (Server WSGI)
    -   SQLite 3 (Database)
    -   Flask-Mail, APScheduler

-   **Frontend:**
    -   HTML5, CSS3, JavaScript (vanilla)
    -   Chart.js, FullCalendar

-   **Testing:**
    -   pytest

---

### 🏁 Installazione Rapida

#### Prerequisiti
-   Python 3.8+
-   Git

#### 1. Clona il Repository
```bash
git clone https://github.com/Badbug6/gestionale-spese-matrimonio.git
cd gestionale-spese-matrimonio
```

#### 2. Crea e Attiva un Ambiente Virtuale
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
```

#### 3. Installa le Dipendenze
```bash
pip install -r requirements.txt
```

#### 4. Avvia l'Applicazione
```bash
python app.py
```
Apri il browser all'indirizzo **`http://127.0.0.1:5001`**.

---

### 📖 Manuale d'Uso

#### Primo Avvio
1.  **Crea Utente Admin:** Inserisci username, email e password.
2.  **Imposta Budget:** Definisci il budget totale previsto.

#### Flusso di Lavoro
1.  **Aggiungi una Spesa:** Dalla dashboard, inserisci una voce con il suo costo totale.
2.  **Gestisci la Spesa:** Clicca sulla spesa nella tabella. Nella sua pagina dedicata potrai:
    -   Modificare i dettagli.
    -   Aggiungere acconti.
    -   Caricare file.

#### Configurazione Email
Vai in **Impostazioni** (solo admin) per configurare le credenziali SMTP. Questo passaggio è **fondamentale** per abilitare i promemoria.

---

### 👨‍💻 Angolo dello Sviluppatore

#### Struttura del Progetto
```
.
├── app.py              # Logica Flask e route
├── test_app.py         # Test automatici
├── requirements.txt    # Dipendenze
├── README.md           # Questo file
├── wedding.db          # Database
├── uploads/            # File caricati
├── static/             # CSS e JS
└── templates/          # File HTML
```

#### Modalità Sviluppo (Debug)
-   **macOS/Linux:** `export FLASK_DEBUG=true && python app.py`
-   **Windows:** `set FLASK_DEBUG=true && python app.py`

#### Esecuzione dei Test
```bash
pytest
```

---

### 🛣️ Roadmap

-   [ ] **Gestione Invitati:** Una nuova sezione per tracciare invitati e conferme.
-   [ ] **Espandere i Test:** Aggiungere test per le API e la gestione delle spese.
-   [ ] **Internazionalizzazione (i18n):** Tradurre l'interfaccia.

I contributi sono benvenuti!

---

### 📜 Licenza
Questo progetto è rilasciato sotto la **Licenza MIT**.
