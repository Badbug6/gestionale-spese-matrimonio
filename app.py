from flask import Flask, render_template, request, redirect, url_for, g, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

# Importa Waitress, che useremo per la produzione
from waitress import serve

app = Flask(__name__)
app.secret_key = 'la-mia-chiave-super-segreta-per-il-matrimonio-cambiami'
DATABASE = 'wedding.db'

# --- GESTIONE DB ---
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

# --- LOGICA DI CREAZIONE DEL DATABASE ---
def create_tables(db):
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, is_admin INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS spese (id INTEGER PRIMARY KEY AUTOINCREMENT, descrizione TEXT NOT NULL, importo REAL NOT NULL, categoria TEXT NOT NULL, user_id INTEGER, data TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS scadenze (id INTEGER PRIMARY KEY AUTOINCREMENT, descrizione TEXT NOT NULL, data_scadenza DATE NOT NULL, stato TEXT NOT NULL DEFAULT 'Da Fare', spesa_associata_id INTEGER, FOREIGN KEY(spesa_associata_id) REFERENCES spese(id) ON DELETE SET NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pagamenti (id INTEGER PRIMARY KEY AUTOINCREMENT, spesa_id INTEGER NOT NULL, importo_pagato REAL NOT NULL, data_pagamento DATE NOT NULL, note TEXT, FOREIGN KEY(spesa_id) REFERENCES spese(id) ON DELETE CASCADE)''')
    db.commit()

# --- FUNZIONE CENTRALE PER I DATI ---
def get_app_state():
    if not os.path.exists(DATABASE): return {"budget_totale": 0, "speso_totale_previsto": 0, "speso_totale_effettivo": 0, "rimanente_previsto": 0, "spese": [], "spese_per_categoria": {}}
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT value FROM config WHERE key = 'budget'")
        budget_row = cursor.fetchone()
        budget_totale = float(budget_row['value']) if budget_row else 0.0
        sql_query = """SELECT s.id, s.descrizione, s.importo, s.categoria, s.user_id, s.data, u.username, COALESCE(p.totale_pagato, 0) as totale_pagato FROM spese s LEFT JOIN users u ON s.user_id = u.id LEFT JOIN (SELECT spesa_id, SUM(importo_pagato) as totale_pagato FROM pagamenti GROUP BY spesa_id) p ON s.id = p.spesa_id ORDER BY s.data DESC"""
        spese_rows = cursor.execute(sql_query).fetchall()
        spese = [dict(row) for row in spese_rows]
        speso_totale_previsto = sum(float(s.get('importo') or 0) for s in spese)
        rimanente_previsto = budget_totale - speso_totale_previsto
        speso_totale_effettivo = sum(float(s.get('totale_pagato') or 0) for s in spese)
        spese_per_categoria = {}
        for s in spese:
            spese_per_categoria[s['categoria']] = spese_per_categoria.get(s['categoria'], 0) + float(s.get('importo') or 0)
        return {"budget_totale": budget_totale, "speso_totale_previsto": speso_totale_previsto, "speso_totale_effettivo": speso_totale_effettivo, "rimanente_previsto": rimanente_previsto, "spese": spese, "spese_per_categoria": spese_per_categoria}
    except (sqlite3.OperationalError, TypeError) as e:
        print(f"Errore in get_app_state: {e}")
        return {"budget_totale": 0, "speso_totale_previsto": 0, "speso_totale_effettivo": 0, "rimanente_previsto": 0, "spese": [], "spese_per_categoria": {}}

# --- ROUTES DI AVVIO E PRINCIPALI ---
@app.route('/')
def index():
    if not os.path.exists(DATABASE): return redirect(url_for('create_admin'))
    db = get_db()
    try:
        if not db.execute("SELECT 1 FROM users WHERE is_admin = 1").fetchone(): return redirect(url_for('create_admin'))
    except sqlite3.OperationalError: return redirect(url_for('create_admin'))
    if not db.execute("SELECT 1 FROM config WHERE key = 'budget'").fetchone(): return redirect(url_for('setup'))
    state = get_app_state()
    categories = [row['name'] for row in db.execute("SELECT name FROM categories ORDER BY name").fetchall()]
    user = get_user_by_id(session['user_id']) if 'user_id' in session else None
    return render_template('index.html', state=state, categories=categories, user=user)

@app.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    if os.path.exists(DATABASE):
        with sqlite3.connect(DATABASE) as db_check:
            try:
                if db_check.execute("SELECT 1 FROM users WHERE is_admin = 1").fetchone(): return redirect(url_for('index'))
            except sqlite3.OperationalError: pass
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        db = get_db()
        create_tables(db)
        password_hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)", (username, password_hash)).commit()
        flash('Utente amministratore creato! Ora imposta il budget.', 'success')
        return redirect(url_for('setup'))
    return render_template('create_admin.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    try:
        db = get_db()
        if not db.execute("SELECT 1 FROM users WHERE is_admin = 1").fetchone(): return redirect(url_for('create_admin'))
        if db.execute("SELECT 1 FROM config WHERE key = 'budget'").fetchone(): return redirect(url_for('index'))
    except sqlite3.OperationalError: return redirect(url_for('create_admin'))
    if request.method == 'POST':
        budget_iniziale = request.form.get('budget', '0').strip().replace(',', '.')
        try: float(budget_iniziale)
        except ValueError:
            flash("Errore: il budget deve essere un numero valido.", 'error')
            return render_template('setup.html')
        db = get_db()
        db.execute("INSERT INTO config (key, value) VALUES (?, ?)", ('budget', budget_iniziale))
        for cat in ['Location', 'Catering', 'Abiti', 'Fiori', 'Foto', 'Musica', 'Viaggio', 'Bomboniere', 'Decorazioni', 'Trasporti']:
            try: db.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
            except sqlite3.IntegrityError: pass
        db.commit()
        flash('Budget impostato con successo!', 'success')
        return redirect(url_for('index'))
    return render_template('setup.html')

# --- ROUTES PER SCADENZARIO E PAGAMENTI ---
@app.route('/scadenzario')
def scadenzario():
    db = get_db()
    scadenze = db.execute("SELECT * FROM scadenze ORDER BY data_scadenza ASC").fetchall()
    spese_disponibili = db.execute("SELECT id, descrizione FROM spese ORDER BY descrizione").fetchall()
    return render_template('scadenzario.html', scadenze=scadenze, spese_disponibili=spese_disponibili)
@app.route('/scadenza/add', methods=['POST'])
def add_scadenza():
    descrizione, data_scadenza = request.form['descrizione'], request.form['data_scadenza']
    spesa_id = request.form.get('spesa_associata_id')
    get_db().execute("INSERT INTO scadenze (descrizione, data_scadenza, spesa_associata_id) VALUES (?, ?, ?)",(descrizione, data_scadenza, spesa_id if spesa_id else None)).commit()
    flash('Scadenza aggiunta!', 'success')
    return redirect(url_for('scadenzario'))
@app.route('/scadenza/toggle/<int:id>')
def toggle_scadenza(id):
    db = get_db()
    scadenza = db.execute("SELECT stato FROM scadenze WHERE id = ?", (id,)).fetchone()
    if scadenza:
        nuovo_stato = 'Completato' if scadenza['stato'] == 'Da Fare' else 'Da Fare'
        db.execute("UPDATE scadenze SET stato = ? WHERE id = ?", (nuovo_stato, id)).commit()
    return redirect(url_for('scadenzario'))
@app.route('/scadenza/delete/<int:id>')
def delete_scadenza(id):
    get_db().execute("DELETE FROM scadenze WHERE id = ?", (id,)).commit()
    flash('Scadenza eliminata.', 'success')
    return redirect(url_for('scadenzario'))
@app.route('/spesa/<int:spesa_id>')
def spesa_detail(spesa_id):
    db = get_db()
    spesa = db.execute("SELECT * FROM spese WHERE id = ?", (spesa_id,)).fetchone()
    if not spesa: return redirect(url_for('index'))
    pagamenti = db.execute("SELECT * FROM pagamenti WHERE spesa_id = ? ORDER BY data_pagamento DESC", (spesa_id,)).fetchall()
    rimanente_da_pagare = spesa['importo'] - sum(p['importo_pagato'] for p in pagamenti)
    return render_template('spesa_detail.html', spesa=spesa, pagamenti=pagamenti, totale_pagato=sum(p['importo_pagato'] for p in pagamenti), rimanente_da_pagare=rimanente_da_pagare)
@app.route('/pagamento/add/<int:spesa_id>', methods=['POST'])
def add_pagamento(spesa_id):
    importo_pagato, data_pagamento, note = request.form.get('importo_pagato', '').strip().replace(',', '.'), request.form['data_pagamento'], request.form['note']
    try: importo = float(importo_pagato)
    except ValueError:
        flash("Importo non valido.", "error")
        return redirect(url_for('spesa_detail', spesa_id=spesa_id))
    get_db().execute("INSERT INTO pagamenti (spesa_id, importo_pagato, data_pagamento, note) VALUES (?, ?, ?, ?)", (spesa_id, importo, data_pagamento, note)).commit()
    flash("Acconto registrato!", "success")
    return redirect(url_for('spesa_detail', spesa_id=spesa_id))

# --- ENDPOINTS API ---
@app.route('/api/add_expense', methods=['POST'])
def api_add_expense():
    data = request.get_json()
    user_id = session.get('user_id')
    try:
        importo_str = str(data.get('importo', '')).strip().replace(',', '.')
        if not importo_str: return jsonify({"error": "L'importo non può essere vuoto."}), 400
        importo, descrizione, categoria = float(importo_str), data['descrizione'], data['categoria']
    except (ValueError, KeyError) as e: return jsonify({"error": f"Dati non validi: {e}"}), 400
    get_db().execute("INSERT INTO spese (descrizione, importo, categoria, user_id) VALUES (?, ?, ?, ?)", (descrizione, importo, categoria, user_id)).commit()
    return jsonify(get_app_state())
@app.route('/api/delete_expense/<int:id>', methods=['POST'])
def api_delete_expense(id):
    get_db().execute("DELETE FROM spese WHERE id = ?", (id,)).commit()
    return jsonify(get_app_state())
@app.route('/api/scadenze')
def api_scadenze():
    scadenze_rows = get_db().execute("SELECT id, descrizione, data_scadenza, stato, spesa_associata_id FROM scadenze").fetchall()
    events = []
    for scadenza in scadenze_rows:
        event = {'title': scadenza['descrizione'], 'start': scadenza['data_scadenza'], 'allDay': True}
        if scadenza['stato'] == 'Completato': event['backgroundColor'], event['borderColor'] = '#28a745', '#28a745'
        if scadenza['spesa_associata_id']: event['url'] = url_for('spesa_detail', spesa_id=scadenza['spesa_associata_id'])
        events.append(event)
    return jsonify(events)
    
# --- GESTIONE SPESE, CATEGORIE, UTENTI E AUTENTICAZIONE ---
@app.route('/categories')
def categories_page():
    categories = get_db().execute("SELECT * FROM categories ORDER BY name").fetchall()
    return render_template('categories.html', categories=categories)
@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form.get('name', '').strip()
    if not name:
        flash("Il nome della categoria non può essere vuoto.", "error")
        return redirect(url_for('categories_page'))
    try:
        get_db().execute("INSERT INTO categories (name) VALUES (?)", (name,)).commit()
        flash(f"Categoria '{name}' aggiunta.", 'success')
    except sqlite3.IntegrityError: flash(f"Errore: la categoria '{name}' esiste già.", 'error')
    return redirect(url_for('categories_page'))
@app.route('/update_category/<int:id>', methods=['POST'])
def update_category(id):
    new_name = request.form.get('new_name', '').strip()
    if not new_name:
        flash("Il nuovo nome non può essere vuoto.", "error")
        return redirect(url_for('categories_page'))
    db, cursor = get_db(), get_db().cursor()
    old_name_row = cursor.execute("SELECT name FROM categories WHERE id = ?", (id,)).fetchone()
    if not old_name_row: return redirect(url_for('categories_page'))
    old_name = old_name_row['name']
    cursor.execute("UPDATE categories SET name = ? WHERE id = ?", (new_name, id))
    cursor.execute("UPDATE spese SET categoria = ? WHERE categoria = ?", (new_name, old_name))
    db.commit()
    flash(f"Categoria rinominata in '{new_name}'.", 'success')
    return redirect(url_for('categories_page'))
@app.route('/delete_category/<int:id>')
def delete_category(id):
    db, cursor = get_db(), get_db().cursor()
    cat_name_row = cursor.execute("SELECT name FROM categories WHERE id = ?", (id,)).fetchone()
    if not cat_name_row: return redirect(url_for('categories_page'))
    cat_name = cat_name_row['name']
    if cursor.execute("SELECT 1 FROM spese WHERE categoria = ?", (cat_name,)).fetchone():
        flash(f"Impossibile eliminare '{cat_name}', è usata da una o più spese.", 'error')
    else:
        cursor.execute("DELETE FROM categories WHERE id = ?", (id,)).commit()
        flash(f"Categoria '{cat_name}' eliminata.", 'success')
    return redirect(url_for('categories_page'))
@app.route('/edit/<int:id>')
def edit_spesa(id):
    db = get_db()
    spesa = db.execute("SELECT * FROM spese WHERE id = ?", (id,)).fetchone()
    if not spesa: return redirect(url_for('index'))
    categories = [row['name'] for row in db.execute("SELECT name FROM categories ORDER BY name").fetchall()]
    return render_template('edit.html', spesa=spesa, categories=categories)
def get_user_by_username(username):
    return get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
def get_user_by_id(user_id):
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        if not get_user_by_username(username):
            get_db().execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, generate_password_hash(password))).commit()
            flash('Registrazione avvenuta! Effettua il login.', 'success')
            return redirect(url_for('login'))
        else: flash('Username già esistente.', 'error')
    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash('Credenziali non valide.', 'error')
    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Sei stato disconnesso.', 'success')
    return redirect(url_for('login'))
@app.route('/manage_users')
def manage_users():
    users = get_db().execute("SELECT id, username, is_admin FROM users ORDER BY username").fetchall()
    return render_template('manage_users.html', users=users)
    
# --- AVVIO APP (UNIVERSALE E PRONTO PER LA PRODUZIONE) ---
if __name__ == '__main__':
    is_debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

    if is_debug:
        # Modalità Sviluppo: usa il server integrato di Flask con il debugger.
        print(">>> AVVIO IN MODALITÀ SVILUPPO (DEBUG) <<<")
        app.run(host='127.0.0.1', port=5001, debug=True)
    else:
        # Modalità Produzione: usa il server robusto e cross-platform Waitress.
        print(f">>> AVVIO IN MODALITÀ PRODUZIONE CON WAITRESS SU http://127.0.0.1:5001 <<<")
        serve(app, host='127.0.0.1', port=5001)