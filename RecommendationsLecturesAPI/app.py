from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ScriptCompétence8 import charger_donnees_et_embeddings, calculate_or_load_cosine_similarity, recommander_livres_sans_categorie
from prometheus_client import Gauge, start_http_server
from pymongo import MongoClient
import numpy as np
import psycopg2
import logging
import traceback
from flask_cors import CORS  # Import CORS

# Configuration des logs
logging.basicConfig(filename='access.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)  # Active CORS pour toutes les routes
# Connexion à MongoDB
mongo_client = MongoClient("mongodb://admin:admin@localhost:27019")
db = mongo_client["RecoLecturesDB"]
favorites_collection = db["favorites"]

# Démarrage du serveur Prometheus
start_http_server(8001)

# Création des métriques Prometheus
similarity_mean_gauge = Gauge('recommendation_similarity_mean', 'Mean similarity score of recommendations')
similarity_std_gauge = Gauge('recommendation_similarity_std', 'Standard deviation of similarity scores for recommendations')
popularity_mean_gauge = Gauge('recommendation_popularity_mean', 'Mean popularity rating of recommended books')

# JWT Configuration
app.config['JWT_SECRET_KEY'] = '88dd82c94b29ad11ffaadd4c3d369e309b7bd2ae4100b3598140a895149c5b8b'
jwt = JWTManager(app)

# Chargement des données et embeddings
data, embeddings = charger_donnees_et_embeddings()
cosine_sim_embeddings = calculate_or_load_cosine_similarity(embeddings)

# Limitation des requêtes
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
limiter.init_app(app)
app.config['RATELIMIT_HEADERS_ENABLED'] = True

@app.route('/login', methods=['POST'])
@limiter.limit("15 per minute")
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username == "admin" and password == "password":
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401




@app.route('/recommendations', methods=['POST'])
@jwt_required()
def get_recommendations():
    book_title = request.json.get('book_title')
    user_id = get_jwt_identity()

    # Récupération des favoris de l'utilisateur
    user_favorites_doc = favorites_collection.find_one({"user_id": user_id})
    user_favorite_titles = [fav['title'] for fav in user_favorites_doc["favorite_books"]] if user_favorites_doc else []
    
    if book_title:
        recommendations = recommander_livres_sans_categorie(book_title, data, cosine_sim_embeddings, user_favorite_titles)

        # Ajout de détails supplémentaires pour chaque recommandation
        for rec in recommendations:
            livre_info = data.loc[data['title'] == rec['title']].iloc[0]
            rec['description'] = livre_info.get('description', 'No description available.')
            rec['published_year'] = livre_info.get('published_year', 'Unknown')
            rec['average_rating'] = livre_info.get('average_rating', 'Not rated')
            rec['categories'] = livre_info.get('categories', 'Not categorized')
            rec['thumbnail'] = livre_info.get('thumbnail', '')

        # Calcul des métriques
        similarity_scores = [rec['score'] for rec in recommendations]
        similarity_mean = np.mean(similarity_scores)
        similarity_std = np.std(similarity_scores)
        similarity_mean_gauge.set(similarity_mean)
        similarity_std_gauge.set(similarity_std)
        
        popularity_scores = [rec.get('average_rating', 0) for rec in recommendations]
        popularity_mean = np.mean(popularity_scores) if popularity_scores else 0
        popularity_mean_gauge.set(popularity_mean)
        
        return jsonify(recommendations)
    return jsonify({"msg": "No book title provided"}), 400





@app.route('/favorites', methods=['POST'])
@jwt_required()
def add_to_favorites():
    user_id = get_jwt_identity()
    book_title = request.json.get('book_title')
    book_author = request.json.get('book_author')
    book_thumbnail = request.json.get('book_thumbnail')  # Récupérer la vignette
    
    new_favorite = {"title": book_title, "author": book_author,"thumbnail": book_thumbnail}
    user_favorites = favorites_collection.find_one({"user_id": user_id})

    if user_favorites:
        if new_favorite not in user_favorites["favorite_books"]:
            favorites_collection.update_one({"user_id": user_id}, {"$push": {"favorite_books": new_favorite}})
    else:
        favorites_collection.insert_one({"user_id": user_id, "favorite_books": [new_favorite]})

    return jsonify({"msg": "Livre ajouté aux favoris"}), 200



@app.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    user_id = get_jwt_identity()
    user_favorites = favorites_collection.find_one({"user_id": user_id})
    return jsonify(user_favorites["favorite_books"] if user_favorites else []), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
