from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_swagger_ui import get_swaggerui_blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ScriptCompétence8 import charger_donnees_et_embeddings, calculate_cosine_similarity_in_batches, recommander_livres_sans_categorie
from prometheus_client import Gauge, Histogram, start_http_server
import numpy as np
import psycopg2
import logging
import traceback    # Import pour capturer les détails de l'exception


app = Flask(__name__)



# Démarrage du serveur Prometheus sur le port 8000 qui est bien libre comme verifié

start_http_server(8001) # Expose les métriques sur http://localhost:8001/metrics. 8000 est deja utilisé sur le projet Django d'alternance


# Création des métriques Prometheus. similarity_mean_gauge, similarity_std_gauge, popularity_mean_gauge : collectent les metriques générées par le modele

similarity_mean_gauge = Gauge('recommendation_similarity_mean', 'Mean similarity score of recommendations')
similarity_std_gauge = Gauge('recommendation_similarity_std', 'Standard deviation of similarity scores for recommendations')
popularity_mean_gauge = Gauge('recommendation_popularity_mean', 'Mean popularity rating of recommended books')

# Configuration du secret pour les tokens JWT
app.config['JWT_SECRET_KEY'] = '88dd82c94b29ad11ffaadd4c3d369e309b7bd2ae4100b3598140a895149c5b8b'
jwt = JWTManager(app)



# Charger les données et calculer les similarités à l'initialisation de l'application Flask
data, embeddings = charger_donnees_et_embeddings()
cosine_sim_embeddings = calculate_cosine_similarity_in_batches(embeddings, batch_size=100)



# Limitation des requêtes en utilisant le stockage en memoire
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://"  # Utilisation du stockage en mémoire locale
)
limiter.init_app(app)

app.config['RATELIMIT_HEADERS_ENABLED'] = True

# Configuration des logs
logging.basicConfig(filename='access.log', level=logging.INFO)




# EN AJOUTANT OU SUPPRIMANT UNE ROUTE IL FAUT MODIFIER SWAGGER.JSON DIRECTEMENT CAR LE FICHIER NE SE MODIFIE PAS AUTOMATIQUEMENT SINON

@app.before_request
def log_request_info():
    logging.info(f"Request from {request.remote_addr}: {request.method} {request.url}")



# Gestionnaire d'erreurs pour les erreurs internes du serveur (statut 500)
@app.errorhandler(500)
def internal_error(error):
    # Affiche la trace complète de l'erreur dans la console
    print(f"Erreur interne : {traceback.format_exc()}")
    # Retourne un message d'erreur personnalisé pour l'utilisateur
    return "Erreur interne du serveur", 500







@app.route('/')
def home():
    return "Bienvenue sur l'API de Recommandations de Livres"




@app.route('/recommendations', methods=['POST'])
@jwt_required()
def get_recommendations():
    user_input = request.json.get('book_title', '')
    if user_input:
        recommendations = recommander_livres_sans_categorie(user_input, data, cosine_sim_embeddings)
        
        # Calcul des métriques de similarité
        similarity_scores = [rec['score'] for rec in recommendations]
        similarity_mean = np.mean(similarity_scores)
        similarity_std = np.std(similarity_scores)
        
        # Enregistrement des métriques de similarité dans Prometheus
        similarity_mean_gauge.set(similarity_mean)
        similarity_std_gauge.set(similarity_std)

        # Calcul de la popularité moyenne des recommandations
        popularity_scores = [rec['average_rating'] for rec in recommendations if 'average_rating' in rec]
        if popularity_scores:
            popularity_mean = np.mean(popularity_scores)
            popularity_mean_gauge.set(popularity_mean)
        
        return jsonify(recommendations)
    return jsonify({"msg": "No book title provided"}), 400







# Connexion à PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="RecommendationsLectures",
        user="postgres",
        password="Lrk389229!"
    )
    return conn

# Authentification avec limite de requêtes
@app.route('/login', methods=['POST'])
@limiter.limit("15 per minute")
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if username != "admin" or password != "password":
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200





# route pour récupérer un livre spécifique par titre
@app.route('/books/title/<string:title>', methods=['GET'])
@jwt_required()
def get_book_by_title(title):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT l.title, l.description, l.published_year, l.average_rating, array_agg(a.author_name) AS authors
        FROM Livre l
        JOIN livre_auteur la ON l.id_livre = la.id_livre
        JOIN Auteur a ON la.id_auteur = a.id_auteur
        WHERE LOWER(l.title) = LOWER(%s)
        GROUP BY l.id_livre;
    ''', (title,))

    book = cur.fetchone()
    cur.close()
    conn.close()

    if book:
        return jsonify({
            'title': book[0],
            'description': book[1],
            'published_year': book[2],
            'average_rating': book[3],
            'authors': book[4]
        }), 200
    else:
        return jsonify({"msg": "Book not found"}), 404





# Récupérer la liste des livres avec leurs auteurs
@app.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT l.title, l.description, l.published_year, l.average_rating, array_agg(a.author_name) AS authors
        FROM Livre l
        JOIN livre_auteur la ON l.id_livre = la.id_livre
        JOIN Auteur a ON la.id_auteur = a.id_auteur
        GROUP BY l.id_livre;
    ''')

    books = cur.fetchall()
    cur.close()
    conn.close()

    book_list = []
    for book in books:
        book_list.append({
            'title': book[0],
            'description': book[1],
            'published_year': book[2],
            'average_rating': book[3],
            'authors': book[4]
        })

    return jsonify(book_list)

# Swagger UI configuration
SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={ 'app_name': "Recommendations Lectures API" }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
