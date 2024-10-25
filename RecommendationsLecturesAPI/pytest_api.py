import requests

# Test de la page d'accueil
def test_home():
    response = requests.get('http://127.0.0.1:5001/')
    assert response.status_code == 200
    assert "Bienvenue sur l'API de Recommandations de Livres" in response.text

# Test de connexion avec des informations incorrectes
def test_login_bad_credentials():
    response = requests.post('http://127.0.0.1:5001/login', json={'username': 'wrong', 'password': 'wrong'})
    assert response.status_code == 401

# Test de connexion avec des informations correctes
def test_login_good_credentials():
    response = requests.post('http://127.0.0.1:5001/login', json={'username': 'admin', 'password': 'password'})
    assert response.status_code == 200
    assert 'access_token' in response.json()

# Test de récupération de la liste des livres après authentification
def test_books_authorized():
    login_response = requests.post('http://127.0.0.1:5001/login', json={'username': 'admin', 'password': 'password'})
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('http://127.0.0.1:5001/books', headers=headers)
    assert response.status_code == 200
