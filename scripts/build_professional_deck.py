"""
Executive Institutional PowerPoint Presentation Generator for PFE Defense.
Candidate: Mohamed Taha El Qassid (Data Engineering, 4th Year, UIR).
Host Company: DXC Technology.
Academic Supervisor: Fayçal ZINEDINE (UIR) | Company Supervisor: Samir GOURROUM (DXC).
Topic: FX P&L Trading Room Application (Accounting Currency: MAD).
"""
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Root directories
ROOT_DIR = Path(__file__).resolve().parent.parent
PRES_DIR = ROOT_DIR / "presentation"
ASSETS_DIR = PRES_DIR / "assets"

# Clean Logo Paths
UIR_LOGO_PATH = ASSETS_DIR / "uir_logo_clean.png"
DXC_LOGO_PATH = ASSETS_DIR / "dxc_logo_clean.png"

# Institutional Palette (Executive Dark / McKinsey & DXC Consulting Style)
C_DARK_BG = RGBColor(9, 13, 22)        # #090D16 Pure Deep Navy
C_CARD_BG = RGBColor(17, 24, 39)       # #111827 Slate 900
C_CARD_BORDER = RGBColor(30, 41, 59)   # #1E293B Slate 800
C_HEADER_BAR = RGBColor(15, 23, 42)    # #0F172A
C_ACCENT_BLUE = RGBColor(14, 165, 233) # #0EA5E9 Sky Blue
C_EMERALD = RGBColor(16, 185, 129)     # #10B981 Emerald Green
C_GOLD = RGBColor(245, 158, 11)        # #F59E0B Amber Gold
C_ROSE = RGBColor(244, 63, 94)         # #F43F5E Rose Red
C_TEXT_WHITE = RGBColor(248, 250, 252) # #F8FAFC
C_TEXT_MUTED = RGBColor(148, 163, 184) # #94A3B8
C_TEXT_DIM = RGBColor(100, 116, 139)   # #64748B

FONT_HEADING = "Segoe UI"
FONT_BODY = "Segoe UI"
FONT_MONO = "Consolas"


def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_bg(slide):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = C_DARK_BG

    def add_top_bar(slide, title, category="PFA DEFENSE · DATA ENGINEERING · DXC & UIR"):
        # Header text
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8.5), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = FONT_HEADING
        p_cat.font.size = Pt(9.5)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_ACCENT_BLUE
        
        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.name = FONT_HEADING
        p_title.font.size = Pt(21)
        p_title.font.bold = True
        p_title.font.color.rgb = C_TEXT_WHITE
        p_title.space_before = Pt(2)

        # Right Header Logos (Clean Dual Badges)
        if UIR_LOGO_PATH.exists() and DXC_LOGO_PATH.exists():
            # DXC Logo Badge
            dxc_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.3), Inches(0.38), Inches(1.2), Inches(0.55))
            dxc_box.fill.solid()
            dxc_box.fill.fore_color.rgb = RGBColor(255, 255, 255)
            dxc_box.line.color.rgb = RGBColor(203, 213, 225)
            dxc_box.line.width = Pt(1)
            slide.shapes.add_picture(str(DXC_LOGO_PATH), Inches(11.35), Inches(0.44), width=Inches(1.1))

            # UIR Logo Badge
            uir_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.55), Inches(0.38), Inches(0.65), Inches(0.55))
            uir_box.fill.solid()
            uir_box.fill.fore_color.rgb = RGBColor(7, 53, 103)
            uir_box.line.color.rgb = RGBColor(14, 165, 233)
            uir_box.line.width = Pt(1)
            slide.shapes.add_picture(str(UIR_LOGO_PATH), Inches(10.60), Inches(0.40), width=Inches(0.55))

    def add_card(slide, left, top, width, height, bg_rgb=C_CARD_BG, border_rgb=C_CARD_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_rgb
        shape.line.color.rgb = border_rgb
        shape.line.width = Pt(1.2)
        return shape

    def add_kpi_card(slide, left, top, width, height, number_text, label_text, sub_text, num_color=C_EMERALD):
        card = add_card(slide, left, top, width, height)
        tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.12), width - Inches(0.3), height - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_num = tf.paragraphs[0]
        p_num.text = number_text
        p_num.font.name = FONT_MONO
        p_num.font.size = Pt(22)
        p_num.font.bold = True
        p_num.font.color.rgb = num_color

        p_lbl = tf.add_paragraph()
        p_lbl.text = label_text
        p_lbl.font.name = FONT_HEADING
        p_lbl.font.size = Pt(10.5)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = C_TEXT_WHITE
        p_lbl.space_before = Pt(2)

        p_sub = tf.add_paragraph()
        p_sub.text = sub_text
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(9)
        p_sub.font.color.rgb = C_TEXT_MUTED
        p_sub.space_before = Pt(2)

    def set_notes(slide, notes):
        ns = slide.notes_slide
        tf = ns.notes_text_frame
        tf.text = notes.strip()

    # =========================================================================
    # SLIDE 1: OFFICIAL DEFENSE TITLE SLIDE (WITH PARTNER LOGOS & SUPERVISORS)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    # Top Partner Brand Banner
    top_banner = add_card(s1, Inches(0.8), Inches(0.5), Inches(11.733), Inches(1.3), bg_rgb=RGBColor(15, 23, 42), border_rgb=C_CARD_BORDER)
    
    # Left: UIR Brand Box
    uir_card = add_card(s1, Inches(1.1), Inches(0.65), Inches(1.0), Inches(1.0), bg_rgb=RGBColor(7, 53, 103), border_rgb=C_ACCENT_BLUE)
    s1.shapes.add_picture(str(UIR_LOGO_PATH), Inches(1.15), Inches(0.70), width=Inches(0.9))

    tb_uir = s1.shapes.add_textbox(Inches(2.25), Inches(0.70), Inches(4.5), Inches(0.9))
    tf_uir = tb_uir.text_frame
    tf_uir.word_wrap = True
    p = tf_uir.paragraphs[0]
    p.text = "INTERNATIONAL UNIVERSITY OF RABAT (UIR)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_TEXT_WHITE
    p2 = tf_uir.add_paragraph()
    p2.text = "School of Data Science and Digital Engineering · Data Engineering (4th Year)"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = C_TEXT_MUTED

    # Right: DXC Technology Brand Box
    dxc_card = add_card(s1, Inches(9.8), Inches(0.65), Inches(2.4), Inches(1.0), bg_rgb=RGBColor(255, 255, 255), border_rgb=RGBColor(203, 213, 225))
    s1.shapes.add_picture(str(DXC_LOGO_PATH), Inches(9.95), Inches(0.78), width=Inches(2.1))

    # Center Hero Card
    hero = add_card(s1, Inches(0.8), Inches(2.0), Inches(11.733), Inches(3.6), bg_rgb=C_CARD_BG, border_rgb=C_ACCENT_BLUE)
    tb_hero = s1.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(10.9), Inches(3.2))
    tf_hero = tb_hero.text_frame
    tf_hero.word_wrap = True

    p_badge = tf_hero.paragraphs[0]
    p_badge.text = "PROJET DE FIN D'ANNÉE (PFA) · GRADUATION THESIS DEFENSE"
    p_badge.font.name = FONT_HEADING
    p_badge.font.size = Pt(11)
    p_badge.font.bold = True
    p_badge.font.color.rgb = C_ACCENT_BLUE

    p_h1 = tf_hero.add_paragraph()
    p_h1.text = "FX Trading Room P&L Application"
    p_h1.font.name = FONT_HEADING
    p_h1.font.size = Pt(30)
    p_h1.font.bold = True
    p_h1.font.color.rgb = C_TEXT_WHITE
    p_h1.space_before = Pt(6)

    p_sub = tf_hero.add_paragraph()
    p_sub.text = "Design, Development and Automation of a Data Engineering Platform for Foreign Exchange Profit & Loss Monitoring, Calculation, Risk Assessment and Front-to-Back Reconciliation (Accounting Currency: MAD)"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(12)
    p_sub.font.color.rgb = C_TEXT_MUTED
    p_sub.space_before = Pt(6)

    # Candidate & Supervisors Metadata Bar
    bottom_bar = add_card(s1, Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.2), bg_rgb=RGBColor(15, 23, 42), border_rgb=C_CARD_BORDER)
    tb_meta = s1.shapes.add_textbox(Inches(1.1), Inches(5.9), Inches(11.1), Inches(1.0))
    tf_m = tb_meta.text_frame
    tf_m.word_wrap = True

    c1, c2, c3 = tf_m.paragraphs[0], tf_m.add_paragraph(), tf_m.add_paragraph()
    c1.text = "Candidate: Mohamed Taha El Qassid (Data Engineering, 4th Year)   |   Academic Year: 2025 – 2026"
    c1.font.name = FONT_HEADING
    c1.font.size = Pt(11)
    c1.font.bold = True
    c1.font.color.rgb = C_EMERALD

    c2.text = "Academic Supervisor: Fayçal ZINEDINE, UIR   |   Company Supervisor: Samir GOURROUM, DXC Technology"
    c2.font.name = FONT_BODY
    c2.font.size = Pt(10.5)
    c2.font.bold = True
    c2.font.color.rgb = C_TEXT_WHITE
    c2.space_before = Pt(3)

    c3.text = "Host Company: DXC Technology Morocco   |   Institution: School of Data Science & Digital Engineering, UIR"
    c3.font.name = FONT_BODY
    c3.font.size = Pt(9.5)
    c3.font.color.rgb = C_TEXT_MUTED
    c3.space_before = Pt(3)

    set_notes(s1, """
Bonjour messieurs les membres du jury, monsieur Fayçal ZINEDINE pour l'UIR, monsieur Samir GOURROUM pour DXC Technology.
Je m'appelle Mohamed Taha El Qassid, étudiant en 4ème année Génie des Données (Data Engineering) à l'Université Internationale de Rabat.
J'ai l'honneur de vous présenter aujourd'hui mon projet de fin d'année réalisé au sein de DXC Technology :
'Conception, développement et automatisation d'une plateforme d'ingénierie des données pour le monitoring du P&L FX en devise comptable MAD'.
""")

    # =========================================================================
    # SLIDE 2: BUSINESS CONTEXT & PROBLEM STATEMENT (PUNCHY, EXECUTIVE)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_top_bar(s2, "Business Context & The Problem Statement", "01. INTRODUCTION & SCOPING")

    # 3 High-Impact Cards side by side
    col_w = Inches(3.7)
    col_h = Inches(5.4)

    # Card 1: Moroccan Trading Room Reality
    c1 = add_card(s2, Inches(0.8), Inches(1.5), col_w, col_h)
    tb = s2.shapes.add_textbox(Inches(1.0), Inches(1.7), col_w - Inches(0.4), col_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "The Trading Room Reality"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_BLUE

    points_1 = [
        ("Corporate Flows:", "OCP (phosphate export), Renault Tanger (vehicle export/import), and Afriquia (crude oil LC) execute multi-million FX contracts daily."),
        ("Market Making:", "Trading desks at Attijariwafa, BCP, and BMCE provide two-way pricing and manage intraday currency exposures."),
        ("Mandatory BAM Revaluation:", "Moroccan banks cannot carry foreign currency books legally. All contracts must revalue into MAD at 15:30 EOD fixing.")
    ]
    for h, b in points_1:
        p = tf.add_paragraph()
        p.text = f"• {h}"
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_WHITE
        p.space_before = Pt(10)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    # Card 2: Why Legacy Systems Fail
    c2 = add_card(s2, Inches(4.8), Inches(1.5), col_w, col_h)
    tb = s2.shapes.add_textbox(Inches(5.0), Inches(1.7), col_w - Inches(0.4), col_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Why Legacy Excel Fails"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_ROSE

    points_2 = [
        ("Front/Back Discrepancies:", "Traders book fast in FO, but Back-Office SWIFT MT300 affirmations differ due to slippage, fees, or partial fills."),
        ("Cross-Rate Calculation Risk:", "Valuing pairs like EUR/USD requires indirect cross multiplication with USD/MAD and EUR/MAD fixings."),
        ("Inventory Ambiguity:", "Inability to track FIFO lot unwinding versus CMP rolling cost causes undetected P&L drift across accounting periods.")
    ]
    for h, b in points_2:
        p = tf.add_paragraph()
        p.text = f"⚠ {h}"
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_ROSE
        p.space_before = Pt(10)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    # Card 3: The Data Engineering Solution
    c3 = add_card(s2, Inches(8.8), Inches(1.5), col_w, col_h)
    tb = s2.shapes.add_textbox(Inches(9.0), Inches(1.7), col_w - Inches(0.4), col_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Our Engineering Solution"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD

    points_3 = [
        ("Automated Medallion Pipeline:", "Idempotent ingestion -> Bronze staging -> dbt Silver mart -> Gold Python calculation engine."),
        ("Physical Integrity Enforcement:", "Database CHECK constraints & dbt singular tests enforce Total = Realized + Latent (BR3)."),
        ("Live FO/BO Reconciliation:", "Automated break matching detecting rate slippages, nominal breaks, and ghost trades with 1-click Excel export.")
    ]
    for h, b in points_3:
        p = tf.add_paragraph()
        p.text = f"✔ {h}"
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_EMERALD
        p.space_before = Pt(10)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    set_notes(s2, """
Ce projet répond à un défi opérationnel concret au sein des banques d'investissement :
Des flux massifs d'entreprises comme l'OCP ou Renault transitent par la salle de marché.
Les feuilles Excel manuelles génèrent des erreurs de calcul, des décalages non détectés entre le Front-Office et le Back-Office,
et ne respectent pas les impératifs d'auditabilité imposés par Bank Al-Maghrib.
Notre mission a été de bâtir un pipeline de données industriel garantissant l'intégrité comptable à chaque étape.
""")

    # =========================================================================
    # SLIDE 3: BANK AL-MAGHRIB REGULATORY FRAMEWORK (FIGURE 2.1 EMBEDDED)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_top_bar(s3, "Regulatory Framework: Bank Al-Maghrib Currency Basket & Peg", "02. REGULATORY FOUNDATIONS")

    # Left: Core Rules Card
    c_left = add_card(s3, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    tb = s3.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Bank Al-Maghrib Regime Mechanics"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_BLUE

    rules = [
        ("Base Currency: MAD", "Moroccan Dirham is the statutory accounting currency. Foreign currencies cannot be held as unvalued balances at close."),
        ("Basket Weighting (60/40):", "The central reference rate anchors to 60% Euro + 40% US Dollar, reflecting Morocco's foreign trade partner structure."),
        ("Central Rate Formulation:", "Central Rate = 0.60 * EUR/MAD + 0.40 * USD/MAD"),
        ("+/- 5% Fluctuation Band:", "Official peg band enacted January 2020. Market rates fluctuate within this boundary. Desks must stress-test positions at band extremes."),
        ("Statutory EOD Fixing (15:30):", "Official fixing published every business day at 15:30 by Bank Al-Maghrib; serves as legal revaluation standard.")
    ]
    for h, b in rules:
        p = tf.add_paragraph()
        p.text = f"• {h}"
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = C_GOLD if "Formulation" in h else C_TEXT_WHITE
        p.space_before = Pt(8)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    # Right: Embedded High-Res Diagram
    img_path = ASSETS_DIR / "bam_basket_band.png"
    if img_path.exists():
        s3.shapes.add_picture(str(img_path), Inches(6.7), Inches(1.6), width=Inches(5.8))

    set_notes(s3, """
Le régime de change marocain est un régime à parité glissante :
Le dirham est rattaché à un panier composé de 60% d'Euros et 40% de Dollars US, avec une marge de fluctuation de +/- 5%.
Bank Al-Maghrib publie son fixing officiel chaque jour à 15h30.
Notre plateforme intègre cette formule réglementaire et surveille en temps réel la position du cours central et des bornes de la bande.
""")

    # =========================================================================
    # SLIDE 4: FINANCIAL FUNDAMENTALS & INVARIANT BR3
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_top_bar(s4, "Financial Fundamentals & Golden Accounting Invariant (BR3)", "03. FINANCIAL ENGINEERING")

    # 3 Metric Cards
    add_kpi_card(s4, Inches(0.8), Inches(1.5), Inches(3.7), Inches(3.2), "1. MTM", "Mark-to-Market Valuation",
                 "Valuation of all open contracts against today's closing BAM fixing rate.\nDirect Pair: (Fixing - Traded) * Nominal\nCross Pair: (Fixing_EUR - Traded*Fixing_USD) * Nominal", C_ACCENT_BLUE)

    add_kpi_card(s4, Inches(4.8), Inches(1.5), Inches(3.7), Inches(3.2), "2. REALIZED", "Income Statement P&L",
                 "Definitive cash profit or loss realized when an open lot is unwound by an opposing trade.\nFlows directly into the bank's Income Statement (Compte de résultat).", C_EMERALD)

    add_kpi_card(s4, Inches(8.8), Inches(1.5), Inches(3.7), Inches(3.2), "3. LATENT", "Balance Sheet Reserve",
                 "Unrealized paper gain or loss on positions carried open overnight.\nRecorded on the Balance Sheet (Capitaux propres) as revaluation reserve.", C_GOLD)

    # Invariant Card at bottom
    inv_card = add_card(s4, Inches(0.8), Inches(4.9), Inches(11.733), Inches(2.0), bg_rgb=RGBColor(15, 23, 42), border_rgb=C_EMERALD)
    tb = s4.shapes.add_textbox(Inches(1.1), Inches(5.05), Inches(11.1), Inches(1.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "THE GOLDEN ACCOUNTING INVARIANT (BUSINESS RULE BR3)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD

    p_eq = tf.add_paragraph()
    p_eq.text = "Total MTM P&L = Realized P&L + Unrealized (Latent) P&L"
    p_eq.font.name = FONT_HEADING
    p_eq.font.size = Pt(20)
    p_eq.font.bold = True
    p_eq.font.color.rgb = C_TEXT_WHITE
    p_eq.space_before = Pt(4)

    p_sub = tf.add_paragraph()
    p_sub.text = "Enforcement: Enforced at database engine level via PostgreSQL CHECK (ROUND(total_mad, 2) = ROUND(realized_mad + unrealized_mad, 2)) and singular dbt SQL assertions. Guaranteed zero financial leakage."
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(10)
    p_sub.font.color.rgb = C_TEXT_MUTED
    p_sub.space_before = Pt(4)

    set_notes(s4, """
Voici le cœur financier de notre système :
Le MTM est la valeur liquidative théorique au cours officiel.
Il se décompose obligatoirement en deux sous-ensembles étanches :
- Le Réalisé, qui représente du cash effectif et va au Compte de Résultat.
- Le Latent, qui représente une plus ou moins-value potentielle et reste au Bilan.
Notre Business Rule BR3 stipule que Total = Réalisé + Latent. Cette contrainte est vérifiée physiquement en base de données.
""")

    # =========================================================================
    # SLIDE 5: CASE STUDY VALIDATION (THE 4 TRADES = +79,460 MAD)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_top_bar(s5, "Case Study Validation: The 4 Benchmark Trades (+79,460 MAD)", "04. MATHEMATICAL PROOF")

    # Left: Exact Table from Chapter 2 of Report
    c_tbl = add_card(s5, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    tb = s5.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.2), Inches(5.1))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Validation on Report Table 2.2 – 2.4"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_BLUE

    trades_txt = [
        ("T1: USD/MAD Buy 1M @ 9.9200", "BAM Fixing: 9.9500 MAD\nFormula: (9.95 - 9.92) * 1M = +30,000 MAD (MTM)"),
        ("T2: USD/MAD Sell 500k @ 9.9600", "Unwinds 500k of T1:\nRealized Cash = (9.96 - 9.92) * 500k = +20,000 MAD\nRemaining 500k Latent = (9.95 - 9.92) * 500k = +15,000 MAD"),
        ("T3: EUR/MAD Buy 800k @ 10.7700", "BAM Fixing: 10.8000 MAD\nFormula: (10.80 - 10.77) * 800k = +24,000 MAD (Latent)"),
        ("T4: EUR/USD Buy 600k @ 1.0820", "Synthetic Triangular Revaluation:\n(10.80 - (1.0820 * 9.95)) * 600k = +20,460 MAD (Latent)")
    ]
    for h, b in trades_txt:
        p = tf.add_paragraph()
        p.text = f"• {h}"
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_WHITE
        p.space_before = Pt(6)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    p_tot = tf.add_paragraph()
    p_tot.text = "\nPORTFOLIO RESULT: Total MTM = +79,460 MAD\nRealized = +20,000 MAD | Latent = +59,460 MAD (100% Match)"
    p_tot.font.bold = True
    p_tot.font.size = Pt(10.5)
    p_tot.font.color.rgb = C_EMERALD

    # Right: Embedded Chart
    img_path = ASSETS_DIR / "benchmark_pnl.png"
    if img_path.exists():
        s5.shapes.add_picture(str(img_path), Inches(6.7), Inches(1.6), width=Inches(5.8))

    set_notes(s5, """
Voici la preuve arithmétique rigoureuse sur le cas d'étude du rapport (Tables 2.2 à 2.4) :
Quatre transactions exécutées dans la journée :
- Le Trade 1 génère +30 000 MAD.
- Le Trade 2 déboucle la moitié du Trade 1, dégageant +20 000 MAD de réalisé et +15 000 MAD de latent.
- Le Trade 3 génère +24 000 MAD de latent.
- Le Trade 4 (EUR/USD) génère +20 460 MAD via le cross synthétique.
Le total portefeuille ressort exactement à +79 460 MAD, composé de +20 000 MAD réalisé et +59 460 MAD latent.
""")

    # =========================================================================
    # SLIDE 6: INVENTORY ACCOUNTING (FIFO VS CMP) & AUDIT CORRECTION
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_top_bar(s6, "Inventory Accounting: FIFO vs. CMP & Brief Audit Correction", "05. ALGORITHMIC INTEGRITY")

    c_left = add_card(s6, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    tb = s6.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.2), Inches(5.1))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Section 4 Proof: 2 Buys + 1 Partial Sale"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_BLUE

    f_txt = [
        ("Position Setup:", "Buy 1: 500k USD @ 9.9100  |  Buy 2: 500k USD @ 9.9300\nSale: 600k USD @ 9.9500"),
        ("FIFO Realized (Murex Standard):", "Lot 1 fully exhausted: (9.95 - 9.91) * 500k = +20,000 MAD\nLot 2 partially sold: (9.95 - 9.93) * 100k = +2,000 MAD\nTotal FIFO Realized = +22,000 MAD (Residual 400k @ 9.93)"),
        ("CMP Realized (Moroccan Accounting):", "Average Purchase Cost = (500k*9.91 + 500k*9.93)/1M = 9.9200 MAD\nRealized = (9.95 - 9.92) * 600k = +18,000 MAD (Residual 400k @ 9.92)"),
        ("Audit Discovery (Report Section 8.2):", "The initial brief prose stated '21,500 MAD (19,500 + 2,000)' due to a drafting typo. Our data engine mathematically audited and proved the true figure of 22,000 MAD.")
    ]
    for h, b in f_txt:
        p = tf.add_paragraph()
        p.text = f"• {h}"
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_GOLD if "Audit" in h else C_TEXT_WHITE
        p.space_before = Pt(6)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    img_path = ASSETS_DIR / "fifo_vs_cmp.png"
    if img_path.exists():
        s6.shapes.add_picture(str(img_path), Inches(6.7), Inches(1.6), width=Inches(5.8))

    set_notes(s6, """
Cette diapositive démontre notre esprit critique d'ingénieur :
En comparant le FIFO et le CMP sur l'exemple de référence, nous avons constaté une coquille dans le sujet original,
qui indiquait 21 500 MAD en mentionnant 19 500 + 2 000.
Or, 0.04 * 500 000 font exactement 20 000 MAD, ce qui donne un résultat mathématique rigoureux de 22 000 MAD.
Cette correction a été intégrée et documentée dans la section 8.2 de notre rapport.
""")

    # =========================================================================
    # SLIDE 7: DATA ENGINEERING ARCHITECTURE (FIGURE 4.1 EMBEDDED)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_top_bar(s7, "System Architecture: Medallion Data Engineering Pipeline", "06. SYSTEM ARCHITECTURE")

    img_path = ASSETS_DIR / "pipeline_arch.png"
    if img_path.exists():
        s7.shapes.add_picture(str(img_path), Inches(0.8), Inches(1.5), width=Inches(11.733))

    # 3 Summary Cards at bottom
    c_w = Inches(3.7)
    c_h = Inches(2.2)
    y_pos = Inches(4.8)

    add_kpi_card(s7, Inches(0.8), y_pos, c_w, c_h, "BRONZE", "Raw Ingestion Layer",
                 "• Ingestion from CSV / REST APIs\n• PostgreSQL / SQLite dual adapter\n• Idempotent deduplication via source_ref", C_ACCENT_BLUE)

    add_kpi_card(s7, Inches(4.8), y_pos, c_w, c_h, "SILVER", "Transformation Layer (dbt)",
                 "• Pure SQL marts (fact_trade_mtm)\n• Synthetic cross-rate conversions\n• Automated dbt singular test quality gates", C_GOLD)

    add_kpi_card(s7, Inches(8.8), y_pos, c_w, c_h, "GOLD", "Calculation & Reconciliation",
                 "• Python FIFO deque matching engine\n• FO vs. BO reconciliation (OS6)\n• daily_pnl persistence & Excel export", C_EMERALD)

    set_notes(s7, """
Sur le plan architectural, nous avons déployé l'architecture médaillon conforme aux meilleures pratiques de l'industrie :
- Bronze : stockage brut dans PostgreSQL avec basculement SQLite automatique.
- Silver : transformations SQL modulaires avec dbt pour calculer les cours croisés et le MTM.
- Gold : moteur Python haute performance utilisant des structures en deque pour le débouclage FIFO et la réconciliation.
""")

    # =========================================================================
    # SLIDE 8: DATA MODELING & ERD (FIGURE 5.1 & LOGICAL LOOKUP)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)
    add_top_bar(s8, "Data Modeling: Relational Schema & The Logical Lookup Strategy", "07. DATA MODELING")

    # Left: Schema Tables Card
    c_left = add_card(s8, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    tb = s8.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Relational Entities (Report Figure 5.1)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_BLUE

    entities = [
        ("BOOK:", "Stores trading desk metadata, assigned trader, default accounting method (FIFO/WAC), and stop-loss limits in MAD."),
        ("TRADE:", "Stores individual Front-Office deals: book_id, currency_pair, direction, nominal, traded rate, execution timestamp, and source_ref."),
        ("BACKOFFICE_SETTLEMENT:", "Stores Back-Office SWIFT MT300 settlement confirmations: settled nominal, settled rate, value date, and counterparty."),
        ("DAILY_PNL:", "Stores calculated EOD figures: realized_mad, unrealized_mad, total_mad. Protected by physical CHECK constraint.")
    ]
    for h, b in entities:
        p = tf.add_paragraph()
        p.text = f"• {h}"
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_WHITE
        p.space_before = Pt(8)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    # Right: Architectural Highlight (Why MARKET_RATE is unlinked)
    c_right = add_card(s8, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), bg_rgb=RGBColor(15, 23, 42), border_rgb=C_GOLD)
    tb = s8.shapes.add_textbox(Inches(7.1), Inches(1.7), Inches(5.1), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Architectural Design Decision (Report Section 5.1)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    decisions = [
        ("Why MARKET_RATE Has No Foreign Key:", "Deliberate design choice: A trade's closing rate is a temporal, logical lookup resolved dynamically at valuation time (by currency_pair and date), not a fixed relational dependency. Linking them with a hard foreign key would prevent revaluing trades against historical or simulated fixings."),
        ("Precision & Numerical Types:", "Zero floating-point rounding errors: All nominals, rates, and P&L metrics use NUMERIC(18,4) and NUMERIC(18,2) types."),
        ("Temporal Audit Trail:", "Full point-in-time reproducibility: historical EOD rates are preserved immutably, ensuring retroactive auditability.")
    ]
    for h, b in decisions:
        p = tf.add_paragraph()
        p.text = f"✔ {h}"
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_WHITE
        p.space_before = Pt(10)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_TEXT_MUTED

    set_notes(s8, """
Dans notre modèle relationnel, un choix de conception majeur concerne la table MARKET_RATE :
Elle n'est délibérément pas reliée par clé étrangère à la table TRADE.
En effet, le cours de valorisation d'un trade est une recherche logique temporelle basée sur la devise et la date,
et non un lien physique statique. Cela permet de rejouer des valorisations historiques ou d'exécuter des stress-tests sans altérer les transactions.
""")

    # =========================================================================
    # SLIDE 9: ORCHESTRATION WITH APACHE AIRFLOW DAG
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9)
    add_top_bar(s9, "Pipeline Orchestration: Apache Airflow DAG at 15:35 EOD", "08. WORKFLOW AUTOMATION")

    # Left: Task sequence
    c_left = add_card(s9, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    tb = s9.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.2), Inches(5.1))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "EOD Workflow: 'fx_pnl_daily_closing'"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_BLUE

    dag_tasks = [
        ("CRON: 35 15 * * 1-5", "Triggered at 15:35 every business day, exactly 5 minutes after Bank Al-Maghrib publishes the fixing."),
        ("1. wait_for_bam_fixing (Sensor):", "Polls the market fixing table; retries with exponential backoff if BAM publication is delayed."),
        ("2. ingest_eod_trades (PythonOperator):", "Extracts raw FO tickets and BO SWIFT records into Bronze staging tables."),
        ("3. dbt_run_mtm (BashOperator):", "Compiles and executes dbt Silver marts (fact_trade_mtm)."),
        ("4. dbt_test_integrity:", "Executes singular assertion tests. Acts as a circuit-breaker halting the run if errors occur."),
        ("5. compute_fifo_pnl & reconcile_fo_bo:", "Executes the Gold Python engine, writes to daily_pnl, and generates the audit package.")
    ]
    for h, b in dag_tasks:
        p = tf.add_paragraph()
        p.text = f"• {h}"
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_EMERALD if "Sensor" in h or "Operator" in h or "dbt" in h else C_TEXT_WHITE
        p.space_before = Pt(5)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    # Right: Production Engineering Qualities
    c_right = add_card(s9, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), bg_rgb=RGBColor(15, 23, 42), border_rgb=C_ACCENT_BLUE)
    tb = s9.shapes.add_textbox(Inches(7.1), Inches(1.7), Inches(5.1), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Production Engineering Guarantees"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_BLUE

    guarantees = [
        ("Idempotency Guaranteed:", "Any historical date can be re-run safely without corrupting data or duplicating P&L records."),
        ("Circuit-Breaker Quality Gates:", "If a dbt test fails (e.g. rate <= 0 or Total != Realized + Latent), the pipeline fails fast before bad data reaches reporting."),
        ("Disaster Recovery Fallback:", "Transparent failover from PostgreSQL container to local SQLite database if infrastructure issues occur."),
        ("Auditable Logging:", "Every step produces execution logs, task run duration, and status alerts.")
    ]
    for h, b in guarantees:
        p = tf.add_paragraph()
        p.text = f"✔ {h}"
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_WHITE
        p.space_before = Pt(10)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_TEXT_MUTED

    set_notes(s9, """
L'orchestration est confiée à Apache Airflow :
Le déclenchement quotidien est fixé à 15h35. Le DAG attend d'abord la publication officielle de Bank Al-Maghrib via un Sensor,
puis enchaîne l'ingestion, le dbt run, les tests d'intégrité faisant office de disjoncteur (circuit-breaker),
et enfin le calcul du P&L et la génération du rapport d'audit.
""")

    # =========================================================================
    # SLIDE 10: AUTOMATED TESTING & DATA QUALITY CONTRACTS (TABLE 8.1)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10)
    add_top_bar(s10, "Automated Testing & Data Quality Contracts (10/10 PASS)", "09. QUALITY ASSURANCE")

    # Left: Pytest Suite
    c_left = add_card(s10, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    tb = s10.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.2), Inches(5.1))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Automated Pytest Suite (10 Tests in 0.51s)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD

    tests = [
        ("test_individual_trade_mtm:", "Validates exact MTM on USD/MAD, EUR/MAD, and cross EUR/USD."),
        ("test_realized_and_unrealized_split:", "Confirms +20k MAD Realized and +59,460 MAD Latent split."),
        ("test_supporting_example_fifo_vs_cmp:", "Validates +22k FIFO vs +18k CMP on 2 purchases + 1 sale."),
        ("test_business_rule_br3_identity:", "Validates Total = Realized + Latent on 100 random deals."),
        ("test_reconciliation_exact_matches:", "Verifies 0 discrepancies on clean matched trades."),
        ("test_reconciliation_rate_slippage:", "Detects pip-level price variance and computes MAD impact."),
        ("test_reconciliation_nominal_mismatch:", "Detects partial fills and credit ceiling cuts."),
        ("test_reconciliation_unconfirmed_trade:", "Flags ghost trades with missing SWIFT confirmations.")
    ]
    for h, b in tests:
        p = tf.add_paragraph()
        p.text = f"✔ {h}"
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = C_EMERALD
        p.space_before = Pt(3)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = C_TEXT_MUTED

    # Right: dbt Contracts Table
    c_right = add_card(s10, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4))
    tb = s10.shapes.add_textbox(Inches(7.1), Inches(1.65), Inches(5.1), Inches(5.1))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "dbt Automated Data Contracts (Report Tab 8.1)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_BLUE

    dbt_rules = [
        ("BR1: BAM Rate Conversion", "Guarantees every currency pair resolves to MAD closing rate; rejects null rates.", "PASS"),
        ("BR2: Rate Revaluation", "Verifies all open tickets are revalued at today's official Bank Al-Maghrib fixing.", "PASS"),
        ("BR3: Accounting Invariant", "Singular SQL test: SELECT * WHERE ROUND(total) != ROUND(realized + latent). Must return 0.", "PASS"),
        ("BR4: FIFO Chronological Order", "Verifies queue unwinding cannot consume a newer lot before earlier timestamped lots.", "PASS"),
        ("Idempotent Deduplication", "source_ref uniqueness constraint prevents duplicate trade bookings.", "PASS")
    ]
    for name, desc, status in dbt_rules:
        p = tf.add_paragraph()
        p.text = f"• {name}  [{status}]"
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_WHITE
        p.space_before = Pt(6)
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    set_notes(s10, """
La fiabilité de notre solution est démontrée par une suite complète de 10 tests unitaires sous pytest,
exécutés en 0.51 seconde, combinée aux assertions dbt.
Chaque règle métier (BR1 à BR4) et chaque cas d'anomalie de réconciliation est testé et validé mathématiquement.
""")

    # =========================================================================
    # SLIDE 11: FRONT-TO-BACK RECONCILIATION & THE 4 BANKING BREAKS (OS6)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_bg(s11)
    add_top_bar(s11, "Front-to-Back Reconciliation: Auditing the 4 Banking Breaks", "10. RECONCILIATION HUB (OS6)")

    # Left: The 4 Conflict Scenarios
    c_left = add_card(s11, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    tb = s11.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.2), Inches(5.1))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "The 4 Real-World Banking Breaks Simulated"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_BLUE

    breaks = [
        ("Break 1: Rate Slippage (BMCE Bank of Africa)", "FO booked EUR/MAD @ 10.7950, but BO confirmation arrived @ 10.7985 (+35 pips / -2,450 MAD variance due to interbank spread)."),
        ("Break 2: Nominal Mismatch (Attijariwafa Bank)", "FO booked 1.5M USD, but BO settled only 1.4M USD (-100k USD missing because the counterparty's intraday credit ceiling was reached)."),
        ("Break 3: Unconfirmed SWIFT MT300 (BNP Paribas)", "FO trader executed EUR/USD 500k at 17:15, but BO received no affirmation message. Poses unhedged overnight currency risk."),
        ("Break 4: Orphan Settlement (Barclays Bank)", "BO received confirmed settlement for 300k GBP, but no FO ticket was booked. Detects rogue or unrecorded dealer trades.")
    ]
    for h, b in breaks:
        p = tf.add_paragraph()
        p.text = f"⚠ {h}"
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_ROSE if "Break" in h else C_TEXT_WHITE
        p.space_before = Pt(6)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    img_path = ASSETS_DIR / "fo_bo_breaks.png"
    if img_path.exists():
        s11.shapes.add_picture(str(img_path), Inches(6.7), Inches(1.6), width=Inches(5.8))

    set_notes(s11, """
Le module de réconciliation Front-to-Back (OS6) compare les tickets de négociation Front-Office aux confirmations SWIFT MT300 du Back-Office.
Nous simulons 4 cas de litiges bancaires concrets :
- L'écart de cours (Rate Slippage) sur BMCE (-2 450 MAD).
- L'écart de nominal (Nominal Mismatch) sur Attijariwafa (-100 000 USD suite au plafonnement de la ligne de crédit).
- La transaction non confirmée sur BNP Paribas, générant un risque de change ouvert la nuit.
- Le règlement orphelin de Barclays sans ticket Front-Office.
Notre système calcule automatiquement l'impact financier en MAD et génère un dossier d'audit Excel opposable aux commissaires aux comptes.
""")

    # =========================================================================
    # SLIDE 12: MARKET RISK & GOLD BREAKOUT ABOVE $4,000/OZ
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_bg(s12)
    add_top_bar(s12, "Live Market Terminal & LBMA Gold Crossing Above $4,000/oz", "11. MARKET DYNAMICS")

    c_left = add_card(s12, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    tb = s12.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.2), Inches(5.1))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Multi-Asset Monitoring & Gold Dynamics"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_BLUE

    g_points = [
        ("Multi-Asset Universe:", "• USD/MAD & EUR/MAD (BAM Fixing)\n• EUR/USD & GBP/MAD (Cross & Interbank)\n• XAU/USD (LBMA Gold Spot Benchmark)"),
        ("The Historic $4,000/oz Breakthrough:", "Gold crossed the historic resistance milestone of $4,000 / oz (trading at $4,038.50). In our platform, corporate treasuries monitor gold as a sovereign inflation and currency hedge."),
        ("Institutional Technical Analysis:", "Dual-pane financial charting: Candlesticks (green/red), 20-period Simple Moving Average (SMA), and trading volume histograms."),
        ("BAM Live Feed Integration:", "Integrated live REST feed pulling quotes and instantly updating central basket rates.")
    ]
    for h, b in g_points:
        p = tf.add_paragraph()
        p.text = f"• {h}"
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_GOLD if "Gold" in h else C_TEXT_WHITE
        p.space_before = Pt(6)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    img_path = ASSETS_DIR / "gold_chart.png"
    if img_path.exists():
        s12.shapes.add_picture(str(img_path), Inches(6.7), Inches(1.6), width=Inches(5.8))

    set_notes(s12, """
Sur ce terminal de marché, nous visualisons l'environnement de cotation multi-actifs.
Comme vous pouvez l'observer sur le graphique en chandeliers japonais, l'or a franchi le cap historique des 4 000 dollars l'once,
s'établissant aujourd'hui autour de 4 038 dollars.
Ce suivi est primordial pour les trésoriers d'entreprises qui utilisent l'or comme réserve de valeur et couverture contre l'inflation.
Le graphique intègre une moyenne mobile à 20 jours et les volumes de transaction.
""")

    # =========================================================================
    # SLIDE 13: INTERACTIVE STREAMLIT WORKSPACE (THE 6 TABS)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_bg(s13)
    add_top_bar(s13, "Interactive Trading Terminal: Streamlit Multi-Tab Workspace", "12. APPLICATION INTERFACE")

    # 6 Feature Cards representing the 6 Workspace Tabs
    tabs_data = [
        ("Tab 1: Trading Desk & Blotter", "Active portfolio KPIs (Total MTM, Realized, Latent), trade blotter with explicit mathematical formulas in MAD, and pre-trade deal ticket simulator."),
        ("Tab 2: FO / BO Reconciliation Hub", "Comprehensive discrepancy detection (rate slippage, nominal break, unconfirmed SWIFT), pips variance, and 1-click Excel audit package download."),
        ("Tab 3: Live Market Browser & Gold", "Interactive dual-pane financial charting: Candlesticks, 20-period SMA, volume histograms, and LBMA Gold $4,000 breakthrough marker."),
        ("Tab 4: Inventory Accounting (FIFO/CMP)", "Visual step-by-step demonstration of Section 4 lot depletion, explaining convergence upon closure and the brief's arithmetic audit note."),
        ("Tab 5: BAM Fluctuation Band Matrix", "Stress-testing matrix simulating +/- 1%, +/- 3%, and +/- 5% currency basket boundary shifts and stop-loss breach alerts."),
        ("Tab 6: Data Engineering Lineage", "End-to-end architecture diagram, dbt test results table, and Airflow DAG orchestration contract enforcement.")
    ]

    for idx, (tab_title, tab_desc) in enumerate(tabs_data):
        col = idx % 2
        row = idx // 2
        x = Inches(0.8 + col * 6.0)
        y = Inches(1.6 + row * 1.8)
        
        add_card(s13, x, y, Inches(5.7), Inches(1.6), bg_rgb=C_CARD_BG, border_rgb=C_CARD_BORDER)
        tb = s13.shapes.add_textbox(x + Inches(0.2), y + Inches(0.15), Inches(5.3), Inches(1.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = tab_title
        p.font.name = FONT_HEADING
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_ACCENT_BLUE if idx < 3 else C_EMERALD
        
        p_d = tf.add_paragraph()
        p_d.text = tab_desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_MUTED
        p_d.space_before = Pt(4)

    set_notes(s13, """
Pour la restitution utilisateur, nous avons conçu une interface professionnelle de type terminal financier (style Murex / Bloomberg) :
Elle est organisée en 6 onglets clairs :
1. Trading Desk & Blotter : formule arithmétique de chaque trade et simulateur d'ordre avant exécution.
2. Hub de Réconciliation FO/BO : détection automatique des anomalies et téléchargement du dossier d'audit Excel en un clic.
3. Live Market Terminal : graphiques en chandeliers et suivi de l'or au-dessus des 4 000 dollars.
4. Comptabilité d'inventaire : comparaison FIFO vs CMP.
5. Stress Testing Bank Al-Maghrib : matrice de sensibilité +/- 5%.
6. Lignage Data Engineering : contrats de données et assertions dbt.
""")

    # =========================================================================
    # SLIDE 14: EVALUATION CRITERIA ALIGNMENT & CONCLUSION
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_bg(s14)
    add_top_bar(s14, "Evaluation Criteria Alignment, Conclusion & Perspectives", "13. CONCLUSION & DEFENSE")

    # Left: Evaluation Criteria Table from Report Table 10.3
    c_left = add_card(s14, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    tb = s14.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.2), Inches(5.1))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Alignment with Evaluation Criteria (Report Tab 10.3)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_EMERALD

    crit = [
        ("Business-Domain Mastery (25%):", "Full compliance with Bank Al-Maghrib peg, MTM, Realized/Latent, and validated corrections to source brief."),
        ("Design Quality (20%):", "Medallion layered pipeline (Bronze/Silver/Gold), ERD with logical lookup, and UML models."),
        ("Development Quality (25%):", "10/10 automated tests, dbt data contracts, and dual PostgreSQL/SQLite storage adapter."),
        ("Relevance of Results (15%):", "Validated benchmark dataset (+79,460 MAD) and realistic FO/BO reconciliation breaks."),
        ("Documentation & Report (10%):", "Comprehensive 33-page technical thesis report and reproducible deployment setup.")
    ]
    for h, b in crit:
        p = tf.add_paragraph()
        p.text = f"✔ {h}"
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = C_TEXT_WHITE
        p.space_before = Pt(4)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = C_TEXT_MUTED

    # Right: Future Perspectives & Thank You
    c_right = add_card(s14, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), bg_rgb=RGBColor(15, 23, 42), border_rgb=C_ACCENT_BLUE)
    tb = s14.shapes.add_textbox(Inches(7.1), Inches(1.65), Inches(5.1), Inches(5.1))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Future Technical Perspectives"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_ACCENT_BLUE

    futures = [
        ("Real-Time Kafka Streaming:", "Transition from 15:35 EOD batch processing to sub-second tick-by-tick real-time position keeping via Apache Kafka."),
        ("SWIFT MT300 Direct Parser:", "Automated ingestion of raw ISO 15022/20022 SWIFT confirmation messages directly from interbank networks."),
        ("Multi-Factor Monte Carlo VaR:", "Advanced Value-at-Risk modeling across non-linear currency options and structural FX forward curves.")
    ]
    for h, b in futures:
        p = tf.add_paragraph()
        p.text = f"➔ {h}"
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = C_GOLD
        p.space_before = Pt(8)
        p_d = tf.add_paragraph()
        p_d.text = b
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_TEXT_MUTED

    p_thx = tf.add_paragraph()
    p_thx.text = "\nThank you for your attention.\nQuestions & Discussion."
    p_thx.font.name = FONT_HEADING
    p_thx.font.size = Pt(16)
    p_thx.font.bold = True
    p_thx.font.color.rgb = C_TEXT_WHITE
    p_thx.space_before = Pt(12)

    set_notes(s14, """
Pour conclure, ce projet allie rigueur mathématique, respect scrupuleux de la réglementation de Bank Al-Maghrib et ingénierie des données moderne.
Le tableau d'alignement avec les critères d'évaluation montre que l'ensemble des exigences académiques et professionnelles ont été satisfaites.
Je remercie chaleureusement mon encadrant académique monsieur Fayçal ZINEDINE (UIR), mon encadrant professionnel monsieur Samir GOURROUM (DXC),
ainsi que l'ensemble des membres du jury pour leur écoute attentive.
Je suis à votre entière disposition pour vos questions.
""")

    # Save upgraded presentation
    output_path = PRES_DIR / "FX_Trading_Room_PFE_Defense_Mohamed_Taha.pptx"
    prs.save(output_path)
    print(f"Upgraded Presentation successfully created at: {output_path}")


if __name__ == "__main__":
    create_deck()
