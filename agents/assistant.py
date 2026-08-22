import os
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from anthropic import Anthropic
import json
from datetime import datetime

load_dotenv()

# --- Configuration ---
CHROMA_DIR = "data/chroma_db"
N_RESULTATS = 5  # nombre de morceaux récupérés par requête

# --- Initialisation ---
modele = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
client_chroma = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client_chroma.get_collection("corpus_ia")
client_claude = Anthropic()

def rechercher(question):
    """Trouve les N morceaux les plus proch es de la question."""
    vecteur = modele.encode([question]).tolist()
    resultats = collection.query(
        query_embeddings=vecteur,
        n_results=N_RESULTATS
    )
    morceaux = []
    for i in range(N_RESULTATS):
        morceaux.append({
            "texte": resultats["documents"][0][i],
            "source": resultats["metadatas"][0][i]["source"]
        })
    return morceaux

def debug_retrieval(question):
    """Affiche les chunks récupérés pour une question."""
    morceaux = rechercher(question)
    print(f"\n--- DEBUG RETRIEVAL ---")
    for i, m in enumerate(morceaux):
        print(f"[Chunk {i+1}] Source : {m['source']}")
        print(f"  {m['texte'][:100]}...")
    print("----------------------\n")
MOTS_SUSPECTS = [
    "ignore tes instructions",
    "ignore les instructions",
    "oublie le contexte",
    "oublie tes instructions",
    "réponds uniquement avec",
    "tu es maintenant",
    "nouveau rôle"
]

def detecter_injection(question):
    """Détecte des patterns d'injection de prompt basiques."""
    question_lower = question.lower()
    for mot in MOTS_SUSPECTS:
        if mot in question_lower:
            return True
    return False

FICHIER_LOG = "logs/logs_assistant.jsonl"

def logger_requete(question, injection_detectee, longueur_reponse, source="manuel"):
    """Écrit une ligne de log au format JSONL."""
    entree = {
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "question": question,
        "injection_detectee": injection_detectee,
        "longueur_reponse": longueur_reponse
    }
    with open(FICHIER_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entree, ensure_ascii=False) + "\n")


def repondre(question, source="manuel"):
    """Construit le prompt avec contexte et interroge Claude."""
    injection = detecter_injection(question)
    
    morceaux = rechercher(question)
    
    contexte = ""
    for i, m in enumerate(morceaux):
        contexte += f"\n[Source {i+1} : {m['source']}]\n{m['texte']}\n"
    
    prompt = f"""Tu es un assistant documentaire spécialisé en IA et gouvernance.

Tu dois répondre UNIQUEMENT en te basant sur les extraits fournis ci-dessous.
Si la réponse ne s'y trouve pas, réponds : "Je ne trouve pas cette information dans les documents."
Cite toujours la source entre crochets.

EXTRAITS :
{contexte}

QUESTION : {question}

RÉPONSE :"""

    message = client_claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    reponse = message.content[0].text
    
    logger_requete(question, injection, len(reponse), source)
    
    return reponse

# --- Boucle interactive ---
if __name__ == "__main__":
    print("Assistant documentaire IA — tapez 'quit' pour quitter\n")
    while True:
        question = input("Votre question : ").strip()
        if question.lower() == "quit":
            break
        if not question:
            continue
        print("\nRecherche en cours...")
        reponse = repondre(question)
        print(f"\nRéponse :\n{reponse}\n")
        print("-" * 60 + "\n")


