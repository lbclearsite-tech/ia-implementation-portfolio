import anthropic
from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel
from typing import List, Optional
from . import pdf_devis
from . import db_devis

load_dotenv()

with open("config/config_entreprise.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TEMPERATURE = 0
MAX_TOKENS = 1800
MAX_RETRIES = 3

class LigneDevis(BaseModel):
    designation: str
    quantite: float
    unite: str
    prix_ht: float
    total_ht: float

class Devis(BaseModel):
    entreprise: str
    siret: str
    client: str
    total_ht: float
    tva_montant: float
    total_ttc: float
    tva_pct: float
    lignes: List[LigneDevis]
    adresse_entreprise: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None

# Définition de l'outil
outil_devis = {
    "name": "generer_devis",
    "description": "Génère un devis BTP structuré à partir des informations du chantier.",
    "input_schema": {
        "type": "object",
        "properties": {
            "client": {"type": "string"},
            "adresse_client": {"type": "string"},
            "telephone_client": {"type": "string"},
            "email_client": {"type": "string"},
            "adresse_chantier": {"type": "string"},
            "date": {"type": "string"},
            "date_debut_travaux": {"type": "string"},
            "date_fin_travaux": {"type": "string"},
            "validite": {"type": "string"},
            "reference": {"type": "string"},
            "lignes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "designation": {"type": "string"},
                        "quantite": {"type": "number"},
                        "unite": {"type": "string"},
                        "prix_ht": {"type": "number"},
                        "total_ht": {"type": "number"}
                    },
                    "required": ["designation", "quantite", "unite", "prix_ht", "total_ht"]
                }
            },
            "total_ht": {"type": "number"},
            "tva_pct": {"type": "number"},
            "tva_montant": {"type": "number"},
            "total_ttc": {"type": "number"},
            "acompte": {"type": "string"},
            "solde": {"type": "string"},
            "delai": {"type": "string"}
        },
        "required": ["client", "adresse_client", "date", "lignes", "total_ht", "tva_pct", "tva_montant", "total_ttc"]
    }
}

client_api = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generer_apercu(client_nom, travaux, main_oeuvre, materiaux, tva="10"):
    """Génère et valide un devis. Renvoie le dict SANS aucun effet de bord.
    Aucune écriture (JSON/PDF/base) : c'est l'aperçu avant la porte de validation."""
    prompt = f"""Genere un devis BTP avec ces informations :

ENTREPRISE (utilise exactement ces données, n'invente rien) :
- Entreprise : {config['entreprise']}
- Forme juridique : {config['forme_juridique']}
- Adresse : {config['adresse_entreprise']}
- Téléphone : {config['telephone']}
- Email : {config['email']}
- SIRET : {config['siret']}
- RCS : {config['rcs']}
- Code APE : {config['code_ape']}
- TVA intra : {config['tva_intra']}
- Assurance décennale : {config['assurance_decennale']}
- IBAN : {config['iban']}
- BIC : {config['bic']}

CHANTIER :
- Client : {client_nom}
- Travaux : {travaux}
- Main d'oeuvre : {main_oeuvre} EUR HT
- Materiaux : {materiaux} EUR HT
- TVA : {tva}%"""

    devis = None
    derniere_erreur = None

    for tentative in range(1, MAX_RETRIES + 1):
        messages = [{"role": "user", "content": prompt}]

        if derniere_erreur:
            messages.append({
                "role": "assistant",
                "content": "[tentative précédente refusée]"
            })
            messages.append({
                "role": "user",
                "content": f"Erreur de validation : {derniere_erreur}. Corrige et réessaie."
            })

        message = client_api.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=MAX_TOKENS,
            tools=[outil_devis],
            tool_choice={"type": "any"},
            system="""Tu es un assistant commercial BTP. Tu génères des devis structurés.
Pour les travaux de rénovation résidentielle de plus de 2 ans, applique obligatoirement la TVA à 10% (art. 279-0 bis du CGI).
Les données entreprise (SIRET, IBAN, assurance, etc.) sont fournies séparément — ne les génère pas.""",
            messages=messages
        )

        devis_chantier = message.content[0].input
        devis = {**devis_chantier, **config}

        try:
            Devis(**devis)  # validation Pydantic
            return devis
        except Exception as e:
            derniere_erreur = str(e)
            if tentative == MAX_RETRIES:
                return None


def emettre_devis(devis):
    """Écrit un devis DÉJÀ validé : JSON + PDF + base. Renvoie l'id créé.
    À n'appeler qu'après la porte de validation (humaine ou UI)."""
    client_nom = devis.get("client", "client")

    fichier_sortie = f"outputs/devis/devis_{client_nom}.json"
    with open(fichier_sortie, "w", encoding="utf-8") as fichier:
        json.dump(devis, fichier, ensure_ascii=False, indent=2)

    pdf_devis.generer_pdf(devis)

    id_devis = db_devis.enregistrer_devis(devis)
    return id_devis


def generer_devis(client_nom, travaux, main_oeuvre, materiaux, tva="10"):
    """Version terminal : génère, affiche la porte de validation, puis écrit.
    Réutilise generer_apercu() et emettre_devis()."""
    print("\nGénération du devis...")
    devis = generer_apercu(client_nom, travaux, main_oeuvre, materiaux, tva)

    if devis is None:
        print(f"\nÉchec après {MAX_RETRIES} tentatives. Arrêt.")
        return None

    # --- PORTE DE VALIDATION HUMAINE (terminal) ---
    print("\n" + "=" * 55)
    print("DEVIS À VALIDER AVANT ÉMISSION")
    print("=" * 55)
    print(f"Client       : {devis.get('client')}")
    print(f"TVA          : {devis.get('tva_pct')} %")
    print(f"Total HT     : {devis.get('total_ht')} EUR")
    print(f"Total TTC    : {devis.get('total_ttc')} EUR")
    print("\nPrestations :")
    for ligne in devis.get("lignes", []):
        print(f"  - {ligne['designation']} : {ligne['total_ht']} EUR HT")
    print("=" * 55)

    confirmation = input("Émettre ce devis ? (oui/non) : ").strip().lower()
    if confirmation not in ("oui", "o"):
        print("Devis abandonné. Aucun fichier écrit.")
        return None
    # --- FIN DE LA PORTE ---

    id_devis = emettre_devis(devis)
    print(f"\nDevis émis. JSON + PDF générés, enregistré en base (id {id_devis}).")
    return devis


if __name__ == "__main__":
    print("=== GENERATEUR DE DEVIS BTP ===\n")
    client_nom = input("Nom du client : ")
    travaux = input("Type de travaux : ")
    main_oeuvre = input("Main d'oeuvre HT (EUR) : ")
    materiaux = input("Materiaux HT (EUR) : ")
    tva = input("TVA (%) [defaut 10% renovation] : ") or "10"
    generer_devis(client_nom, travaux, main_oeuvre, materiaux, tva)