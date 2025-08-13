import os
import sqlite3
from datetime import date, timedelta, datetime

from flask import (Flask, flash, g, jsonify, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from waitress import serve

from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = 'la-mia-chiave-super-segreta-per-il-matrimonio-cambiami'
DATABASE = 'wedding.db'

app.config.update(
    MAIL_SERVER='', MAIL_PORT=587, MAIL_USERNAME='', MAIL_PASSWORD='',
    MAIL_USE_TLS=True, MAIL_USE_SSL=False
)

mail = Mail(app)
scheduler = BackgroundScheduler(daemon=True)

# --- FUNZIONI DB ---
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

def create_tables(db):
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL, email TEXT UNIQUE NOT NULL, is_admin INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS spese (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, descrizione TEXT NOT NULL, importo REAL NOT NULL,
                        categoria TEXT NOT NULL, user_id INTEGER, data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS scadenze (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, descrizione TEXT NOT NULL, data_scadenza DATE NOT NULL,
                        importo_scadenza REAL, stato TEXT NOT NULL DEFAULT 'Da Fare', spesa_associata_id INTEGER,
                        FOREIGN KEY(spesa_associata_id) REFERENCES spese(id) ON DELETE SET NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS pagamenti (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, spesa_id INTEGER NOT NULL,
                        importo_pagato REAL NOT NULL, data_pagamento DATE NOT NULL, note TEXT,
                        scadenza_associata_id INTEGER,
                        FOREIGN KEY(spesa_id) REFERENCES spese(id) ON DELETE CASCADE,
                        FOREIGN KEY(scadenza_associata_id) REFERENCES scadenze(id) ON DELETE SET NULL
                    )''')
    db.commit()

# --- FUNZIONI DI SUPPORTO ---
def get_app_state():
    db = get_db()
    try:
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
        sql_query_pagamenti = "SELECT strftime('%Y-%m', data_pagamento) as mese, SUM(importo_pagato) as totale FROM pagamenti GROUP BY mese ORDER BY mese ASC"
        pagamenti_mensili_rows = cursor.execute(sql_query_pagamenti).fetchall()
        pagamenti_mensili = {'labels': [row['mese'] for row in pagamenti_mensili_rows], 'data': [row['totale'] for row in pagamenti_mensili_rows]}
        return {"budget_totale": budget_totale, "speso_totale_previsto": speso_totale_previsto, "speso_totale_effettivo": speso_totale_effettivo, "rimanente_previsto": rimanente_previsto, "spese": spese, "spese_per_categoria": spese_per_categoria, "pagamenti_mensili": pagamenti_mensili}
    except Exception: return {"budget_totale": 0, "speso_totale_previsto": 0, "speso_totale_effettivo": 0, "rimanente_previsto": 0, "spese": [], "spese_per_categoria": {}, "pagamenti_mensili": {'labels': [], 'data': []}}

def get_user_by_username(username):
    return get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

def get_user_by_id(user_id):
    if not user_id: return None
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

def send_email(subject, recipients, text_body, html_body):
    try:
        db = get_db()
        configs = db.execute("SELECT key, value FROM config WHERE key LIKE 'SMTP_%'").fetchall()
        config_dict = {row['key']: row['value'] for row in configs}
        if not config_dict.get('SMTP_SERVER'):
            return (False, "Configurazione SMTP non trovata.")
        temp_app = Flask(__name__)
        temp_app.config.update(
            MAIL_SERVER=config_dict.get('SMTP_SERVER'), MAIL_PORT=int(config_dict.get('SMTP_PORT', 587)),
            MAIL_USERNAME=config_dict.get('SMTP_USERNAME'), MAIL_PASSWORD=config_dict.get('SMTP_PASSWORD'),
            MAIL_USE_TLS=True, MAIL_USE_SSL=False
        )
        temp_mail = Mail(temp_app)
        msg = Message(subject, sender=temp_app.config['MAIL_USERNAME'], recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        temp_mail.send(msg)
        return (True, "Email inviata con successo!")
    except Exception as e:
        print(f"Errore durante l'invio dell'email: {e}")
        return (False, f"Errore: {e}")

def check_and_send_reminders():
    with app.app_context():
        db = get_db()
        reminder_date = date.today() + timedelta(days=7)
        scadenze = db.execute("SELECT * FROM scadenze WHERE stato = 'Da Fare' AND data_scadenza = ?", (reminder_date.strftime('%Y-%m-%d'),)).fetchall()
        if not scadenze: return f"Nessuna scadenza trovata per il {reminder_date}."
        users = db.execute("SELECT * FROM users WHERE email IS NOT NULL AND email != ''").fetchall()
        if not users: return "Nessun utente con email trovato."
        for user in users:
            subject = f"Promemoria Scadenze Matrimonio - {user['username']}"
            html = render_template('email/reminder.html', scadenze=scadenze, user=user, now=datetime.utcnow())
            text = "Hai delle scadenze in arrivo."
            send_email(subject, [user['email']], text, html)
        return f"Promemoria inviato a {len(users)} utenti per {len(scadenze)} scadenze."

# --- ROUTES ---
@app.route('/scadenza/toggle/<int:id>')
def toggle_scadenza(id):
    if not session.get('user_id'): return redirect(url_for('login'))
    db = get_db()
    scadenza = db.execute("SELECT * FROM scadenze WHERE id = ?", (id,)).fetchone()
    if scadenza:
        nuovo_stato = 'Completato' if scadenza['stato'] == 'Da Fare' else 'Da Fare'
        db.execute("UPDATE scadenze SET stato = ? WHERE id = ?", (nuovo_stato, id))
        if scadenza['spesa_associata_id'] and scadenza['importo_scadenza']:
            spesa_id, importo_pagamento = scadenza['spesa_associata_id'], scadenza['importo_scadenza']
            if nuovo_stato == 'Completato':
                pagamento_esistente = db.execute("SELECT id FROM pagamenti WHERE scadenza_associata_id = ?", (id,)).fetchone()
                if not pagamento_esistente:
                    db.execute(
                        "INSERT INTO pagamenti (spesa_id, importo_pagato, data_pagamento, note, scadenza_associata_id) VALUES (?, ?, ?, ?, ?)",
                        # --- CORREZIONE APPLICATA QUI ---
                        (spesa_id, importo_pagamento, date.today().isoformat(), f"Pagamento da scadenza: {scadenza['descrizione']}", id)
                    )
                    flash(f"Pagamento di €{importo_pagamento:.2f} registrato.", 'success')
            elif nuovo_stato == 'Da Fare':
                db.execute("DELETE FROM pagamenti WHERE scadenza_associata_id = ?", (id,))
                flash(f"Pagamento associato alla scadenza '{scadenza['descrizione']}' annullato.", 'info')
        db.commit()
    return redirect(url_for('scadenzario'))

# ... (tutte le altre route sono corrette e invariate)
@app.route('/')
def index():
    if not os.path.exists(DATABASE): return redirect(url_for('create_admin'))
    try:
        db = get_db()
        if not db.execute("SELECT 1 FROM users WHERE is_admin = 1").fetchone(): return redirect(url_for('create_admin'))
    except sqlite3.OperationalError: return redirect(url_for('create_admin'))
    if not session.get('user_id'): return redirect(url_for('login'))
    if not get_db().execute("SELECT 1 FROM config WHERE key = 'budget'").fetchone(): return redirect(url_for('setup'))
    state = get_app_state()
    categories = [row['name'] for row in get_db().execute("SELECT name FROM categories ORDER BY name").fetchall()]
    user = get_user_by_id(session.get('user_id'))
    return render_template('index.html', state=state, categories=categories, user=user)

@app.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    try:
        if os.path.exists(DATABASE) and get_db().execute("SELECT 1 FROM users WHERE is_admin = 1").fetchone():
            return redirect(url_for('index'))
    except sqlite3.OperationalError: pass
    if request.method == 'POST':
        username, email, password = request.form['username'], request.form['email'], request.form['password']
        db = get_db()
        create_tables(db)
        password_hash = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, 1)", (username, email, password_hash))
            db.commit()
            flash('Utente amministratore creato! Ora imposta il budget.', 'success')
            return redirect(url_for('setup'))
        except sqlite3.IntegrityError:
            flash('Username o Email già esistenti.', 'error')
            return redirect(url_for('create_admin'))
    return render_template('create_admin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session.permanent = True
            return redirect(url_for('index'))
        flash('Credenziali non valide.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Sei stato disconnesso.', 'success')
    return redirect(url_for('login'))

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
        return redirect(url_for('login'))
    return render_template('setup.html')

@app.route('/scadenzario')
def scadenzario():
    if not session.get('user_id'): return redirect(url_for('login'))
    db = get_db()
    scadenze = db.execute("SELECT * FROM scadenze ORDER BY data_scadenza DESC").fetchall()
    spese_disponibili = db.execute("SELECT id, descrizione FROM spese ORDER BY descrizione").fetchall()
    return render_template('scadenzario.html', scadenze=scadenze, spese_disponibili=spese_disponibili, user=get_user_by_id(session.get('user_id')))

@app.route('/scadenza/add', methods=['POST'])
def add_scadenza():
    if not session.get('user_id'): return redirect(url_for('login'))
    descrizione = request.form['descrizione']
    data_scadenza = request.form['data_scadenza']
    spesa_id = request.form.get('spesa_associata_id')
    importo_str = request.form.get('importo_scadenza', '').strip().replace(',', '.')
    importo_scadenza = float(importo_str) if importo_str else None
    db = get_db()
    db.execute("INSERT INTO scadenze (descrizione, data_scadenza, importo_scadenza, spesa_associata_id) VALUES (?, ?, ?, ?)",
               (descrizione, data_scadenza, importo_scadenza, spesa_id if spesa_id else None))
    db.commit()
    flash('Scadenza aggiunta!', 'success')
    return redirect(url_for('scadenzario'))

@app.route('/scadenza/delete/<int:id>')
def delete_scadenza(id):
    if not session.get('user_id'): return redirect(url_for('login'))
    db = get_db()
    db.execute("DELETE FROM scadenze WHERE id = ?", (id,))
    db.commit()
    flash('Scadenza eliminata.', 'success')
    return redirect(url_for('scadenzario'))

@app.route('/pagamento/add/<int:spesa_id>', methods=['POST'])
def add_pagamento(spesa_id):
    if not session.get('user_id'): return redirect(url_for('login'))
    importo_pagato = request.form.get('importo_pagato', '').strip().replace(',', '.')
    data_pagamento = request.form['data_pagamento']
    note = request.form['note']
    try:
        importo = float(importo_pagato)
    except ValueError:
        flash("Importo non valido.", "error")
        return redirect(url_for('edit_spesa', id=spesa_id))
    db = get_db()
    db.execute("INSERT INTO pagamenti (spesa_id, importo_pagato, data_pagamento, note) VALUES (?, ?, ?, ?)",
               (spesa_id, importo, data_pagamento, note))
    db.commit()
    flash("Acconto registrato!", "success")
    return redirect(url_for('edit_spesa', id=spesa_id))

@app.route('/pagamento/delete/<int:pagamento_id>', methods=['POST'])
def delete_pagamento(pagamento_id):
    if not session.get('user_id'): return redirect(url_for('login'))
    db = get_db()
    pagamento = db.execute("SELECT spesa_id, scadenza_associata_id FROM pagamenti WHERE id = ?", (pagamento_id,)).fetchone()
    if pagamento:
        spesa_id = pagamento['spesa_id']
        db.execute("DELETE FROM pagamenti WHERE id = ?", (pagamento_id,))
        if pagamento['scadenza_associata_id']:
            db.execute("UPDATE scadenze SET stato = 'Da Fare' WHERE id = ?", (pagamento['scadenza_associata_id'],))
            flash("Pagamento eliminato e scadenza associata riaperta.", "success")
        else:
            flash("Pagamento eliminato con successo.", "success")
        db.commit()
        return redirect(url_for('edit_spesa', id=spesa_id))
    flash("Pagamento non trovato.", "error")
    return redirect(url_for('index'))

@app.route('/api/add_expense', methods=['POST'])
def api_add_expense():
    if not session.get('user_id'): return jsonify({"error": "Non autorizzato"}), 401
    data = request.get_json()
    user_id = session.get('user_id')
    try:
        importo_str = str(data.get('importo', '')).strip().replace(',', '.')
        if not importo_str: return jsonify({"error": "L'importo non può essere vuoto."}), 400
        importo, descrizione, categoria = float(importo_str), data['descrizione'], data['categoria']
    except (ValueError, KeyError) as e: return jsonify({"error": f"Dati non validi: {e}"}), 400
    db = get_db()
    db.execute("INSERT INTO spese (descrizione, importo, categoria, user_id) VALUES (?, ?, ?, ?)", (descrizione, importo, categoria, user_id))
    db.commit()
    return jsonify(get_app_state())

@app.route('/api/delete_expense/<int:id>', methods=['POST'])
def api_delete_expense(id):
    if not session.get('user_id'): return jsonify({"error": "Non autorizzato"}), 401
    db = get_db()
    db.execute("DELETE FROM spese WHERE id = ?", (id,))
    db.commit()
    return jsonify(get_app_state())

@app.route('/api/scadenze')
def api_scadenze():
    if not session.get('user_id'): return jsonify([]), 401
    scadenze_rows = get_db().execute("SELECT id, descrizione, data_scadenza, stato, spesa_associata_id FROM scadenze ORDER BY data_scadenza").fetchall()
    events = []
    for scadenza in scadenze_rows:
        event = {'title': scadenza['descrizione'], 'start': scadenza['data_scadenza'], 'allDay': True}
        if scadenza['stato'] == 'Completato': event['backgroundColor'], event['borderColor'] = '#28a745', '#28a745'
        if scadenza['spesa_associata_id']: event['url'] = url_for('edit_spesa', id=scadenza['spesa_associata_id'])
        events.append(event)
    return jsonify(events)

@app.route('/categories')
def categories_page():
    if not session.get('user_id'): return redirect(url_for('login'))
    categories = get_db().execute("SELECT * FROM categories ORDER BY name").fetchall()
    return render_template('categories.html', categories=categories, user=get_user_by_id(session.get('user_id')))

@app.route('/add_category', methods=['POST'])
def add_category():
    if not session.get('user_id'): return redirect(url_for('login'))
    name = request.form.get('name', '').strip()
    if not name:
        flash("Il nome della categoria non può essere vuoto.", "error")
        return redirect(url_for('categories_page'))
    try:
        db = get_db()
        db.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        db.commit()
        flash(f"Categoria '{name}' aggiunta.", 'success')
    except sqlite3.IntegrityError: flash(f"Errore: la categoria '{name}' esiste già.", 'error')
    return redirect(url_for('categories_page'))

@app.route('/update_category/<int:id>', methods=['POST'])
def update_category(id):
    if not session.get('user_id'): return redirect(url_for('login'))
    new_name = request.form.get('new_name', '').strip()
    if not new_name:
        flash("Il nuovo nome non può essere vuoto.", "error")
        return redirect(url_for('categories_page'))
    db = get_db()
    cursor = db.cursor()
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
    if not session.get('user_id'): return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor()
    cat_name_row = cursor.execute("SELECT name FROM categories WHERE id = ?", (id,)).fetchone()
    if not cat_name_row: return redirect(url_for('categories_page'))
    cat_name = cat_name_row['name']
    if cursor.execute("SELECT 1 FROM spese WHERE categoria = ?", (cat_name,)).fetchone():
        flash(f"Impossibile eliminare '{cat_name}', è usata da una o più spese.", 'error')
    else:
        cursor.execute("DELETE FROM categories WHERE id = ?", (id,))
        db.commit()
        flash(f"Categoria '{cat_name}' eliminata.", 'success')
    return redirect(url_for('categories_page'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_spesa(id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    db = get_db()
    spesa = db.execute("SELECT * FROM spese WHERE id = ?", (id,)).fetchone()
    if not spesa:
        flash("Spesa non trovata.", "error")
        return redirect(url_for('index'))
    pagamenti = db.execute("SELECT * FROM pagamenti WHERE spesa_id = ? ORDER BY data_pagamento DESC", (id,)).fetchall()
    totale_pagato = sum(p['importo_pagato'] for p in pagamenti)
    rimanente_da_pagare = spesa['importo'] - totale_pagato
    if request.method == 'POST':
        if 'descrizione' in request.form:
            descrizione = request.form['descrizione']
            importo_str = request.form.get('importo', '0').strip().replace(',', '.')
            categoria = request.form['categoria']
            try:
                importo = float(importo_str)
            except ValueError:
                flash("L'importo inserito non è un numero valido.", 'error')
                categories = [row['name'] for row in db.execute("SELECT name FROM categories ORDER BY name").fetchall()]
                return render_template('edit.html', spesa=spesa, categories=categories, pagamenti=pagamenti, totale_pagato=totale_pagato, rimanente_da_pagare=rimanente_da_pagare, user=get_user_by_id(session.get('user_id')))
            db.execute("UPDATE spese SET descrizione = ?, importo = ?, categoria = ? WHERE id = ?", (descrizione, importo, categoria, id))
            db.commit()
            flash('Spesa aggiornata con successo!', 'success')
            return redirect(url_for('edit_spesa', id=id))
    categories = [row['name'] for row in db.execute("SELECT name FROM categories ORDER BY name").fetchall()]
    return render_template('edit.html', spesa=spesa, categories=categories, pagamenti=pagamenti, totale_pagato=totale_pagato, rimanente_da_pagare=rimanente_da_pagare, user=get_user_by_id(session.get('user_id')))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' not in session or not get_user_by_id(session['user_id'])['is_admin']:
        flash('Solo un amministratore può registrare nuovi utenti.', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        username, email, password = request.form['username'], request.form['email'], request.form['password']
        db = get_db()
        try:
            if not get_user_by_username(username):
                db.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (username, email, generate_password_hash(password)))
                db.commit()
                flash(f'Utente {username} registrato con successo!', 'success')
                return redirect(url_for('manage_users'))
            else:
                flash('Username già esistente.', 'error')
        except sqlite3.IntegrityError:
            flash('Email già in uso da un altro utente.', 'error')
    return render_template('register.html', user=get_user_by_id(session.get('user_id')))

@app.route('/manage_users')
def manage_users():
    if 'user_id' not in session or not get_user_by_id(session['user_id'])['is_admin']:
        flash('Accesso non autorizzato.', 'error')
        return redirect(url_for('index'))
    users = get_db().execute("SELECT id, username, email, is_admin FROM users ORDER BY username").fetchall()
    return render_template('manage_users.html', users=users, user=get_user_by_id(session.get('user_id')))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session or not get_user_by_id(session['user_id'])['is_admin']:
        flash('Accesso non autorizzato.', 'error')
        return redirect(url_for('index'))
    db = get_db()
    if request.method == 'POST':
        for key, value in request.form.items():
            db.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
        db.commit()
        flash('Impostazioni SMTP salvate con successo!', 'success')
        return redirect(url_for('settings'))
    configs_db = db.execute("SELECT key, value FROM config").fetchall()
    config_dict = {row['key']: row['value'] for row in configs_db}
    return render_template('settings.html', config=config_dict, user=get_user_by_id(session.get('user_id')))

@app.route('/test_email', methods=['POST'])
def test_email():
    if 'user_id' not in session or not get_user_by_id(session['user_id'])['is_admin']:
        return "Non autorizzato", 403
    admin_user = get_user_by_id(session['user_id'])
    recipient = admin_user['email']
    if not recipient:
        flash('L\'utente amministratore non ha un\'email registrata.', 'error')
        return redirect(url_for('settings'))
    subject = "Email di Prova - Gestionale Matrimonio"
    html_body = f"<h1>Ciao {admin_user['username']}!</h1><p>Se hai ricevuto questa email, significa che la configurazione SMTP funziona correttamente.</p>"
    text_body = f"Ciao {admin_user['username']}! Se hai ricevuto questa email, significa che la configurazione SMTP funziona correttamente."
    success, message = send_email(subject, [recipient], text_body, html_body)
    if success:
        flash(f"Email di prova inviata a {recipient}. Controlla la tua casella di posta.", 'success')
    else:
        flash(f"Impossibile inviare l'email di prova. {message}", 'error')
    return redirect(url_for('settings'))

@app.route('/test_reminder', methods=['POST'])
def test_reminder():
    if 'user_id' not in session or not get_user_by_id(session['user_id'])['is_admin']:
        flash('Accesso non autorizzato.', 'error')
        return redirect(url_for('index'))
    status_message = check_and_send_reminders()
    flash(f"Test dei promemoria eseguito. Risultato: {status_message}", 'success')
    return redirect(url_for('settings'))

# --- AVVIO APP ---
if __name__ == '__main__':
    with app.app_context():
        create_tables(get_db())
    scheduler.add_job(id='daily_reminder_task', func=check_and_send_reminders, trigger='cron', hour=8, minute=0)
    if not scheduler.running:
        scheduler.start()
    is_debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    if is_debug and not os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("Scheduler in attesa del riavvio del reloader Werkzeug.")
    if is_debug:
        print(">>> AVVIO IN MODALITÀ SVILUPPO (DEBUG) <<<")
        app.run(host='127.0.0.1', port=5001, debug=True)
    else:
        print(f">>> AVVIO IN MODALITÀ PRODUZIONE CON WAITRESS SU http://127.0.0.1:5001 <<<")
        serve(app, host='0.0.0.0', port=5001)