from flask import Flask, render_template, jsonify, request
import logging
import requests

app = Flask(__name__)

# URL de base de l'API backend
BASE_URL = "http://127.0.0.1:5001"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    return jsonify(response.json()), response.status_code

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    token = request.headers.get('Authorization')
    book_title = request.json.get('book_title')
    response = requests.post(f"{BASE_URL}/recommendations", headers={'Authorization': token}, json={"book_title": book_title})
    return jsonify(response.json()), response.status_code

@app.route('/favorites', methods=['POST'])
def add_to_favorites():
    token = request.headers.get('Authorization')
    book_title = request.json.get('book_title')
    book_author = request.json.get('book_author')
    book_thumbnail = request.json.get('book_thumbnail')  # Ajouter ce champ

    response = requests.post(f"{BASE_URL}/favorites", headers={'Authorization': token}, json={"book_title": book_title, "book_author": book_author,"book_thumbnail": book_thumbnail})
    return jsonify(response.json()), response.status_code

@app.route('/favorites', methods=['GET'])
def get_favorites():
    token = request.headers.get('Authorization')
    response = requests.get(f"{BASE_URL}/favorites", headers={'Authorization': token})
    return jsonify(response.json()), response.status_code

if __name__ == "__main__":
    app.run(debug=True, port=5002)
