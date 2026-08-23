import os
import streamlit as st
from dotenv import load_dotenv

# Chargement de la clé API — local (.env) ET en ligne (secrets Streamlit)
load_dotenv()
try:
    if "ANTHROPIC_API_KEY" in st.secrets:
        os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
except st.errors.StreamlitSecretNotFoundError:
    pass

# NB : on importe UNIQUEMENT l'agent devis, jamais l'assistant RAG.
# L'assistant charge un modèle d'embedding lourd (sentence-transformers)
# qui dépasse la RAM du tier gratuit Streamlit. Version de démo allégée.
from agents.generateur_devis import generer_apercu, emettre_devis

st.title("Générateur de devis BTP — Démo")
st.write(
    "Démonstration en ligne de l'agent de génération de devis : "
    "sortie structurée validée, et porte de validation humaine avant émission."
)
st.caption(
    "Version allégée pour l'hébergement gratuit. L'assistant documentaire (RAG) "
    "et l'orchestrateur multi-agents tournent dans la version complète en local."
)
st.divider()

st.header("Générer un devis")

client_nom = st.text_input("Nom du client")
travaux = st.text_input("Type de travaux")
main_oeuvre = st.text_input("Main d'œuvre HT (EUR)")
materiaux = st.text_input("Matériaux HT (EUR)")
tva = st.text_input("TVA (%)", value="10")

# --- CLIC 1 : générer l'aperçu, SANS rien écrire ---
if st.button("Générer le devis (aperçu)"):
    if client_nom.strip() and travaux.strip():
        with st.spinner("Génération du devis..."):
            devis = generer_apercu(client_nom, travaux, main_oeuvre, materiaux, tva)
        if devis is None:
            st.error("Échec de la génération du devis.")
        else:
            st.session_state["devis_en_attente"] = devis
    else:
        st.warning("Le nom du client et le type de travaux sont obligatoires.")

# --- Aperçu + porte de validation (deux clics) ---
if "devis_en_attente" in st.session_state:
    devis = st.session_state["devis_en_attente"]

    st.subheader("Devis à valider avant émission")
    st.write(f"**Client :** {devis.get('client')}")
    st.write(f"**TVA :** {devis.get('tva_pct')} %")
    st.write(f"**Total HT :** {devis.get('total_ht')} EUR")
    st.write(f"**Total TTC :** {devis.get('total_ttc')} EUR")
    st.write("**Prestations :**")
    for ligne in devis.get("lignes", []):
        st.write(f"- {ligne['designation']} : {ligne['total_ht']} EUR HT")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Valider et émettre"):
            id_devis = emettre_devis(devis)
            st.success(f"Devis émis et enregistré en base (id {id_devis}).")
            del st.session_state["devis_en_attente"]
    with col2:
        if st.button("❌ Abandonner"):
            del st.session_state["devis_en_attente"]
            st.info("Devis abandonné. Aucun fichier écrit.")