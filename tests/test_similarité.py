import numpy as np
import torch

# Charger les embeddings générés
embeddings = torch.tensor(np.load('embeddings/embeddings.npy'))

def validation_cosine_similarity():
    cosine_sim = torch.mm(embeddings, embeddings.T)
    assert cosine_sim.shape == (embeddings.shape[0], embeddings.shape[0]), "Dimensions incorrectes de la matrice de similarité cosinus."
    assert torch.allclose(cosine_sim, cosine_sim.T, atol=1e-6), "La matrice de similarité cosinus n'est pas symétrique."

if __name__ == "__main__":
    validation_cosine_similarity()
    print("Validation des similarités cosinus : OK")
