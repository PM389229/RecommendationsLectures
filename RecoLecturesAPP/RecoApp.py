from flask import Flask, render_template, jsonify, request
import logging
import requests
import time

app = Flask(__name__)

# URL de base de l'API backend
BASE_URL = "https://projetchefdoeuvre.osc-fr1.scalingo.io"

def safe_json_response(response):
    try:
        return response.json()
    except ValueError:
        # Log an error if JSON decoding fails
        app.logger.error("Failed to decode JSON response")
        return {"error": "Invalid JSON response from server"}, 500


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    start_time = time.time()
    
    try:
        # Envoyer la requête POST au backend avec un timeout de 10 secondes
        response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password}, timeout=10)
        response.raise_for_status()  # Vérifie si la requête a réussi
        
        # Utiliser la fonction pour gérer la réponse JSON en toute sécurité
        json_data = safe_json_response(response)
    
    except requests.exceptions.Timeout as e:
        app.logger.error(f"Request timeout: {e}")
        return jsonify({"error": "Timeout occurred"}), 504
    
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request error: {e}")
        app.logger.error(f"Response content: {response.text if response else 'No response'}")
        return jsonify({"error": "Request failed"}), 500
    
    end_time = time.time()
    app.logger.info(f"Login request took {end_time - start_time} seconds")
    
    # Retourne les données JSON si la requête a réussi
    return jsonify(json_data), response.status_code


@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    token = request.headers.get('Authorization')
    book_title = request.json.get('book_title')
    
    try:
        response = requests.post(
            f"{BASE_URL}/recommendations",
            headers={'Authorization': token},
            json={"book_title": book_title},
            timeout=10
        )
        response.raise_for_status()
        json_data = safe_json_response(response)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request error in get_recommendations: {e}")
        return jsonify({"error": "Request failed"}), 500

    return jsonify(json_data), response.status_code


@app.route('/favorites', methods=['POST'])
def add_to_favorites():
    token = request.headers.get('Authorization')
    book_data = {
        "book_title": request.json.get('book_title'),
        "book_author": request.json.get('book_author'),
        "book_thumbnail": request.json.get('book_thumbnail'),
        "book_description": request.json.get('book_description'),
        "book_published_year": request.json.get('book_published_year'),
        "book_average_rating": request.json.get('book_average_rating'),
        "book_categories": request.json.get('book_categories')
    }

    try:
        response = requests.post(
            f"{BASE_URL}/favorites",
            headers={'Authorization': token},
            json=book_data,
            timeout=10
        )
        response.raise_for_status()
        json_data = safe_json_response(response)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request error in add_to_favorites: {e}")
        return jsonify({"error": "Request failed"}), 500

    return jsonify(json_data), response.status_code


@app.route('/favorites', methods=['GET'])
def get_favorites():
    token = request.headers.get('Authorization')
    
    try:
        response = requests.get(
            f"{BASE_URL}/favorites",
            headers={'Authorization': token},
            timeout=10
        )
        response.raise_for_status()
        json_data = safe_json_response(response)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request error in get_favorites: {e}")
        return jsonify({"error": "Request failed"}), 500

    return jsonify(json_data), response.status_code


if __name__ == "__main__":
    app.run(debug=True, port=5002)
