import zipfile

# permet de créer un package ZIP contenant les embeddings
with zipfile.ZipFile('packages/embeddings_package.zip', 'w') as zipf:
    zipf.write('embeddings/embeddings.npy', arcname='embeddings.npy')
print("Embeddings packagés pour le déploiement.")
