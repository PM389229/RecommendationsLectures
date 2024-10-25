from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

# URL de base de l'API existante
BASE_URL = "http://127.0.0.1:5001"

# Route pour la page d'accueil
@app.route('/')
def index():
    return render_template('index.html')  # Va charger le fichier HTML dans /templates

# Route pour l'authentification
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"msg": "Login failed"}), 401

# Route pour obtenir les recommandations
@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    token = request.json.get('token')
    book_title = request.json.get('book_title')
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/recommendations", json={"book_title": book_title}, headers=headers)
    
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"msg": "Error fetching recommendations"}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5002)  # L'application tourne sur le port 5002
