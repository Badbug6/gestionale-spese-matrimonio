import os
import pytest
from app import app as flask_app

@pytest.fixture
def client():
    # Usa un percorso temporaneo gestito da pytest per il database
    # Questo è più pulito e sicuro
    db_path = "test_wedding.db"
    
    flask_app.config.update({
        "TESTING": True,
        "DATABASE": db_path,
        "WTF_CSRF_ENABLED": False # Disabilita la protezione CSRF per i test
    })

    # Assicurati che non esista un db di test da sessioni precedenti
    if os.path.exists(db_path):
        os.remove(db_path)

    with flask_app.test_client() as client:
        with flask_app.app_context():
            from app import create_tables, get_db
            # La prima volta che viene chiamato, crea il file del database
            create_tables(get_db())
        
        yield client

    # Pulizia
    os.remove(db_path)


def test_index_redirects_anonymous(client):
    """Testa che la homepage reindirizzi alla creazione admin se il DB è vuoto."""
    response = client.get('/')
    assert response.status_code == 302
    assert '/create_admin' in response.headers['Location']

def test_auth_pages_load(client):
    """Testa che le pagine di autenticazione si carichino."""
    assert client.get('/login').status_code == 200
    assert client.get('/create_admin').status_code == 200

def test_full_auth_and_setup_flow(client):
    """Testa l'intero flusso: crea admin -> imposta budget -> login -> logout."""
    
    # Step 1: Crea admin
    response_create = client.post('/create_admin', data={
        'username': 'testadmin',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response_create.status_code == 302
    assert '/setup' in response_create.headers['Location']
    
    # Step 2: Imposta budget
    response_setup = client.post('/setup', data={'budget': '20000'})
    assert response_setup.status_code == 302
    assert '/login' in response_setup.headers['Location']
    
    # Step 3: Login
    response_login = client.post('/login', data={
        'username': 'testadmin',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response_login.status_code == 200
    assert b'Ciao, testadmin!' in response_login.data
    
    # Step 4: Logout
    response_logout = client.get('/logout', follow_redirects=True)
    assert response_logout.status_code == 200
    # Dopo il logout, dovremmo vedere il messaggio di avvenuto logout
    assert b'Sei stato disconnesso.' in response_logout.data