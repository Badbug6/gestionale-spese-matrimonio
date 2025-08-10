from flask import Flask, render_template, request, redirect, url_for, g, flash, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'la-mia-chiave-super-segreta-per-il-matrimonio-cambiami'
DATABASE = 'wedding.db'

# --- GESTIONE DB (invariata) ---
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

# --- SETUP (invariato) ---
@app.before_request
def check_for_setup():
    if not os.path.exists(DATABASE):
        if request.endpoint != 'setup' and request.endpoint != 'static':
            return redirect(url_for('setup'))

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if os.path.exists(DATABASE): return redirect(url_for('index'))
    if request.method == 'POST':
        budget_iniziale = request.form['budget']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('CREATE TABLE spese (id INTEGER PRIMARY KEY, descrizione TEXT, importo REAL, categoria TEXT, data TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        cursor.execute('CREATE TABLE config (key TEXT PRIMARY KEY, value TEXT)')
        cursor.execute('CREATE TABLE categories (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)')
        cursor.execute('INSERT INTO config (key, value) VALUES (?, ?)', ('budget', budget_iniziale))
        default_categories = ['Location', 'Fiori', 'Fotografo', 'Abbigliamento', 'Musica', 'Burocrazia', 'Altro']
        for cat in default_categories:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
        db.commit()
        return redirect(url_for('index'))
    return render_template('setup.html')

# --- FUNZIONE CENTRALE PER I DATI (CON LA CORREZIONE DEFINITIVA) ---
def get_app_state():
    if not os.path.exists(DATABASE):
        return { "budget_totale": 0, "speso_totale": 0, "rimanente": 0, "spese": [], "spese_per_categoria": {} }
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM spese ORDER BY data DESC")
        spese = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT value FROM config WHERE key = 'budget'")
        budget_totale = float(cursor.fetchone()['value'])
        
        speso_totale = sum(s['importo'] for s in spese)
        rimanente = budget_totale - speso_totale
        
        # ★★★ LA CORREZIONE È QUI ★★★
        # Metodo sicuro in due passaggi che non causa l'errore.
        spese_per_categoria = {}
        for s in spese:
            spese_per_categoria[s['categoria']] = spese_per_categoria.get(s['categoria'], 0) + s['importo']
        
        return {
            "budget_totale": budget_totale, "speso_totale": speso_totale, "rimanente": rimanente,
            "spese": spese, "spese_per_categoria": spese_per_categoria
        }
    except (sqlite3.OperationalError, TypeError):
        return { "budget_totale": 0, "speso_totale": 0, "rimanente": 0, "spese": [], "spese_per_categoria": {} }

# --- ROUTES HTML (invariate) ---
@app.route('/')
def index():
    state = get_app_state()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM categories ORDER BY name")
    categories = [row['name'] for row in cursor.fetchall()]
    return render_template('index.html', state=state, categories=categories)

@app.route('/edit/<int:id>')
def edit_spesa(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM spese WHERE id = ?", (id,))
    spesa = cursor.fetchone()
    if spesa is None: return redirect(url_for('index'))
    cursor.execute("SELECT name FROM categories ORDER BY name")
    categories = [row['name'] for row in cursor.fetchall()]
    return render_template('edit.html', spesa=spesa, categories=categories)

@app.route('/categories')
def categories_page():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()
    return render_template('categories.html', categories=categories)

# --- API ENDPOINTS (invariati) ---
@app.route('/api/add_expense', methods=['POST'])
def api_add_expense():
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO spese (descrizione, importo, categoria) VALUES (?, ?, ?)",(data['descrizione'], data['importo'], data['categoria']))
    db.commit()
    return jsonify(get_app_state())

@app.route('/api/delete_expense/<int:id>', methods=['POST'])
def api_delete_expense(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM spese WHERE id = ?", (id,))
    db.commit()
    return jsonify(get_app_state())

# --- ROUTES CLASSICHE (invariate) ---
@app.route('/update/<int:id>', methods=['POST'])
def update_spesa(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE spese SET descrizione = ?, importo = ?, categoria = ? WHERE id = ?",(request.form['descrizione'], request.form['importo'], request.form['categoria'], id))
    db.commit()
    return redirect(url_for('index'))

@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form['name']
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
    new_name = request.form['new_name']
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM categories WHERE id = ?", (id,))
    old_name = cursor.fetchone()['name']
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
    cat_name = cursor.fetchone()['name']
    cursor.execute("SELECT COUNT(id) as count FROM spese WHERE categoria = ?", (cat_name,))
    usage_count = cursor.fetchone()['count']
    if usage_count > 0:
        flash(f"Impossibile eliminare '{cat_name}'. È usata da {usage_count} spese.", 'error')
    else:
        cursor.execute("DELETE FROM categories WHERE id = ?", (id,))
        db.commit()
        flash(f"Categoria '{cat_name}' eliminata.", 'success')
    return redirect(url_for('categories_page'))

# --- AVVIO APP ---
if __name__ == '__main__':
    app.run(debug=True)