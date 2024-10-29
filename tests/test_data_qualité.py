import pandas as pd

# Chargement du fichier CSV
data = pd.read_csv('data/final_dataset_clean.csv')

def test_data_qualité():
    assert data['title'].notnull().all(), "Certaines entrées de titres sont nulles."
    assert data['description'].notnull().all(), "Certaines descriptions sont nulles."
    assert data['average_rating'].between(0, 5).all(), "Certaines notes moyennes sont hors limites."

if __name__ == "__main__":
    test_data_qualité()
    print("Test de qualité des données : OK")
