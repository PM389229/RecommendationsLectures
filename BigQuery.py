from google.cloud import bigquery
from google.oauth2 import service_account

# Chemin vers le fichier de clé JSON
key_path = r"C:\Users\User\Downloads\CoursAlternance\Chefoeuvre\RecommendationsLectures\singular-facet-433313-t8-58d5ddafa06b.json"


# Initialiser les identifiants du service account
credentials = service_account.Credentials.from_service_account_file(key_path)

# Initialiser le client BigQuery avec les identifiants
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Définir la requête SQL
query = """
    SELECT Title, Authors, Category
    FROM `singular-facet-433313-t8.BooksDataset.BooksDataset`
    WHERE LOWER(Category) LIKE '%history%'
    LIMIT 10
"""

# Exécuter la requête
query_job = client.query(query)

# Obtenir les résultats
results = query_job.result()

# Afficher les résultats
for row in results:
    print(f"Title: {row.Title}, Authors: {row.Authors}, Category: {row.Category}")

# Exporter les résultats dans un fichier CSV (optionnel)
with open("filtered_books.csv", "w") as file:
    for row in results:
        file.write(f"{row.Title},{row.Authors},{row.Category}\n")
