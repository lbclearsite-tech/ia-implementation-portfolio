# Projet : générateur de devis BTP — LB ClearSite

## Contexte
Script Python qui génère des devis PDF pour des artisans BTP.
Client = TPE/PME françaises (peinture, plomberie, menuiserie).

## Stack
- Python 3.14, fpdf2, python-dotenv
- PDF généré dans /output/
- Clé API dans .env (ne jamais afficher ni modifier)

## Conventions
- Tous les montants en EUR, TVA à 10 % par défaut
- Phrases courtes dans les commentaires (style LB)
- Ne jamais écraser un PDF existant sans confirmation