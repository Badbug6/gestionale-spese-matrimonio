from flask import Flask, render_template, request, redirect, url_for, g, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

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

# --- FUNZIONI DI AVVIO E CONTROLLO ---
def create_tables(db):
    """Funzione helper per creare tutte le tabelle se non esistono."""
    cursor = db.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS spese (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descrizione TEXT NOT NULL,
        importo REAL NOT NULL,
        categoria TEXT NOT NULL,
        user_id INTEGER,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )''')
    db.commit()

# --- FUNZIONE CENTRALE PER I DATI (CON CORREZIONE PER JSON e TYPEERROR) ---
def get_app_state():
    if not os.path.exists(DATABASE):
        return {"budget_totale": 0, "speso_totale": 0, "rimanente": 0, "spese": [], "spese_per_categoria": {}}
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT value FROM config WHERE key = 'budget'")
        budget_row = cursor.fetchone()
        budget_totale = float(budget_row['value']) if budget_row else 0.0

        cursor.execute("SELECT spese.*, users.username FROM spese LEFT JOIN users ON spese.user_id = users.id ORDER BY data DESC")
        spese_rows = cursor.fetchall()

        # ★ CORREZIONE JSON: Converti la lista di Row in una lista di dizionari
        spese = [dict(row) for row in spese_rows]

        # ★ CORREZIONE TYPEERROR: Assicurati che gli importi siano numeri prima di sommarli
        speso_totale = sum(float(s.get('importo') or 0) for s in spese)
        rimanente = budget_totale - speso_totale

        spese_per_categoria = {}
        for s in spese:
            importo = float(s.get('importo') or 0)
            spese_per_categoria[s['categoria']] = spese_per_categoria.get(s['categoria'], 0) + importo

        return {
            "budget_totale": budget_totale,
            "speso_totale": speso_totale,
            "rimanente": rimanente,
            "spese": spese,  # Ora è una lista di dizionari, serializzabile
            "spese_per_categoria": spese_per_categoria
        }
    except (sqlite3.OperationalError, TypeError) as e:
        print(f"Errore in get_app_state: {e}")
        return {"budget_totale": 0, "speso_totale": 0, "rimanente": 0, "spese": [], "spese_per_categoria": {}}


# --- ROUTES DI AVVIO E PRINCIPALI ---
@app.route('/')
def index():
    if not os.path.exists(DATABASE):
        return redirect(url_for('create_admin'))
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT 1 FROM users WHERE is_admin = 1")
        if cursor.fetchone() is None:
            return redirect(url_for('create_admin'))
    except sqlite3.OperationalError:
        return redirect(url_for('create_admin'))

    cursor.execute("SELECT 1 FROM config WHERE key = 'budget'")
    if cursor.fetchone() is None:
        return redirect(url_for('setup'))

    state = get_app_state()
    cursor.execute("SELECT name FROM categories ORDER BY name")
    categories = [row['name'] for row in cursor.fetchall()]
    user = None
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
    return render_template('index.html', state=state, categories=categories, user=user)


@app.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    if os.path.exists(DATABASE):
        with sqlite3.connect(DATABASE) as db_check:
            try:
                if db_check.execute("SELECT 1 FROM users WHERE is_admin = 1").fetchone():
                    return redirect(url_for('index'))
            except sqlite3.OperationalError:
                pass  # Tabella non esiste, procedi.
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        create_tables(db)
        password_hash = generate_password_hash(password)
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)", (username, password_hash))
        db.commit()
        flash('Utente amministratore creato! Ora imposta il budget.', 'success')
        return redirect(url_for('setup'))
    return render_template('create_admin.html')


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    try:
        db = get_db()
        cursor = db.cursor()
        if not cursor.execute("SELECT 1 FROM users WHERE is_admin = 1").fetchone():
            return redirect(url_for('create_admin'))
        if cursor.execute("SELECT 1 FROM config WHERE key = 'budget'").fetchone():
            return redirect(url_for('index'))
    except sqlite3.OperationalError:
        return redirect(url_for('create_admin'))

    if request.method == 'POST':
        budget_iniziale = request.form.get('budget', '0').strip().replace(',', '.')
        try:
            # Valida che il budget sia un numero
            float(budget_iniziale)
        except ValueError:
            flash("Errore: il budget deve essere un numero valido.", 'error')
            return render_template('setup.html')

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", ('budget', budget_iniziale))
        categorie_standard = ['Location', 'Catering', 'Abiti', 'Fiori', 'Foto', 'Musica', 'Viaggio', 'Bomboniere', 'Decorazioni', 'Trasporti']
        for cat in categorie_standard:
            try:
                cursor.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
            except sqlite3.IntegrityError:
                pass
        db.commit()
        flash('Budget impostato con successo!', 'success')
        return redirect(url_for('index'))
    return render_template('setup.html')


# --- ROUTES PER LA GESTIONE DELLE SPESE (con validazione) ---
@app.route('/aggiungi', methods=['POST'])
def aggiungi_spesa():
    descrizione = request.form['descrizione']
    importo_str = request.form.get('importo', '').strip().replace(',', '.')
    categoria = request.form['categoria']
    user_id = session.get('user_id')

    if not importo_str:
        flash('Errore: l\'importo non può essere vuoto.', 'error')
        return redirect(url_for('index'))
    try:
        importo = float(importo_str)
    except ValueError:
        flash(f"Errore: '{importo_str}' non è un importo valido.", 'error')
        return redirect(url_for('index'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO spese (descrizione, importo, categoria, user_id) VALUES (?, ?, ?, ?)",
                   (descrizione, importo, categoria, user_id))
    db.commit()
    flash('Spesa aggiunta con successo!', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>')
def edit_spesa(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM spese WHERE id = ?", (id,))
    spesa = cursor.fetchone()
    if spesa is None:
        return redirect(url_for('index'))
    cursor.execute("SELECT name FROM categories ORDER BY name")
    categories = [row['name'] for row in cursor.fetchall()]
    return render_template('edit.html', spesa=spesa, categories=categories)


@app.route('/update/<int:id>', methods=['POST'])
def update_spesa(id):
    descrizione = request.form['descrizione']
    importo_str = request.form.get('importo', '').strip().replace(',', '.')
    categoria = request.form['categoria']

    if not importo_str:
        flash('Errore: l\'importo non può essere vuoto.', 'error')
        return redirect(url_for('edit_spesa', id=id))
    try:
        importo = float(importo_str)
    except ValueError:
        flash(f"Errore: '{importo_str}' non è un importo valido.", 'error')
        return redirect(url_for('edit_spesa', id=id))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE spese SET descrizione = ?, importo = ?, categoria = ? WHERE id = ?",
                   (descrizione, importo, categoria, id))
    db.commit()
    flash('Spesa aggiornata con successo!', 'success')
    return redirect(url_for('index'))


# --- ROUTES PER LA GESTIONE DELLE CATEGORIE ---
@app.route('/categories')
def categories_page():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()
    return render_template('categories.html', categories=categories)


@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form.get('name', '').strip()
    if not name:
        flash("Il nome della categoria non può essere vuoto.", "error")
        return redirect(url_for('categories_page'))
    db = get_db()
    try:
        db.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        db.commit()
        flash(f"Categoria '{name}' aggiunta.", 'success')
    except sqlite3.IntegrityError:
        flash(f"Errore: la categoria '{name}' esiste già.", 'error')
    return redirect(url_for('categories_page'))


@app.route('/update_category/<int:id>', methods=['POST'])
def update_category(id):
    new_name = request.form.get('new_name', '').strip()
    if not new_name:
        flash("Il nuovo nome della categoria non può essere vuoto.", "error")
        return redirect(url_for('categories_page'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM categories WHERE id = ?", (id,))
    old_name_row = cursor.fetchone()
    if not old_name_row:
        return redirect(url_for('categories_page'))
    old_name = old_name_row['name']
    cursor.execute("UPDATE categories SET name = ? WHERE id = ?", (new_name, id))
    cursor.execute("UPDATE spese SET categoria = ? WHERE categoria = ?", (new_name, old_name))
    db.commit()
    flash(f"Categoria '{old_name}' rinominata in '{new_name}'.", 'success')
    return redirect(url_for('categories_page'))


@app.route('/delete_category/<int:id>')
def delete_category(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM categories WHERE id = ?", (id,))
    cat_name_row = cursor.fetchone()
    if not cat_name_row:
        return redirect(url_for('categories_page'))
    cat_name = cat_name_row['name']
    cursor.execute("SELECT COUNT(id) as count FROM spese WHERE categoria = ?", (cat_name,))
    usage_count = cursor.fetchone()['count']
    if usage_count > 0:
        flash(f"Impossibile eliminare '{cat_name}'. È usata da {usage_count} spese.", 'error')
    else:
        cursor.execute("DELETE FROM categories WHERE id = ?", (id,))
        db.commit()
        flash(f"Categoria '{cat_name}' eliminata.", 'success')
    return redirect(url_for('categories_page'))


# --- ENDPOINTS API ---
@app.route('/api/add_expense', methods=['POST'])
def api_add_expense():
    data = request.get_json()
    user_id = session.get('user_id')
    try:
        importo_str = str(data.get('importo', '')).strip().replace(',', '.')
        if not importo_str:
            return jsonify({"error": "L'importo non può essere vuoto."}), 400
        importo = float(importo_str)
        descrizione = data['descrizione']
        categoria = data['categoria']
    except (ValueError, KeyError) as e:
        return jsonify({"error": f"Dati non validi: {e}"}), 400
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO spese (descrizione, importo, categoria, user_id) VALUES (?, ?, ?, ?)",
                   (descrizione, importo, categoria, user_id))
    db.commit()
    return jsonify(get_app_state())


@app.route('/api/delete_expense/<int:id>', methods=['POST'])
def api_delete_expense(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM spese WHERE id = ?", (id,))
    db.commit()
    return jsonify(get_app_state())


# --- GESTIONE UTENTI E AUTENTICAZIONE ---
@app.route('/manage_users')
def manage_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username, is_admin FROM users ORDER BY username")
    users = cursor.fetchall()
    return render_template('manage_users.html', users=users)


def get_user_by_username(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchone()


def get_user_by_id(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not get_user_by_username(username):
            password_hash = generate_password_hash(password)
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
            db.commit()
            flash('Registrazione avvenuta con successo! Effettua il login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username già esistente. Scegline un altro.', 'error')
            return render_template('register.html')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash('Credenziali non valide. Riprova.', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Sei stato disconnesso.', 'success')
    return redirect(url_for('login'))


# --- AVVIO APP ---
if __name__ == '__main__':
    # Esegui sulla porta 5001 per evitare conflitti su macOS
    app.run(debug=True, port=5001)