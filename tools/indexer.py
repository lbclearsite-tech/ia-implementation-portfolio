import os
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer

# --- Configuration ---
CORPUS_DIR = "data/corpus"
CHROMA_DIR = "data/chroma_db"
CHUNK_SIZE = 500       # caractères par morceau
CHUNK_OVERLAP = 50     # chevauchement entre morceaux

# --- Étape 1 : Lire les PDF ---
def lire_pdf(chemin):
    reader = PdfReader(chemin)
    texte = ""
    for page in reader.pages:
        texte += page.extract_text() or ""
    return texte

# --- Étape 2 : Découper en morceaux (chunking) ---
def decouper(texte, taille=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    morceaux = []
    debut = 0
    while debut < len(texte):
        fin = debut + taille
        morceaux.append(texte[debut:fin])
        debut += taille - overlap
    return morceaux

# --- Étape 3 : Indexer dans Chroma ---
def indexer():
    print("Chargement du modèle d'embeddings...")
    modele = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    
    # Repart de zéro si la collection existe déjà
    try:
        client.delete_collection("corpus_ia")
    except:
        pass
    collection = client.create_collection("corpus_ia")

    pdf_files = [f for f in os.listdir(CORPUS_DIR) if f.endswith(".pdf")]
    
    tous_ids = []
    tous_textes = []
    toutes_metadonnees = []

    for pdf_file in pdf_files:
        print(f"Lecture : {pdf_file}")
        chemin = os.path.join(CORPUS_DIR, pdf_file)
        texte = lire_pdf(chemin)
        morceaux = decouper(texte)
        print(f"  → {len(morceaux)} morceaux")

        for i, morceau in enumerate(morceaux):
            tous_ids.append(f"{pdf_file}_{i}")
            tous_textes.append(morceau)
            toutes_metadonnees.append({"source": pdf_file, "chunk": i})

    print(f"\nCalcul des embeddings ({len(tous_textes)} morceaux au total)...")
    embeddings = modele.encode(tous_textes, show_progress_bar=True).tolist()

    print("Stockage dans Chroma...")
    collection.add(
        ids=tous_ids,
        documents=tous_textes,
        embeddings=embeddings,
        metadatas=toutes_metadonnees
    )

    print(f"\n✓ Indexation terminée. {len(tous_textes)} morceaux stockés dans '{CHROMA_DIR}'.")

if __name__ == "__main__":
    indexer()