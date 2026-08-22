import json
from statistics import mean

FICHIER_LOG = "logs_assistant.jsonl"
SEUIL_REFUS = 600  # en dessous : probablement un refus

# --- Lecture du log ---
entrees = []
with open(FICHIER_LOG, "r", encoding="utf-8") as f:
    for ligne in f:
        ligne = ligne.strip()
        if ligne:
            entrees.append(json.loads(ligne))

if not entrees:
    print("Log vide.")
    exit()

# --- Calculs ---
total = len(entrees)
injections = [e for e in entrees if e["injection_detectee"]]
longueurs = [e["longueur_reponse"] for e in entrees]
courtes = [l for l in longueurs if l < SEUIL_REFUS]
prod = [e for e in entrees if e.get("source", "manuel") == "manuel"]
evals = [e for e in entrees if e.get("source") == "eval"]

# --- Rapport ---
print("=" * 55)
print("ANALYSE DES LOGS")
print("=" * 55)
print(f"Requêtes totales        : {total}")
print(f"Injections détectées    : {len(injections)} ({len(injections)/total*100:.1f} %)")
print(f"Longueur moyenne        : {mean(longueurs):.0f} caractères")
print(f"Longueur min / max      : {min(longueurs)} / {max(longueurs)}")
print(f"Réponses courtes (<{SEUIL_REFUS}) : {len(courtes)} ({len(courtes)/total*100:.1f} %)")
print("=" * 55)

print(f"\nRépartition par source :")
print(f"  manuel / production : {len(prod)}")
print(f"  eval (tests)        : {len(evals)}")

if prod:
    long_prod = [e["longueur_reponse"] for e in prod]
    print(f"\nHors tests — {len(prod)} requêtes, longueur moyenne {mean(long_prod):.0f}")

if injections:
    print("\nQuestions signalées :")
    for e in injections:
        print(f"  [{e['timestamp'][:19]}] {e['question'][:70]}")