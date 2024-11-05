import csv
import psycopg2

# Configuration de la connexion à la base de données
conn = psycopg2.connect(
    host="localhost",
    database="RecommendationsLectures",
    user="postgres",
    password="Lrk389229!"  # Remplacez par votre mot de passe
)
cur = conn.cursor()

# Fonction pour insérer un auteur et obtenir son ID
def get_author_id(name):
    cur.execute("SELECT id_auteur FROM auteur WHERE author_name = %s", (name,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        cur.execute("INSERT INTO auteur (author_name) VALUES (%s) RETURNING id_auteur", (name,))
        conn.commit()
        return cur.fetchone()[0]

# Fonction pour insérer une catégorie et obtenir son ID
def get_category_id(name):
    cur.execute("SELECT id_categorie FROM categorie WHERE category_name = %s", (name,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        cur.execute("INSERT INTO categorie (category_name) VALUES (%s) RETURNING id_categorie", (name,))
        conn.commit()
        return cur.fetchone()[0]


# Importer les livres et remplir les tables de jointure
# Importer les livres et remplir les tables de jointure
with open("final_dataset_clean.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Convertir 'published_year' en entier (supprimer les décimales)
        published_year = int(float(row['published_year'])) if row['published_year'] else None

        # Vérifier si le livre existe déjà dans la table
        cur.execute("SELECT id_livre FROM livre WHERE title = %s", (row['title'],))
        livre_existant = cur.fetchone()
        
        if livre_existant:
            # Si le livre existe déjà, obtenir son id_livre pour les jointures
            livre_id = livre_existant[0]
        else:
            # Insertion du livre s'il n'existe pas
            cur.execute("""
                INSERT INTO livre (title, description, published_year, average_rating)
                VALUES (%s, %s, %s, %s) RETURNING id_livre
            """, (row['title'], row['description'], published_year, row['average_rating']))
            livre_id = cur.fetchone()[0]
            conn.commit()

        # Insertion des auteurs et ajout dans la table de jointure
        authors = row['authors'].split(";")
        for author in authors:
            author_id = get_author_id(author.strip())
            cur.execute("INSERT INTO livre_auteur (id_livre, id_auteur) VALUES (%s, %s) ON CONFLICT DO NOTHING", (livre_id, author_id))
            conn.commit()

        # Insertion des catégories et ajout dans la table de jointure
        categories = row['categories'].split(";")
        for category in categories:
            category_id = get_category_id(category.strip())
            cur.execute("INSERT INTO livre_categorie (id_livre, id_categorie) VALUES (%s, %s) ON CONFLICT DO NOTHING", (livre_id, category_id))
            conn.commit()



# Fermeture de la connexion
cur.close()
conn.close()

print("Importation des données terminée avec succès.")
