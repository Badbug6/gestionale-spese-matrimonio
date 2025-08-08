import sqlite3

# Connessione al database (se non esiste, lo crea)
connection = sqlite3.connect('wedding.db')
cursor = connection.cursor()

# Creazione della tabella 'spese'
cursor.execute('''
CREATE TABLE IF NOT EXISTS spese (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descrizione TEXT NOT NULL,
    importo REAL NOT NULL,
    categoria TEXT NOT NULL,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Salviamo le modifiche e chiudiamo la connessione
connection.commit()
connection.close()

print("Database 'wedding.db' e tabella 'spese' creati con successo!")