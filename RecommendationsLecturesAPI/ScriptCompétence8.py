import os
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer

# Mettre à jour les chemins d'accès vers les fichiers existants
EMBEDDINGS_FILE = 'C:\\Users\\pmgue\\Downloads\\ProjetChefDoeuvre\\RecommendationsLectures\\BlocCompétences2\\embeddings.pt'
DATA_FILE = 'C:\\Users\\pmgue\\Downloads\\ProjetChefDoeuvre\\RecommendationsLectures\\StockDatas\\final_dataset_clean_THUMBNAILS_with_images_updated.csv'
SIMILARITY_FILE = 'C:\\Users\\pmgue\\Downloads\\ProjetChefDoeuvre\\RecommendationsLectures\\BlocCompétences2\\cosine_sim_embeddings.pt'

# Fonction pour charger ou calculer les données et embeddings
def charger_donnees_et_embeddings():
    # Charger les données du fichier CSV si elles ne sont pas déjà enregistrées
    if os.path.exists(DATA_FILE) and os.path.exists(EMBEDDINGS_FILE):
        print("Chargement des données et des embeddings à partir des fichiers")
        data = pd.read_csv(DATA_FILE)
        embeddings = torch.load(EMBEDDINGS_FILE)
    else:
        print("Calcul des embeddings pour la première fois")
        data = pd.read_csv('C:\\Users\\pmgue\\Downloads\\ProjetChefDoeuvre\\RecommendationsLectures\\StockDatas\\final_dataset_clean_THUMBNAILS_with_images_updated.csv')
        
        # Charger le modèle SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model.to(device)
        
        # Encoder les descriptions des livres en embeddings
        model.max_seq_length = 512
        embeddings = model.encode(data['description'].fillna(''), convert_to_tensor=True)

        # Sauvegarder les données et embeddings pour les réutiliser plus tard
        data.to_csv(DATA_FILE, index=False)
        torch.save(embeddings, EMBEDDINGS_FILE)
        print("Données et embeddings sauvegardés")

    return data, embeddings

# Fonction pour calculer ou charger les similarités cosinus
def calculate_or_load_cosine_similarity(embeddings):
    if os.path.exists(SIMILARITY_FILE):
        print("Chargement des similarités cosinus à partir du fichier")
        cosine_sim_embeddings = torch.load(SIMILARITY_FILE)
    else:
        print("Calcul des similarités cosinus pour la première fois")
        cosine_sim_embeddings = calculate_cosine_similarity_in_batches(embeddings, batch_size=100)

        # Sauvegarder les similarités pour les réutiliser plus tard
        torch.save(cosine_sim_embeddings, SIMILARITY_FILE)
        print("Similarités cosinus sauvegardées")

    return cosine_sim_embeddings

# Fonction pour calculer la similarité cosinus par lots
def calculate_cosine_similarity_in_batches(embeddings, batch_size=100):
    cosine_sim_list = []
    for i in range(0, embeddings.shape[0], batch_size):
        batch_embeddings = embeddings[i:i + batch_size]
        batch_cosine_sim = torch.mm(batch_embeddings, embeddings.T)
        cosine_sim_list.append(batch_cosine_sim)
    return torch.cat(cosine_sim_list)


def recommander_livres_sans_categorie(titre_livre, data, cosine_sim_embeddings, user_favorite_titles):
    # Trouver l'index du livre demandé
    results = data[data['title'].str.contains(titre_livre, case=False, na=False)]
    if results.empty:
        return []  # Aucun résultat pour le titre donné

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
                'thumbnail': livre_info.get('thumbnail')  # Ajout de la vignette
            })
        
        if len(recommendations) >= 3:  # Limite à 3 recommandations
            break

    return recommendations


# Exécution principale pour générer et sauvegarder les embeddings et similarités
if __name__ == "__main__":
    data, embeddings = charger_donnees_et_embeddings()
    cosine_sim_embeddings = calculate_or_load_cosine_similarity(embeddings)
    print("Embeddings et similarités chargés avec succès")
