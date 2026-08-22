from fpdf import FPDF
import os

def generer_pdf(data):

    # --- Palette ---
    BLEU_FONCE  = (15, 52, 96)
    BLEU_CLAIR  = (41, 128, 185)
    ORANGE      = (230, 126, 34)
    GRIS_FOND   = (245, 247, 250)
    GRIS_TEXTE  = (100, 110, 120)
    BLANC       = (255, 255, 255)
    NOIR        = (30, 30, 30)


    class DevisPDF(FPDF):
        def header(self):
            pass

        def footer(self):
            self.set_y(-12)
            self.set_font("DejaVu", "", 7)
            self.set_text_color(*GRIS_TEXTE)
            self.cell(0, 5, f"Page {self.page_no()} — {data.get('reference', '')} — {data.get('entreprise', '')}", align="C")


    pdf = DevisPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_font("DejaVu", "",  "config/DejaVuSans.ttf")
    pdf.add_font("DejaVu", "B", "config/DejaVuSans.ttf")


    # ============================================================
    # EN-TETE : bande bleue gauche + bloc DEVIS droit
    # ============================================================

    # Bande colorée à gauche (fond pour infos entreprise)
    pdf.set_fill_color(*BLEU_FONCE)
    pdf.rect(0, 0, 75, 68, "F")

    # Nom entreprise
    pdf.set_xy(5, 8)
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(*BLANC)
    pdf.cell(65, 8, data["entreprise"].upper(), new_x="LMARGIN", new_y="NEXT")

    # Forme juridique
    pdf.set_xy(5, pdf.get_y())
    pdf.set_font("DejaVu", "", 8)
    pdf.set_text_color(180, 210, 240)
    pdf.cell(65, 5, data.get("forme_juridique", ""), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Coordonnées entreprise
    pdf.set_font("DejaVu", "", 7.5)
    pdf.set_text_color(*BLANC)
    infos_entreprise = [
        data.get("adresse_entreprise", ""),
        data.get("telephone", ""),
        data.get("email", ""),
        "SIRET : " + data.get("siret", ""),
        "RCS : "   + data.get("rcs", ""),
        "APE : "   + data.get("code_ape", ""),
        "TVA : "   + data.get("tva_intra", ""),
        "Ass. : "  + data.get("assurance_decennale", ""),
    ]
    for info in infos_entreprise:
        if info.strip() and info.strip() not in ("SIRET : ", "RCS : ", "APE : ", "TVA : ", "Ass. : "):
            pdf.set_xy(5, pdf.get_y())
            pdf.cell(65, 4.5, info, new_x="LMARGIN", new_y="NEXT")

    # Bloc DEVIS à droite
    pdf.set_fill_color(*BLEU_CLAIR)
    pdf.rect(80, 5, 115, 28, "F")

    pdf.set_xy(82, 8)
    pdf.set_font("DejaVu", "B", 26)
    pdf.set_text_color(*BLANC)
    pdf.cell(109, 14, "DEVIS", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_xy(82, 22)
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(*BLANC)
    pdf.cell(109, 6, data.get("reference", ""), align="C", new_x="LMARGIN", new_y="NEXT")

    # Infos devis à droite (sous le bloc bleu)
    pdf.set_xy(82, 36)
    pdf.set_font("DejaVu", "", 8.5)
    pdf.set_text_color(*NOIR)

    details_devis = [
        ("Date",           data.get("date", "")),
        ("Validité",       data.get("validite", "")),
        ("Début travaux",  data.get("date_debut_travaux", "")),
        ("Fin travaux",    data.get("date_fin_travaux", "")),
    ]
    for label, valeur in details_devis:
        if valeur:
            pdf.set_xy(82, pdf.get_y())
            pdf.set_font("DejaVu", "B", 8.5)
            pdf.set_text_color(*BLEU_FONCE)
            pdf.cell(35, 5, label + " :", new_x="RIGHT", new_y="TOP")
            pdf.set_font("DejaVu", "", 8.5)
            pdf.set_text_color(*NOIR)
            pdf.cell(78, 5, valeur, new_x="LMARGIN", new_y="NEXT")

    # Ligne séparatrice épaisse
    pdf.set_y(70)
    pdf.set_draw_color(*BLEU_FONCE)
    pdf.set_line_width(1.2)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)


    # ============================================================
    # BLOC CLIENT
    # ============================================================
    y_client = pdf.get_y()
    pdf.set_fill_color(*GRIS_FOND)
    pdf.rect(15, y_client, 85, 32, "F")
    pdf.set_draw_color(*BLEU_CLAIR)
    pdf.set_line_width(0.3)
    pdf.rect(15, y_client, 85, 32)

    pdf.set_xy(18, y_client + 3)
    pdf.set_font("DejaVu", "B", 9)
    pdf.set_text_color(*BLEU_FONCE)
    pdf.cell(79, 5, "CLIENT / DESTINATAIRE", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("DejaVu", "B", 9)
    pdf.set_text_color(*NOIR)
    pdf.set_xy(18, pdf.get_y())
    pdf.cell(79, 5, data.get("client", ""), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("DejaVu", "", 8.5)
    pdf.set_text_color(*GRIS_TEXTE)
    for ligne_client in [
        data.get("adresse_client", ""),
        data.get("telephone_client", ""),
        data.get("email_client", ""),
    ]:
        if ligne_client:
            pdf.set_xy(18, pdf.get_y())
            pdf.cell(79, 4.5, ligne_client, new_x="LMARGIN", new_y="NEXT")

    chantier = data.get("adresse_chantier", "")
    if chantier and "identique" not in chantier.lower():
        pdf.set_xy(18, pdf.get_y())
        pdf.set_font("DejaVu", "B", 8)
        pdf.set_text_color(*BLEU_CLAIR)
        pdf.cell(79, 4.5, "Chantier : " + chantier, new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(y_client + 36)
    pdf.ln(4)


    # ============================================================
    # TABLEAU DES PRESTATIONS
    # ============================================================
    pdf.set_font("DejaVu", "B", 9)
    pdf.set_text_color(*BLEU_FONCE)
    pdf.cell(0, 6, "DETAIL DES PRESTATIONS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*BLEU_FONCE)
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)

    # Header tableau
    pdf.set_fill_color(*BLEU_CLAIR)
    pdf.set_text_color(*BLANC)
    pdf.set_font("DejaVu", "B", 8.5)
    pdf.set_line_width(0)
    pdf.cell(85, 8, "Designation", border=0, fill=True)
    pdf.cell(18, 8, "Qte",    border=0, fill=True, align="C")
    pdf.cell(15, 8, "Unite",  border=0, fill=True, align="C")
    pdf.cell(30, 8, "Prix HT",border=0, fill=True, align="R")
    pdf.cell(32, 8, "Total HT",border=0,fill=True, align="R", new_x="LMARGIN", new_y="NEXT")

    # Lignes alternées
    pdf.set_text_color(*NOIR)
    pdf.set_font("DejaVu", "", 8)
    ligne_pair = False
    for ligne in data["lignes"]:
        designation = str(ligne.get("designation", ""))
        quantite    = ligne.get("quantite", 0)
        unite       = str(ligne.get("unite", ""))
        prix_ht     = float(ligne.get("prix_ht", 0))
        total_ht    = float(ligne.get("total_ht", 0))

        x = pdf.get_x()
        y = pdf.get_y()

        # Fond alterné
        nb_lignes_text = len(designation) // 43 + 1
        hauteur_estimee = max(7, nb_lignes_text * 4.5)
        if ligne_pair:
            pdf.set_fill_color(*GRIS_FOND)
            pdf.rect(15, y, 180, hauteur_estimee + 1, "F")
        ligne_pair = not ligne_pair

        pdf.set_xy(15, y)
        pdf.multi_cell(85, 4.5, designation, border=0)
        new_y = pdf.get_y()
        hauteur_reelle = new_y - y

        pdf.set_xy(100, y)
        pdf.cell(18, hauteur_reelle, str(quantite), border=0, align="C")
        pdf.cell(15, hauteur_reelle, unite,          border=0, align="C")
        pdf.cell(30, hauteur_reelle, f"{prix_ht:.2f} EUR", border=0, align="R")
        pdf.cell(32, hauteur_reelle, f"{total_ht:.2f} EUR", border=0, align="R", new_x="LMARGIN", new_y="NEXT")

        # Ligne séparatrice légère entre chaque prestation
        pdf.set_draw_color(220, 225, 230)
        pdf.set_line_width(0.2)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())

    pdf.ln(5)


    # ============================================================
    # TOTAUX
    # ============================================================
    total_ht    = float(data.get("total_ht", 0))
    tva_pct     = data.get("tva_pct", 10)
    tva_montant = float(data.get("tva_montant", 0))
    total_ttc   = float(data.get("total_ttc", 0))
    tva_article = data.get("tva_article", "")

    pdf.set_draw_color(*BLEU_CLAIR)
    pdf.set_line_width(0.3)

    # Total HT
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(*NOIR)
    pdf.cell(125, 6, "")
    pdf.cell(38, 6, "Total HT :", align="R")
    pdf.cell(32, 6, f"{total_ht:.2f} EUR", align="R", new_x="LMARGIN", new_y="NEXT")

    # TVA
    pdf.cell(125, 6, "")
    pdf.cell(38, 6, f"TVA {tva_pct}% :", align="R")
    pdf.cell(32, 6, f"{tva_montant:.2f} EUR", align="R", new_x="LMARGIN", new_y="NEXT")

    if tva_article:
        pdf.set_font("DejaVu", "", 7)
        pdf.set_text_color(*GRIS_TEXTE)
        pdf.set_x(15)
        pdf.cell(0, 4, tva_article, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "", 9)

    pdf.ln(1)
    pdf.set_draw_color(*ORANGE)
    pdf.set_line_width(0.8)
    pdf.line(125, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(2)

    # Total TTC
    pdf.set_fill_color(*ORANGE)
    pdf.rect(125, pdf.get_y(), 70, 10, "F")
    pdf.set_font("DejaVu", "B", 11)
    pdf.set_text_color(*BLANC)
    pdf.cell(125, 10, "")
    pdf.cell(38, 10, "TOTAL TTC :", align="R")
    pdf.cell(32, 10, f"{total_ttc:.2f} EUR", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)


    # ============================================================
    # CONDITIONS DE REGLEMENT
    # ============================================================
    def section_titre(pdf, titre):
        pdf.set_font("DejaVu", "B", 9)
        pdf.set_text_color(*BLEU_FONCE)
        pdf.cell(0, 6, titre, new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(*BLEU_CLAIR)
        pdf.set_line_width(0.4)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(3)

    def ligne_info(pdf, label, valeur):
        if not valeur:
            return
        pdf.set_font("DejaVu", "B", 8.5)
        pdf.set_text_color(*BLEU_FONCE)
        pdf.cell(45, 5, label + " :", new_x="RIGHT", new_y="TOP")
        pdf.set_font("DejaVu", "", 8.5)
        pdf.set_text_color(*NOIR)
        pdf.cell(135, 5, valeur, new_x="LMARGIN", new_y="NEXT")

    section_titre(pdf, "CONDITIONS DE REGLEMENT")
    ligne_info(pdf, "Acompte",  data.get("acompte", ""))
    ligne_info(pdf, "Solde",    data.get("solde", ""))
    ligne_info(pdf, "Delai",    data.get("delai", ""))
    ligne_info(pdf, "Paiement", data.get("paiement", ""))
    if data.get("iban"):
        ligne_info(pdf, "IBAN", data.get("iban", ""))
    if data.get("bic"):
        ligne_info(pdf, "BIC",  data.get("bic", ""))
    pdf.ln(6)


    # ============================================================
    # GARANTIES LEGALES
    # ============================================================
    garanties = data.get("garanties", {})
    if garanties:
        section_titre(pdf, "GARANTIES LEGALES")
        pdf.set_font("DejaVu", "", 8.5)
        pdf.set_text_color(*NOIR)
        for texte in garanties.values():
            pdf.set_x(15)
            pdf.cell(5, 5, "-")
            pdf.multi_cell(170, 5, texte)
        pdf.ln(4)


    # ============================================================
    # MENTIONS LEGALES
    # ============================================================
    section_titre(pdf, "INFORMATIONS ET MENTIONS LEGALES")
    pdf.set_font("DejaVu", "", 7.5)
    pdf.set_text_color(*GRIS_TEXTE)

    mentions = [
        data.get("retractation", ""),
        data.get("penalites_retard", ""),
        data.get("mediateur", ""),
        data.get("rgpd", ""),
        data.get("mentions_legales", ""),
    ]
    for mention in mentions:
        if mention:
            pdf.set_x(15)
            pdf.multi_cell(180, 4.5, "• " + mention)
            pdf.ln(1)
    pdf.ln(5)


    # ============================================================
    # ZONE SIGNATURE
    # ============================================================
    pdf.set_font("DejaVu", "B", 8.5)
    pdf.set_text_color(*NOIR)
    pdf.multi_cell(180, 5, data.get("mention", ""))
    pdf.ln(4)

    pdf.set_fill_color(*GRIS_FOND)
    pdf.set_draw_color(*BLEU_CLAIR)
    pdf.set_line_width(0.3)

    pdf.cell(87, 28, "", border=1, fill=True)
    pdf.cell(3, 28, "")
    pdf.cell(87, 28, "", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

    y_sig = pdf.get_y() - 26
    pdf.set_xy(18, y_sig)
    pdf.set_font("DejaVu", "B", 8)
    pdf.set_text_color(*BLEU_FONCE)
    pdf.cell(75, 5, "Signature et date du client :")
    pdf.set_xy(108, y_sig)
    pdf.cell(75, 5, "Cachet et signature de l'entreprise :")


# ============================================================
    # GENERATION
    # ============================================================
    nom_base = f"outputs/devis/devis_{data.get('client', 'client')}"
    fichier_sortie = nom_base + ".pdf"
    pdf.output(fichier_sortie)
    print("PDF généré : " + fichier_sortie)
    return fichier_sortie
