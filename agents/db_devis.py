import sqlite3
import os

DB_PATH = "data/devis.db"


def _assurer_base():
    """Crée le dossier data/ et la table devis si absents. Idempotent."""
    os.makedirs("data", exist_ok=True)
    connexion = sqlite3.connect(DB_PATH)
    curseur = connexion.cursor()
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


def enregistrer_devis(devis):
    """Insère un devis validé dans la base SQLite. Renvoie l'id créé."""
    _assurer_base()  # garantit dossier + table, en local comme en ligne

    connexion = sqlite3.connect(DB_PATH)
    curseur = connexion.cursor()

    prestation = " / ".join(l["designation"] for l in devis.get("lignes", []))

    curseur.execute("""
        INSERT INTO devis (client, date, prestation, total_ht, tva_pct, total_ttc)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        devis.get("client"),
        devis.get("date"),
        prestation,
        devis.get("total_ht"),
        devis.get("tva_pct"),
        devis.get("total_ttc"),
    ))

    id_cree = curseur.lastrowid
    connexion.commit()
    connexion.close()
    return id_cree