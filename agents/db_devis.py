import sqlite3

DB_PATH = "data/devis.db"


def enregistrer_devis(devis):
    """Insère un devis validé dans la base SQLite. Renvoie l'id créé."""
    connexion = sqlite3.connect(DB_PATH)
    curseur = connexion.cursor()

    # On extrait les champs utiles du dict devis
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