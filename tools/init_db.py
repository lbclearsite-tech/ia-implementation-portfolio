import sqlite3

# Connexion : crée le fichier devis.db s'il n'existe pas
connexion = sqlite3.connect("data/devis.db")
curseur = connexion.cursor()

# Création de la table (IF NOT EXISTS : ne plante pas si elle existe déjà)
curseur.execute("""
CREATE TABLE IF NOT EXISTS devis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client TEXT NOT NULL,
    date TEXT,
    prestation TEXT,
    total_ht REAL,
    tva_pct REAL,
    total_ttc REAL
)
""")

connexion.commit()
connexion.close()

print("Base initialisée : data/devis.db (table 'devis' prête)")