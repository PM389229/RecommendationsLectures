import os
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Tuple

# Chemins pour les fichiers d'embeddings et de similarité cosinus
EMBEDDINGS_FILE = 'C:\\Users\\pmgue\\Downloads\\ProjetChefDoeuvre\\RecommendationsLectures\\BlocCompétences2\\embeddings.npy'
SIMILARITY_FILE = 'C:\\Users\\pmgue\\Downloads\\ProjetChefDoeuvre\\RecommendationsLectures\\BlocCompétences2\\cosine_sim_embeddings.npy'

# Fonction pour établir une connexion à la base de données PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="RecommendationsLectures",
        user="postgres",
        password="Lrk389229!"
    )

def charger_donnees_et_embeddings() -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Charge les données des livres depuis PostgreSQL et génère/charge les embeddings
    en utilisant TF-IDF pour la vectorisation du texte.
    
    Returns:
        Tuple[pd.DataFrame, np.ndarray]: Les données des livres et leurs embeddings
    """
    # Vérification si les embeddings sont déjà sauvegardés
    if os.path.exists(EMBEDDINGS_FILE):
        print("Chargement des embeddings à partir du fichier")
        
        # Connexion à PostgreSQL pour charger les données des livres
        conn = get_db_connection()
        data = pd.read_sql_query("""
            SELECT l.title, l.description, l.published_year, l.average_rating, l.thumbnail,
                   array_agg(DISTINCT a.author_name) AS authors,
                   array_agg(DISTINCT c.category_name) AS categories
            FROM Livre l
            LEFT JOIN Livre_Auteur la ON l.id_livre = la.id_livre
            LEFT JOIN Auteur a ON la.id_auteur = a.id_auteur
            LEFT JOIN Livre_Categorie lc ON l.id_livre = lc.id_livre
            LEFT JOIN Categorie c ON lc.id_categorie = c.id_categorie
            GROUP BY l.id_livre
        """, conn)
        conn.close()
        
        # Charger les embeddings depuis le fichier
        embeddings = np.load(EMBEDDINGS_FILE)
    else:
        print("Calcul des embeddings pour la première fois")
        
        # Connexion à PostgreSQL pour charger les données des livres
        conn = get_db_connection()
        data = pd.read_sql_query("""
            SELECT l.title, l.description, l.published_year, l.average_rating, l.thumbnail,
                   array_agg(DISTINCT a.author_name) AS authors,
                   array_agg(DISTINCT c.category_name) AS categories
            FROM Livre l
            LEFT JOIN Livre_Auteur la ON l.id_livre = la.id_livre
            LEFT JOIN Auteur a ON la.id_auteur = a.id_auteur
            LEFT JOIN Livre_Categorie lc ON l.id_livre = lc.id_livre
            LEFT JOIN Categorie c ON lc.id_categorie = c.id_categorie
            GROUP BY l.id_livre
        """, conn)
        conn.close()

        # Initialiser le vectoriseur TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=512,  # Limiter le nombre de features
            stop_words='english',  # Supprimer les mots vides en anglais
            ngram_range=(1, 2),  # Utiliser des unigrammes et bigrammes
            min_df=2,  # Ignorer les termes apparaissant dans moins de 2 documents
            strip_accents='unicode'  # Gérer les accents
        )
        
        # Générer les embeddings TF-IDF
        descriptions = data['description'].fillna('')
        embeddings = vectorizer.fit_transform(descriptions).toarray()
        
        # Sauvegarder les embeddings pour les réutiliser plus tard
        np.save(EMBEDDINGS_FILE, embeddings)
        print("Embeddings sauvegardés")
        
        # Sauvegarder également le vocabulaire pour référence future
        vocab_file = EMBEDDINGS_FILE.replace('.npy', '_vocabulary.txt')
        with open(vocab_file, 'w', encoding='utf-8') as f:
            for word in vectorizer.get_feature_names_out():
                f.write(f"{word}\n")
    
    return data, embeddings

# Fonction pour calculer ou charger les similarités cosinus
def calculate_or_load_cosine_similarity(embeddings):
    if os.path.exists(SIMILARITY_FILE):
        print("Chargement des similarités cosinus à partir du fichier")
        cosine_sim_embeddings = np.load(SIMILARITY_FILE)
    else:
        print("Calcul des similarités cosinus pour la première fois")
        cosine_sim_embeddings = calculate_cosine_similarity_in_batches(embeddings, batch_size=100)
        
        # Sauvegarder les similarités pour les réutiliser plus tard
        np.save(SIMILARITY_FILE, cosine_sim_embeddings)
        print("Similarités cosinus sauvegardées")

    return cosine_sim_embeddings

# Fonction pour calculer la similarité cosinus par lots
def calculate_cosine_similarity_in_batches(embeddings, batch_size=100):
    cosine_sim_list = []
    for i in range(0, embeddings.shape[0], batch_size):
        batch_embeddings = embeddings[i:i + batch_size]
        batch_cosine_sim = 1 - np.dot(batch_embeddings, embeddings.T)  # Utilisation de numpy pour calculer la similarité
        cosine_sim_list.append(batch_cosine_sim)
    return np.vstack(cosine_sim_list)  # Retourne un tableau numpy

# Fonction de recommandation qui utilise les embeddings de similarité cosinus
def recommander_livres_sans_categorie(titre_livre, data, cosine_sim_embeddings, user_favorite_titles):
    # Filtrer les livres correspondant au titre depuis `data`
    results = data[data['title'].str.contains(titre_livre, case=False, na=False)]
    if results.empty:
        return []  # Aucun résultat pour le titre donné

    # Obtenir l'indice du livre correspondant
    idx = results.index[0]
    sim_scores = list(enumerate(cosine_sim_embeddings[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    recommendations = []
    for i, score in sim_scores[1:]:  # Commence après l'index 0 (le livre lui-même)
        livre_info = data.iloc[i]

        # Exclure les livres déjà dans les favoris de l'utilisateur
        if livre_info['title'] not in user_favorite_titles:
            recommendations.append({
                'title': livre_info['title'],
                'authors': livre_info['authors'],
                'score': score.item(),
                'thumbnail': livre_info.get('thumbnail'),
                'description': livre_info.get('description', 'No description available.'),
                'published_year': livre_info.get('published_year', 'Unknown'),
                'average_rating': livre_info.get('average_rating', 'Not rated'),
                'categories': livre_info.get('categories', 'Not categorized')
            })

        if len(recommendations) >= 3:
            break

    return recommendations

# Exécution principale pour générer et sauvegarder les embeddings et similarités
if __name__ == "__main__":
    data, embeddings = charger_donnees_et_embeddings()
    cosine_sim_embeddings = calculate_or_load_cosine_similarity(embeddings)
    print("Embeddings et similarités chargés avec succès")
