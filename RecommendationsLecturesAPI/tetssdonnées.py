import os

EMBEDDINGS_FILE = 'C:\\Users\\pmgue\\Downloads\\ProjetChefDoeuvre\\RecommendationsLectures\\BlocCompétences2\\embeddings.pt'
DATA_FILE = 'C:\\Users\\pmgue\\Downloads\\ProjetChefDoeuvre\\RecommendationsLectures\\final_dataset_clean.csv'
SIMILARITY_FILE = 'C:\\Users\\pmgue\\Downloads\\ProjetChefDoeuvre\\RecommendationsLectures\\BlocCompétences2\\cosine_sim_embeddings.pt'

print("Existence des fichiers :")
print("Data file exists:", os.path.exists(DATA_FILE))
print("Embeddings file exists:", os.path.exists(EMBEDDINGS_FILE))
print("Cosine similarity file exists:", os.path.exists(SIMILARITY_FILE))
