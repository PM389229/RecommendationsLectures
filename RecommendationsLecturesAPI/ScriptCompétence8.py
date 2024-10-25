# Installation des packages nécessaires (à commenter si déjà installés)
# %pip install torch sentence-transformers pandas scikit-learn

# 1. Chargement des bibliothèques
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer

# 2. Fonction pour charger les données et les embeddings
def charger_donnees_et_embeddings():
    # Charger les données du fichier CSV
    data = pd.read_csv('C:\\Users\\User\\Downloads\\CoursAlternance\\Chefoeuvre\\RecommendationsLectures\\final_dataset_clean.csv')

    # Charger le modèle SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    # Encoder les descriptions des livres en embeddings
    model.max_seq_length = 512
    embeddings = model.encode(data['description'].fillna(''), convert_to_tensor=True)

    return data, embeddings

# 3. Fonction pour calculer la similarité cosinus
def calculate_cosine_similarity_in_batches(embeddings, batch_size=100):
    cosine_sim_list = []
    for i in range(0, embeddings.shape[0], batch_size):
        batch_embeddings = embeddings[i:i + batch_size]
        batch_cosine_sim = torch.mm(batch_embeddings, embeddings.T)
        cosine_sim_list.append(batch_cosine_sim)
    return torch.cat(cosine_sim_list)

# 4. Fonction pour recommander des livres
def recommander_livres_sans_categorie(titre_livre, data, cosine_sim_embeddings):
    results = data[data['title'].str.contains(titre_livre, case=False, na=False)]
    
    if results.empty:
        return []

    idx = results.index[0]
    sim_scores = list(enumerate(cosine_sim_embeddings[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    recommendations = []
    for i, score in sim_scores[1:4]:
        livre_info = data.iloc[i]
        recommendations.append({
            'title': livre_info['title'],
            'authors': livre_info['authors'],
            'score': score.item()  # Convertir le score de similarité en format standard Python
        })
    
    return recommendations
