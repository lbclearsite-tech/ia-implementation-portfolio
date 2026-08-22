import json
from agents.assistant import repondre
from datetime import datetime

# --- Configuration ---
FICHIER_TESTS = "config/tests_golden.json"
PHRASE_REFUS = "Je ne trouve pas"

# --- Chargement des tests ---
with open(FICHIER_TESTS, "r", encoding="utf-8") as f:
    tests = json.load(f)

# --- Exécution des tests ---
resultats = []
print(f"Lancement de {len(tests)} tests...\n")

for test in tests:
    print(f"[{test['id']}] {test['question'][:60]}...")
    reponse = repondre(test["question"], source="eval")
    print(f"  RÉPONSE : {reponse[:300]}\n")
    
    debut = reponse.strip()[:200]
    refus = PHRASE_REFUS in debut
    
    if test["type"] == "in_corpus":
        succes = not refus
    else:
        succes = refus
    
    resultats.append({
        "id": test["id"],
        "type": test["type"],
        "succes": succes,
        "reponse": reponse[:150]
    })
    
    statut = "✓" if succes else "✗"
    print(f"  {statut} {'OK' if succes else 'ÉCHEC'}\n")

# --- Rapport final ---
total = len(resultats)
reussis = sum(1 for r in resultats if r["succes"])
in_corpus = [r for r in resultats if r["type"] == "in_corpus"]
out_corpus = [r for r in resultats if r["type"] == "out_of_corpus"]

score_in = sum(1 for r in in_corpus if r["succes"])
score_out = sum(1 for r in out_corpus if r["succes"])

print("=" * 60)
print(f"SCORE GLOBAL     : {reussis}/{total}")
print(f"In corpus        : {score_in}/{len(in_corpus)}")
print(f"Out of corpus    : {score_out}/{len(out_corpus)}")
print("=" * 60)

# --- Export du rapport ---
rapport = {
    "timestamp": datetime.now().isoformat(),
    "score_global": f"{reussis}/{total}",
    "taux_reussite": round(reussis / total * 100, 1),
    "score_in_corpus": f"{score_in}/{len(in_corpus)}",
    "score_out_corpus": f"{score_out}/{len(out_corpus)}",
    "echecs": [r["id"] for r in resultats if not r["succes"]],
    "details": resultats
}

nom_fichier = f"outputs/rapports/rapport_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(nom_fichier, "w", encoding="utf-8") as f:
    json.dump(rapport, f, ensure_ascii=False, indent=2)

print(f"\nRapport exporté : {nom_fichier}")