import streamlit as st
from orchestrateur import router

st.title("Assistant IA — Devis & Documentation")
st.write("Système multi-agents : génération de devis BTP et assistant documentaire.")
st.divider()

# ============================================================
# ZONE 1 — ROUTAGE + AGENT DOCUMENTAIRE
# ============================================================
demande = st.text_input(
    "Votre demande :",
    placeholder="Ex : Que dit l'AI Act sur les systèmes à haut risque ?"
)

if st.button("Analyser la demande"):
    if demande.strip():
        agent, justification = router(demande)
        st.info(f"**Agent choisi : {agent}**\n\n{justification}")

        if agent == "documentaire":
            with st.spinner("Recherche dans la documentation..."):
                from agents.assistant import repondre
                reponse = repondre(demande)
            st.markdown(reponse)

        elif agent == "devis":
            st.warning("Demande de devis détectée — utilisez le formulaire ci-dessous.")

        else:  # aucun
            st.error("Cette demande ne relève d'aucun agent disponible.")
    else:
        st.warning("Merci de saisir une demande.")

st.divider()

# ============================================================
# ZONE 2 — GÉNÉRATION DE DEVIS (deux étapes = porte de validation)
# ============================================================
st.header("Générer un devis")

client_nom = st.text_input("Nom du client")
travaux = st.text_input("Type de travaux")
main_oeuvre = st.text_input("Main d'œuvre HT (EUR)")
materiaux = st.text_input("Matériaux HT (EUR)")
tva = st.text_input("TVA (%)", value="10")

# --- CLIC 1 : générer et afficher le résumé, SANS rien écrire ---
if st.button("Générer le devis (aperçu)"):
    if client_nom.strip() and travaux.strip():
        with st.spinner("Génération du devis..."):
            from agents.generateur_devis import generer_apercu
            devis = generer_apercu(client_nom, travaux, main_oeuvre, materiaux, tva)

        if devis is None:
            st.error("Échec de la génération du devis.")
        else:
            # On range le devis dans la mémoire de session pour le retrouver au clic 2
            st.session_state["devis_en_attente"] = devis
    else:
        st.warning("Le nom du client et le type de travaux sont obligatoires.")

# --- Affichage du résumé si un devis est en attente de validation ---
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

    # --- CLIC 2 : valider et écrire (JSON + PDF + base) ---
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Valider et émettre"):
            from agents.generateur_devis import emettre_devis
            id_devis = emettre_devis(devis)
            st.success(f"Devis émis et enregistré en base (id {id_devis}).")
            del st.session_state["devis_en_attente"]
    with col2:
        if st.button("❌ Abandonner"):
            del st.session_state["devis_en_attente"]
            st.info("Devis abandonné. Aucun fichier écrit.")