from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import json
import os # Importiamo il modulo 'os' per controllare l'esistenza dei file

app = Flask(__name__)

DATABASE = 'wedding.db'
# Rimuoviamo la costante BUDGET_TOTALE da qui, la leggeremo dal database

# --- GESTIONE DATABASE (invariata) ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- NUOVA FUNZIONE (CORRETTA) ---
@app.before_request
def check_for_setup():
    # Controlla se il DB non esiste
    if not os.path.exists(DATABASE):
        # Se non esiste, permetti l'accesso SOLO alla pagina di setup
        # E ai file statici (altrimenti non carica il CSS!).
        if request.endpoint != 'setup' and request.endpoint != 'static':
            return redirect(url_for('setup'))

# --- NUOVA ROUTE PER IL SETUP ---
@app.route('/setup', methods=['GET', 'POST'])
def setup():
    # Se il database esiste già, non permettere di accedere a /setup
    if os.path.exists(DATABASE):
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Prendiamo il budget dal form
        budget_iniziale = request.form['budget']

        # Creiamo il database e le tabelle
        db = get_db()
        cursor = db.cursor()
        
        # 1. Tabella delle spese (come in database.py)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS spese (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descrizione TEXT NOT NULL,
            importo REAL NOT NULL,
            categoria TEXT NOT NULL,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 2. NUOVA tabella per la configurazione
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        ''')
        
        # 3. Inseriamo il budget nella tabella di configurazione
        cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", ('budget', budget_iniziale))
        
        db.commit()
        
        # Reindirizziamo alla pagina principale, che ora funzionerà
        return redirect(url_for('index'))

    # Se la richiesta è GET, mostriamo la pagina di setup
    return render_template('setup.html')


# Funzione helper per leggere il budget dal DB
def get_budget_from_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT value FROM config WHERE key = 'budget'")
    result = cursor.fetchone()
    return float(result['value']) if result else 0.0


# --- ROUTES PRINCIPALI (MODIFICATE) ---
@app.route('/')
def index():
    # Se il db non esiste, il before_request ci avrà già reindirizzato
    
    # Leggiamo il budget dal DB invece che dalla costante
    budget_totale = get_budget_from_db()

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM spese ORDER BY data DESC")
    spese = cursor.fetchall()

    speso_totale = sum(s['importo'] for s in spese)
    rimanente = budget_totale - speso_totale

    spese_per_categoria = {}
    for spesa in spese:
        cat = spesa['categoria']
        imp = spesa['importo']
        spese_per_categoria[cat] = spese_per_categoria.get(cat, 0) + imp

    # Preparazione dati per il grafico (spese per categoria)
    spese_per_categoria = {}
    for spesa in spese:
        cat = spesa['categoria']
        imp = spesa['importo']
        spese_per_categoria[cat] = spese_per_categoria.get(cat, 0) + imp

    # AGGIUNGI QUESTA RIGA PER IL DEBUG
    print("Dati per il grafico inviati:", spese_per_categoria)
    return render_template(
        'index.html',
        spese=spese,
        budget_totale=budget_totale,
        speso_totale=speso_totale,
        rimanente=rimanente,
        dati_grafico=json.dumps(spese_per_categoria)
    )


# Le route /aggiungi e /elimina rimangono INVARIATE
@app.route('/aggiungi', methods=['POST'])
def aggiungi_spesa():
    descrizione = request.form['descrizione']
    importo = request.form['importo']
    categoria = request.form['categoria']

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO spese (descrizione, importo, categoria) VALUES (?, ?, ?)",
                   (descrizione, importo, categoria))
    db.commit()

    return redirect(url_for('index'))

@app.route('/elimina/<int:id>')
def elimina_spesa(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM spese WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)