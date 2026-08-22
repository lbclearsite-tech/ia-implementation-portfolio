import json
from collections import Counter

FICHIER_LOG = "logs/logs_routage.jsonl"

# --- Lecture ---
entrees = []
with open(FICHIER_LOG, "r", encoding="utf-8") as f:
    for ligne in f:
        ligne = ligne.strip()
        if ligne:
            entrees.append(json.loads(ligne))

if not entrees:
    print("Log de routage vide.")
    exit()

# --- Calculs ---
total = len(entrees)
repartition = Counter(e["agent"] for e in entrees)
n_aucun = repartition.get("aucun", 0)

# --- Rapport ---
print("=" * 55)
print("ANALYSE DU ROUTAGE")
print("=" * 55)
print(f"Décisions totales : {total}")
print("\nRépartition par agent :")
for agent, n in repartition.most_common():
    print(f"  {agent:<14} : {n} ({n/total*100:.1f} %)")
print(f"\nTaux de 'aucun'   : {n_aucun/total*100:.1f} %")
print("=" * 55)