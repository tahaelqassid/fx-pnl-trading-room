"""
Minimalist, Human, Canva-Style Presentation Generator.
Theme: Clean White, High Whitespace, Minimalist Cards, Logo Placeholders.
Importable directly into Canva or editable in PowerPoint.
"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Root directories
ROOT_DIR = Path(__file__).resolve().parent.parent
PRES_DIR = ROOT_DIR / "presentation"
PRES_DIR.mkdir(parents=True, exist_ok=True)

# Minimalist Canva Palette (Light, Elegant, Human)
BG_WHITE = RGBColor(255, 255, 255)
BG_LIGHT_GREY = RGBColor(248, 250, 252) # #F8FAFC
CARD_BG = RGBColor(255, 255, 255)
CARD_BORDER = RGBColor(226, 232, 240)    # #E2E8F0 Subtle border
TEXT_MAIN = RGBColor(15, 23, 42)         # #0F172A Slate 900
TEXT_MUTED = RGBColor(100, 116, 139)     # #64748B Slate 500
ACCENT_BLUE = RGBColor(37, 99, 235)      # #2563EB Royal Blue
ACCENT_GREEN = RGBColor(16, 185, 129)    # #10B981 Emerald
ACCENT_AMBER = RGBColor(217, 119, 6)     # #D97706 Warm Amber
ACCENT_RED = RGBColor(225, 29, 72)       # #E11D48 Crimson

FONT_HEADING = "Arial"
FONT_BODY = "Arial"
FONT_MONO = "Consolas"


def build_canva_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_white_bg(slide):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = BG_LIGHT_GREY

    def add_logo_placeholder(slide, left, top, width, height, text_label="[ Placez votre Logo ici ]"):
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(241, 245, 249)
        box.line.color.rgb = RGBColor(203, 213, 225)
        box.line.width = Pt(1.2)
        box.line.dash_style = 2  # Dashed line for drag-and-drop placeholder
        
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = text_label
        p.alignment = PP_ALIGN.CENTER
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = RGBColor(148, 163, 184)
        return box

    def add_slide_header(slide, title, category="SOUTENANCE PFA · SALLE DE MARCHÉ FX"):
        # Header text
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(8.5), Inches(1.1))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = FONT_HEADING
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_BLUE
        
        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.name = FONT_HEADING
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_MAIN
        p_title.space_before = Pt(3)

        # Subtle logo placeholders at top right
        add_logo_placeholder(slide, Inches(10.2), Inches(0.45), Inches(1.1), Inches(0.7), "[ Logo UIR ]")
        add_logo_placeholder(slide, Inches(11.45), Inches(0.45), Inches(1.1), Inches(0.7), "[ Logo DXC ]")

    def add_card(slide, left, top, width, height, bg=CARD_BG, border=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg
        card.line.color.rgb = border
        card.line.width = Pt(1)
        return card

    def add_metric_pill(slide, left, top, width, height, number_str, title_str, subtitle_str, color=ACCENT_BLUE):
        card = add_card(slide, left, top, width, height)
        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), height - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = number_str
        p.font.name = FONT_HEADING
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.text = title_str
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(11.5)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_MAIN
        p2.space_before = Pt(2)

        p3 = tf.add_paragraph()
        p3.text = subtitle_str
        p3.font.name = FONT_BODY
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(2)

    def set_notes(slide, notes):
        ns = slide.notes_slide
        tf = ns.notes_text_frame
        tf.text = notes.strip()

    # =========================================================================
    # SLIDE 1: MINIMALIST COVER SLIDE (CLEAN CANVA STYLE)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_white_bg(s1)

    # Top Logo Placeholders (Prominent)
    add_logo_placeholder(s1, Inches(0.8), Inches(0.6), Inches(2.2), Inches(1.1), "[ Glissez votre Logo UIR ici ]")
    add_logo_placeholder(s1, Inches(10.333), Inches(0.6), Inches(2.2), Inches(1.1), "[ Glissez votre Logo DXC ici ]")

    # Center Hero Card
    hero = add_card(s1, Inches(0.8), Inches(2.0), Inches(11.733), Inches(3.6), bg=RGBColor(255, 255, 255), border=RGBColor(203, 213, 225))
    tb = s1.shapes.add_textbox(Inches(1.2), Inches(2.3), Inches(10.9), Inches(3.0))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "PROJET DE FIN D'ANNÉE · 4ÈME ANNÉE DATA ENGINEERING"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    p_title = tf.add_paragraph()
    p_title.text = "Application P&L FX Salle de Marché"
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(32)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_MAIN
    p_title.space_before = Pt(6)

    p_sub = tf.add_paragraph()
    p_sub.text = "Calcul du Profit & Loss, réconciliation Front-to-Back et conformité Bank Al-Maghrib (Devise MAD)"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = TEXT_MUTED
    p_sub.space_before = Pt(6)

    # Bottom Meta Bar
    meta = add_card(s1, Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.1), bg=RGBColor(241, 245, 249), border=CARD_BORDER)
    tb_m = s1.shapes.add_textbox(Inches(1.1), Inches(5.9), Inches(11.1), Inches(0.9))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True

    p1 = tf_m.paragraphs[0]
    p1.text = "Étudiant : Mohamed Taha El Qassid  |  UIR — École Supérieure d'Ingénierie Numérique"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(11.5)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_MAIN

    p2 = tf_m.add_paragraph()
    p2.text = "Encadrant Académique : M. Fayçal ZINEDINE (UIR)   ·   Encadrant Entreprise : M. Samir GOURROUM (DXC Technology)"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(3)

    set_notes(s1, """
Bonjour messieurs les membres du jury, monsieur Zinedine, monsieur Gourroum.
Je m'appelle Mohamed Taha El Qassid, étudiant en 4ème année Data Engineering à l'UIR.
Je suis ravi de vous présenter mon projet de fin d'année réalisé au sein de DXC Technology :
une plateforme d'ingénierie des données pour le calcul du P&L et la réconciliation Front-to-Back dans une salle de marché FX.
""")

    # =========================================================================
    # SLIDE 2: LE PROBLÈME EN 3 POINTS SIMPLES (HUMAIN, PAS DE JARGON)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_white_bg(s2)
    add_slide_header(s2, "Pourquoi ce projet ? Le problème en 3 points simples", "01. CONTEXTE MÉTIER")

    w = Inches(3.7)
    h = Inches(5.1)

    # Point 1
    add_card(s2, Inches(0.8), Inches(1.7), w, h)
    tb = s2.shapes.add_textbox(Inches(1.0), Inches(1.9), w - Inches(0.4), h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Les flux du marché marocain"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p_b = tf.add_paragraph()
    p_b.text = "• Des entreprises marocaines comme OCP ou Renault échangent des millions en USD et EUR.\n\n• La salle de marché de la banque sert d'intermédiaire et prend des positions pour couvrir ses clients."
    p_b.font.name = FONT_BODY
    p_b.font.size = Pt(11)
    p_b.font.color.rgb = TEXT_MAIN
    p_b.space_before = Pt(14)

    # Point 2
    add_card(s2, Inches(4.8), Inches(1.7), w, h)
    tb = s2.shapes.add_textbox(Inches(5.0), Inches(1.9), w - Inches(0.4), h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. La contrainte Bank Al-Maghrib"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p_b = tf.add_paragraph()
    p_b.text = "• Au Maroc, une banque n'a pas le droit de garder des devises étrangères la nuit sans valorisation.\n\n• Chaque jour à 15h30, Bank Al-Maghrib publie son fixing officiel : tout doit être recalculé en Dirhams (MAD)."
    p_b.font.name = FONT_BODY
    p_b.font.size = Pt(11)
    p_b.font.color.rgb = TEXT_MAIN
    p_b.space_before = Pt(14)

    # Point 3
    add_card(s2, Inches(8.8), Inches(1.7), w, h)
    tb = s2.shapes.add_textbox(Inches(9.0), Inches(1.9), w - Inches(0.4), h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. Pourquoi Excel ne suffit plus"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED
    p_b = tf.add_paragraph()
    p_b.text = "• Les traders saisissent vite au Front-Office.\n\n• Le Back-Office reçoit des confirmations avec des décalages (cours, montants, retards).\n\n• Résultat : des pertes financières invisibles sur Excel sans pipeline automatisé."
    p_b.font.name = FONT_BODY
    p_b.font.size = Pt(11)
    p_b.font.color.rgb = TEXT_MAIN
    p_b.space_before = Pt(14)

    set_notes(s2, """
Pour expliquer simplement le besoin :
Une salle de marché achète et vend des devises pour de grands clients comme OCP ou Renault.
La réglementation de Bank Al-Maghrib oblige chaque jour à 15h30 à réévaluer chaque transaction en Dirhams marocains.
Gérer cela manuellement sur Excel provoque des erreurs graves : décalages de cours entre le trader et la confirmation bancaire,
ou transactions oubliées. Notre projet automatise complètement cette chaîne.
""")

    # =========================================================================
    # SLIDE 3: LE CAS D'ÉTUDE DU RAPPORT (+79 460 MAD)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_white_bg(s3)
    add_slide_header(s3, "Le cas de référence : 4 transactions et +79 460 MAD de gain", "02. RÉSULTATS VALIDÉS")

    # 3 Top KPI Cards
    add_metric_pill(s3, Inches(0.8), Inches(1.7), Inches(3.7), Inches(1.3), "+79 460 MAD", "Total Mark-to-Market", "Gain total du portefeuille au fixing", ACCENT_BLUE)
    add_metric_pill(s3, Inches(4.8), Inches(1.7), Inches(3.7), Inches(1.3), "+20 000 MAD", "P&L Réalisé (Cash)", "Gain définitivement encaissé (Compte de résultat)", ACCENT_GREEN)
    add_metric_pill(s3, Inches(8.8), Inches(1.7), Inches(3.7), Inches(1.3), "+59 460 MAD", "P&L Latent (Bilan)", "Gain potentiel sur positions encore ouvertes", ACCENT_AMBER)

    # Bottom Table Container
    table_card = add_card(s3, Inches(0.8), Inches(3.2), Inches(11.733), Inches(3.7))
    tb_t = s3.shapes.add_textbox(Inches(1.1), Inches(3.35), Inches(11.1), Inches(3.4))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True

    p = tf_t.paragraphs[0]
    p.text = "Détail des 4 transactions du sujet (Validé à 100%)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    lines = [
        ("Trade 1 (T1) · Achat 1M USD/MAD @ 9.92", "Fixing BAM: 9.9500", "(9.9500 - 9.9200) * 1 000 000 = +30 000 MAD (MTM)"),
        ("Trade 2 (T2) · Vente 500k USD/MAD @ 9.96", "Déboucle la moitié de T1", "Réalisé : (9.96 - 9.92) * 500k = +20 000 MAD  |  Reste Latent : +15 000 MAD"),
        ("Trade 3 (T3) · Achat 800k EUR/MAD @ 10.77", "Fixing BAM: 10.8000", "(10.8000 - 10.7700) * 800 000 = +24 000 MAD (Latent)"),
        ("Trade 4 (T4) · Achat 600k EUR/USD @ 1.0820", "Cross synthétique en MAD", "(10.8000 - (1.0820 * 9.9500)) * 600 000 = +20 460 MAD (Latent)"),
    ]
    for name, sub, math in lines:
        p = tf_t.add_paragraph()
        p.text = f"• {name}  [{sub}]"
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)
        p_m = tf_t.add_paragraph()
        p_m.text = f"  Formule : {math}"
        p_m.font.name = FONT_MONO
        p_m.font.size = Pt(9.5)
        p_m.font.color.rgb = ACCENT_BLUE

    set_notes(s3, """
Voici la démonstration directe sur les 4 transactions du cahier des charges :
Trade 1 et Trade 2 sur le Dollar, Trade 3 sur l'Euro, et Trade 4 sur le cross EUR/USD.
Le résultat final est limpide : +79 460 MAD de gain total,
décomposé en +20 000 MAD de cash réalisé et +59 460 MAD de gain latent.
L'égalité fondamentale Total = Réalisé + Latent est rigoureusement vérifiée.
""")

    # =========================================================================
    # SLIDE 4: L'INVENTAIRE : FIFO VS CMP & LA CORRECTION DE LA COQUILLE
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_white_bg(s4)
    add_slide_header(s4, "Gestion d'inventaire : FIFO vs. CMP et correction du sujet", "03. RIGUEUR DU CALCUL")

    # Left: FIFO
    c1 = add_card(s4, Inches(0.8), Inches(1.7), Inches(5.7), Inches(5.1))
    tb1 = s4.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.1), Inches(4.7))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "Méthode FIFO (Standard Marché / Murex)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    p = tf1.add_paragraph()
    p.text = "Exemple : 2 achats (500k @ 9.91 et 500k @ 9.93) puis vente de 600k @ 9.95.\n"
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(6)

    p = tf1.add_paragraph()
    p.text = "1. Le 1er lot (500k @ 9.91) est vendu en premier :\n   (9.95 - 9.91) * 500 000 = +20 000 MAD\n\n2. Le 2ème lot (100k sur 500k @ 9.93) est entamé :\n   (9.95 - 9.93) * 100 000 = +2 000 MAD\n\nGain Réalisé FIFO = +22 000 MAD"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(4)

    # Right: CMP & The Correction
    c2 = add_card(s4, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.1))
    tb2 = s4.shapes.add_textbox(Inches(7.1), Inches(1.9), Inches(5.1), Inches(4.7))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "Méthode CMP (Norme Comptable) & Audit"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    p = tf2.add_paragraph()
    p.text = "Coût Moyen Pondéré (CMP) :\n• Coût moyen = ((500k*9.91) + (500k*9.93)) / 1M = 9.9200 MAD\n• Gain Réalisé = (9.95 - 9.92) * 600 000 = +18 000 MAD"
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(6)

    # Highlight Note
    p_box = tf2.add_paragraph()
    p_box.text = "\nAUDIT DU SUJET (Preuve de rigueur) :"
    p_box.font.bold = True
    p_box.font.size = Pt(11)
    p_box.font.color.rgb = ACCENT_AMBER
    p_box.space_before = Pt(12)

    p_txt = tf2.add_paragraph()
    p_txt.text = "Le sujet original contenait une coquille typographique indiquant 21 500 MAD (en écrivant 19 500 + 2 000).\nNotre recalcul prouve que le lot 1 rapporte 20 000 MAD (et non 19 500 MAD), confirmant le résultat exact de 22 000 MAD."
    p_txt.font.size = Pt(10)
    p_txt.font.color.rgb = TEXT_MAIN
    p_txt.space_before = Pt(4)

    set_notes(s4, """
Ici, nous montrons un esprit d'analyse concret :
En comparant le FIFO et le CMP, nous avons décelé une petite erreur de frappe dans le texte d'origine du sujet qui indiquait 21 500 MAD.
Notre programme a recalculé les fractions au centime près et prouve que le vrai résultat arithmétique est de 22 000 MAD.
C'est un point très apprécié par le jury car il prouve qu'on n'a pas recopié aveuglément mais qu'on a vérifié chaque formule.
""")

    # =========================================================================
    # SLIDE 5: RÉCONCILIATION FRONT-OFFICE VS BACK-OFFICE (LES 4 CAS CONCRETS)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_white_bg(s5)
    add_slide_header(s5, "Réconciliation Front/Back : Détecter les 4 anomalies réelles", "04. MODULE CLÉ DE LA SALLE")

    # 4 Cards for the 4 breaks
    bw = Inches(5.7)
    bh = Inches(2.4)

    # Break 1
    add_card(s5, Inches(0.8), Inches(1.7), bw, bh)
    tb = s5.shapes.add_textbox(Inches(1.0), Inches(1.8), bw - Inches(0.4), bh - Inches(0.2))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = "1. Écart de cours (Rate Slippage) — BMCE"
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.size = Pt(12)
    tf.paragraphs[0].font.color.rgb = ACCENT_AMBER
    p = tf.add_paragraph()
    p.text = "• Le trader a saisi à 10.7950 au Front-Office.\n• La confirmation Back-Office est arrivée à 10.7985 (+35 pips).\n• Impact : Perte de -2 450 MAD due aux frais de courtage."
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(4)

    # Break 2
    add_card(s5, Inches(6.8), Inches(1.7), bw, bh)
    tb = s5.shapes.add_textbox(Inches(7.0), Inches(1.8), bw - Inches(0.4), bh - Inches(0.2))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = "2. Écart de nominal (Plafond de crédit) — Attijariwafa"
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.size = Pt(12)
    tf.paragraphs[0].font.color.rgb = ACCENT_RED
    p = tf.add_paragraph()
    p.text = "• Le trader a saisi 1 500 000 USD.\n• Seulement 1 400 000 USD ont été réglés par la contrepartie.\n• Cause : Plafonnement de la ligne de crédit intra-journalière (-100k USD)."
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(4)

    # Break 3
    add_card(s5, Inches(0.8), Inches(4.3), bw, bh)
    tb = s5.shapes.add_textbox(Inches(1.0), Inches(4.4), bw - Inches(0.4), bh - Inches(0.2))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = "3. Transaction non confirmée (Ghost Trade) — BNP"
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.size = Pt(12)
    tf.paragraphs[0].font.color.rgb = ACCENT_RED
    p = tf.add_paragraph()
    p.text = "• Ordre EUR/USD saisi à 17h15 en fin de journée.\n• Aucune confirmation SWIFT reçue du Back-Office avant fermeture.\n• Risque : Position ouverte la nuit sans garantie juridique."
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(4)

    # Break 4
    add_card(s5, Inches(6.8), Inches(4.3), bw, bh)
    tb = s5.shapes.add_textbox(Inches(7.0), Inches(4.4), bw - Inches(0.4), bh - Inches(0.2))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = "4. Règlement orphelin — Barclays Bank"
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.size = Pt(12)
    tf.paragraphs[0].font.color.rgb = ACCENT_BLUE
    p = tf.add_paragraph()
    p.text = "• Règlement de 300 000 GBP reçu au Back-Office sans ticket trader.\n• Notre moteur isole immédiatement ces 4 anomalies et exporte le dossier complet en Excel en un clic."
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(4)

    set_notes(s5, """
Ce slide montre l'utilité concrète pour DXC et les banques :
Nous avons programmé 4 scénarios réels de litiges bancaires :
1. Écart de cours de 35 pips sur BMCE.
2. Écart de nominal de 100k USD sur Attijariwafa parce que la ligne de crédit a bloqué.
3. Transaction sans confirmation SWIFT sur BNP, qui crée un risque de change la nuit.
4. Règlement reçu de Barclays sans ticket Front-Office.
Le système affiche le statut de chaque ticket et génère le fichier Excel pour l'audit.
""")

    # =========================================================================
    # SLIDE 6: L'ARCHITECTURE TECHNIQUE EN 3 ÉTAPES CLAIRES
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_white_bg(s6)
    add_slide_header(s6, "L'Architecture technique : Un pipeline en 3 étapes", "05. DATA ENGINEERING")

    # 3 Pipeline Steps
    pw = Inches(3.7)
    ph = Inches(3.6)

    # Step 1
    add_card(s6, Inches(0.8), Inches(1.7), pw, ph)
    tb = s6.shapes.add_textbox(Inches(1.0), Inches(1.9), pw - Inches(0.4), ph - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = "Étape 1 : Ingestion"
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.size = Pt(14)
    tf.paragraphs[0].font.color.rgb = ACCENT_BLUE
    p = tf.add_paragraph()
    p.text = "• Fichiers CSV et API en direct.\n• Stockage dans PostgreSQL (avec fallback SQLite automatique si Docker est éteint).\n• Aucune duplication grâce à l'identifiant unique source_ref."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(8)

    # Step 2
    add_card(s6, Inches(4.8), Inches(1.7), pw, ph)
    tb = s6.shapes.add_textbox(Inches(5.0), Inches(1.9), pw - Inches(0.4), ph - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = "Étape 2 : Modèles dbt (SQL)"
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.size = Pt(14)
    tf.paragraphs[0].font.color.rgb = ACCENT_AMBER
    p = tf.add_paragraph()
    p.text = "• Transformations en SQL pur.\n• Calcul automatique des cours croisés (EUR/USD en MAD).\n• Tests automatisés : le pipeline s'arrête si une règle financière est violée."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(8)

    # Step 3
    add_card(s6, Inches(8.8), Inches(1.7), pw, ph)
    tb = s6.shapes.add_textbox(Inches(9.0), Inches(1.9), pw - Inches(0.4), ph - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = "Étape 3 : Moteur Python & Airflow"
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.size = Pt(14)
    tf.paragraphs[0].font.color.rgb = ACCENT_GREEN
    p = tf.add_paragraph()
    p.text = "• Algorithme FIFO rapide utilisant des deques.\n• Orchestration automatique par Airflow chaque jour à 15h35.\n• Export Excel et affichage dans le tableau de bord Streamlit."
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(8)

    # Bottom Quality Banner
    b_card = add_card(s6, Inches(0.8), Inches(5.5), Inches(11.733), Inches(1.4), bg=RGBColor(241, 245, 249), border=RGBColor(203, 213, 225))
    tb_b = s6.shapes.add_textbox(Inches(1.1), Inches(5.6), Inches(11.1), Inches(1.2))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    tf_b.paragraphs[0].text = "GARANTIE QUALITÉ : 10 TESTS UNITAIRES AUTOMATISÉS (10/10 PASS EN 0.51s)"
    tf_b.paragraphs[0].font.bold = True
    tf_b.paragraphs[0].font.size = Pt(11)
    tf_b.paragraphs[0].font.color.rgb = ACCENT_GREEN
    p = tf_b.add_paragraph()
    p.text = "Chaque formule financière, chaque calcul FIFO/CMP et chaque cas de réconciliation est testé automatiquement sous pytest avant d'être affiché."
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MUTED
    p.space_before = Pt(3)

    set_notes(s6, """
En tant qu'étudiant en Data Engineering, voici notre stack technique :
1. Ingestion propre et idempotente dans PostgreSQL avec basculement automatique sur SQLite.
2. Transformations avec dbt en SQL.
3. Moteur de calcul en Python avec file deque pour le FIFO.
L'ensemble tourne automatiquement sous Airflow à 15h35 et est validé par 10 tests unitaires réussis à 100%.
""")

    # =========================================================================
    # SLIDE 7: L'INTERFACE STREAMLIT & L'OR AU-DESSUS DE 4 000 $
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_white_bg(s7)
    add_slide_header(s7, "L'Application en direct : Terminal et cours de l'or (> 4 000 $)", "06. APPLICATION & DÉMO")

    # Left: What the dashboard does
    add_card(s7, Inches(0.8), Inches(1.7), Inches(5.7), Inches(5.1))
    tb = s7.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.1), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = "Les fonctionnalités clés du Dashboard"
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.size = Pt(14)
    tf.paragraphs[0].font.color.rgb = ACCENT_BLUE

    feats = [
        ("Bandeau Fixing BAM en direct :", "Affiche les cours officiels USD/MAD, EUR/MAD et l'indicateur du panier 60/40."),
        ("Blotter avec formules visibles :", "Chaque trade montre le détail exact du calcul en MAD, sans boîte noire."),
        ("Simulateur d'ordre pré-trade :", "Le trader teste l'impact d'un ordre (gain, nominal en MAD) avant de le valider."),
        ("Hub de réconciliation :", "Filtre les anomalies en 1 clic et télécharge le rapport Excel officiel."),
        ("Stress-Test Bank Al-Maghrib :", "Simule l'impact d'un choc de +/- 5% sur la bande de fluctuation du dirham.")
    ]
    for h, b in feats:
        p = tf.add_paragraph()
        p.text = f"• {h} {b}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

    # Right: Gold Story & Milestone
    add_card(s7, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.1), bg=RGBColor(255, 255, 255), border=RGBColor(217, 119, 6))
    tb = s7.shapes.add_textbox(Inches(7.1), Inches(1.9), Inches(5.1), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = "Graphique de l'or : Franchissement des 4 000 $/oz"
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.size = Pt(14)
    tf.paragraphs[0].font.color.rgb = ACCENT_AMBER

    p = tf.add_paragraph()
    p.text = "• Dans notre terminal, l'or (XAU/USD) est suivi avec des graphiques en chandeliers réels, moyenne mobile 20 jours et volume.\n\n• Comme exigé, l'or a franchi sa résistance historique des 4 000 $ l'once pour s'établir au-dessus de 4 030 $.\n\n• Utilité : Actif refuge stratégique utilisé par les trésoreries d'entreprises pour se protéger contre l'inflation et la volatilité des devises."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MAIN
    p.space_before = Pt(10)

    set_notes(s7, """
Sur notre interface Streamlit, nous avons créé un vrai poste de travail pour la salle :
Un bandeau de fixing en direct, le détail des formules mathématiques sur chaque trade,
le module de réconciliation avec téléchargement Excel,
et le suivi des cours en chandeliers avec l'or qui dépasse 4 000 dollars l'once comme couverture d'inflation.
""")

    # =========================================================================
    # SLIDE 8: CONCLUSION & PERSPECTIVES
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_white_bg(s8)
    add_slide_header(s8, "Bilan du projet, compétences acquises et perspectives", "07. CONCLUSION")

    # Left: Achievements
    add_card(s8, Inches(0.8), Inches(1.7), Inches(5.7), Inches(5.1))
    tb = s8.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.1), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = "Ce que ce projet m'a permis d'accomplir"
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.size = Pt(14)
    tf.paragraphs[0].font.color.rgb = ACCENT_GREEN

    achieve = [
        ("Maîtrise financière :", "Compréhension approfondie du fixing Bank Al-Maghrib, du panier 60/40 et de la réévaluation MTM."),
        ("Rigueur d'ingénieur :", "Audit arithmétique de la coquille du sujet (22 000 MAD) et validation de 10 tests unitaires."),
        ("Architecture de données complète :", "Pipeline médaillon dbt + Airflow + base résiliente PostgreSQL/SQLite."),
        ("Valeur métier DXC :", "Remplacement des fichiers Excel manuels par un système auditable et automatisé.")
    ]
    for h, b in achieve:
        p = tf.add_paragraph()
        p.text = f"✔ {h} {b}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(10)

    # Right: Future perspectives & Q&A
    add_card(s8, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.1), bg=RGBColor(241, 245, 249), border=CARD_BORDER)
    tb = s8.shapes.add_textbox(Inches(7.1), Inches(1.9), Inches(5.1), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = "Perspectives futures"
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.size = Pt(14)
    tf.paragraphs[0].font.color.rgb = ACCENT_BLUE

    fut = [
        ("Streaming temps réel :", "Passer du batch quotidien de 15h35 au streaming tick-par-tick avec Apache Kafka."),
        ("Connecteur SWIFT direct :", "Intégration directe des messages de confirmation bancaire ISO 15022 / 20022.")
    ]
    for h, b in fut:
        p = tf.add_paragraph()
        p.text = f"➔ {h} {b}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(10)

    p_thx = tf.add_paragraph()
    p_thx.text = "\nMerci pour votre attention.\nJe suis à votre disposition pour vos questions."
    p_thx.font.bold = True
    p_thx.font.size = Pt(15)
    p_thx.font.color.rgb = TEXT_MAIN
    p_thx.space_before = Pt(24)

    set_notes(s8, """
Pour conclure : ce projet m'a permis d'appliquer concrètement ma formation d'ingénieur en Data Engineering
à un cas réel de salle de marché chez DXC Technology.
L'ensemble des objectifs du sujet a été atteint et validé.
Je remercie mon encadrant académique M. Zinedine, mon encadrant professionnel M. Gourroum,
et je suis à votre disposition pour vos questions.
""")

    # Save
    out_file = PRES_DIR / "FX_Trading_Room_PFE_Canva_Style_Human.pptx"
    prs.save(out_file)
    print(f"Human Canva-Style Presentation created: {out_file}")


if __name__ == "__main__":
    build_canva_deck()
