import numpy as np
from flask import Flask, jsonify

# Charger les embeddings au démarrage de l’API
embeddings = np.load('embeddings/embeddings.npy')

app = Flask(__name__)

@app.route('/')
def home():
    return "Bienvenue sur l'API de Recommandations de Livres"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
    print("API déployée avec succès.")
