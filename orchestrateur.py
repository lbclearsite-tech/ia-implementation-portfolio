import os
import json
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from assistant import repondre
from generateur_devis import generer_devis

load_dotenv()
client = Anthropic()

# --- Définition de l'outil de routage ---
outil_routage = {
    "name": "router_demande",
    "description": "Détermine quel agent doit traiter la demande utilisateur.",
    "input_schema": {
        "type": "object",
        "properties": {
            "agent": {
                "type": "string",
                "enum": ["devis", "documentaire", "aucun"],
                "description": (
                    "devis = créer un devis BTP. "
                    "documentaire = question sur l'IA, l'AI Act, Anthropic. "
                    "aucun = hors périmètre des deux agents."
                )
            },
            "justification": {
                "type": "string",
                "description": "Raison du choix, une phrase."
            }
        },
        "required": ["agent", "justification"]
    }
}

FICHIER_LOG_ROUTAGE = "logs/logs_routage.jsonl"


def logger_routage(demande, agent, justification):
    """Trace chaque décision de routage au format JSONL."""
    entree = {
        "timestamp": datetime.now().isoformat(),
        "demande": demande,
        "agent": agent,
        "justification": justification
    }
    with open(FICHIER_LOG_ROUTAGE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entree, ensure_ascii=False) + "\n")


def router(demande):
    """Renvoie (agent, justification) pour une demande utilisateur."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        tools=[outil_routage],
        tool_choice={"type": "any"},
        messages=[{"role": "user", "content": demande}]
    )
    resultat = message.content[0].input
    return resultat["agent"], resultat["justification"]


def traiter(demande):
    """Route la demande puis exécute l'agent choisi."""
    agent, justif = router(demande)
    print(f"\n[ROUTAGE → {agent.upper()}] {justif}")
    logger_routage(demande, agent, justif)

    if agent == "documentaire":
        return repondre(demande)

    elif agent == "devis":
        print("\nDemande de devis détectée. Saisie des détails :")
        client_nom = input("Nom du client : ")
        travaux = input("Type de travaux : ")
        main_oeuvre = input("Main d'oeuvre HT (EUR) : ")
        materiaux = input("Materiaux HT (EUR) : ")
        tva = input("TVA (%) [defaut 10%] : ") or "10"
        resultat = generer_devis(client_nom, travaux, main_oeuvre, materiaux, tva)
        if resultat is None:
            return "Devis non émis."
        return "Devis généré et enregistré."

    else:  # aucun
        return "Cette demande ne relève d'aucun agent disponible (devis BTP ou documentaire IA)."


if __name__ == "__main__":
    print("=== ORCHESTRATEUR MULTI-AGENTS ===")
    print("Tapez 'quit' pour quitter.\n")
    while True:
        demande = input("Votre demande : ").strip()
        if demande.lower() == "quit":
            break
        if not demande:
            continue
        reponse = traiter(demande)
        print(f"\n{reponse}\n")
        print("-" * 60)