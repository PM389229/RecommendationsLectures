from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd

# Charger les données et le modèle
data = pd.read_csv('StockDatas/final_dataset_clean.csv')
model = SentenceTransformer('all-MiniLM-L6-v2')
descriptions = data['description'].tolist()

# Calculer les embeddings
embeddings = model.encode(descriptions)

# Sauvegarder les embeddings pour utilisation ultérieure
np.save('embeddings/embeddings.npy', embeddings)
print("Embeddings générés et sauvegardés.")
