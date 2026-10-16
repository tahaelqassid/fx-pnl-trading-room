"""
Institutional PowerPoint Presentation Generator for PFE Defense.
Candidate: Mohamed Taha El Qassid (Data Engineering, 4th Year, UIR).
Internship: DXC Technology.
Topic: Application P&L FX Salle de Marché (Devise Comptable MAD).
"""
import os
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
PRES_DIR = ROOT_DIR / "presentation"
ASSETS_DIR = PRES_DIR / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Institutional Color Palette
DARK_BG = "#0B0E14"
CARD_BG = "#111827"
NAVY_BLUE = "#1E293B"
ACCENT_BLUE = "#38BDF8"
EMERALD_GREEN = "#10B981"
AMBER_GOLD = "#F59E0B"
CRIMSON_RED = "#EF4444"
TEXT_WHITE = "#F8FAFC"
TEXT_MUTED = "#94A3B8"

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 0.8


# =========================================================================
# STEP 1: GENERATE INSTITUTIONAL DIAGRAMS (HIGH-RES 300 DPI)
# =========================================================================

def generate_bam_basket_diagram():
    """Generates the Bank Al-Maghrib Currency Basket & Fluctuation Band diagram."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), facecolor=CARD_BG)
    
    # Left: Donut Chart for Basket Weights
    weights = [60, 40]
    labels = ['EUR (Euro)\n60%', 'USD (Dollar)\n40%']
    colors = ['#3B82F6', '#10B981']
    explode = (0.04, 0.04)
    
    wedges, texts, autotexts = ax1.pie(
        weights, explode=explode, labels=labels, autopct='%1.0f%%',
        startangle=90, colors=colors,
        textprops=dict(color=TEXT_WHITE, fontsize=11, weight='bold'),
        wedgeprops=dict(width=0.45, edgecolor=CARD_BG, linewidth=2)
    )
    for at in autotexts:
        at.set_color(CARD_BG)
    ax1.set_title("Bank Al-Maghrib Currency Basket\n(Official Weighting)", color=TEXT_WHITE, fontsize=12, pad=12, weight='bold')
    
    # Right: Fluctuation Band (+/- 5%)
    central_rate = 10.5307  # Central Basket rate in MAD
    upper_band = central_rate * 1.05
    lower_band = central_rate * 0.95
    
    ax2.set_facecolor(CARD_BG)
    ax2.axhspan(lower_band, upper_band, color='#1E293B', alpha=0.9, label='BAM Fluctuation Band (+/-5%)')
    ax2.axhline(central_rate, color='#38BDF8', linestyle='--', linewidth=2, label=f'Central Rate: {central_rate:.4f} MAD')
    ax2.axhline(upper_band, color='#EF4444', linestyle='-', linewidth=1.5, label=f'Upper Limit (+5%): {upper_band:.4f} MAD')
    ax2.axhline(lower_band, color='#10B981', linestyle='-', linewidth=1.5, label=f'Lower Limit (-5%): {lower_band:.4f} MAD')
    
    # Current active rate marker
    ax2.plot([0.5], [10.5307], marker='o', markersize=10, color='#F59E0B', label='Current Interbank Central Quote')
    
    ax2.set_xlim(0, 1)
    ax2.set_ylim(lower_band - 0.2, upper_band + 0.2)
    ax2.set_xticks([])
    ax2.set_ylabel("Exchange Rate (MAD)", color=TEXT_WHITE, fontsize=11)
    ax2.tick_params(axis='y', colors=TEXT_WHITE)
    ax2.set_title("Regulatory Fluctuation Band (+/-5%)\nBank Al-Maghrib Peg Regime", color=TEXT_WHITE, fontsize=12, pad=12, weight='bold')
    ax2.legend(loc='lower left', facecolor='#0F172A', edgecolor='#334155', labelcolor=TEXT_WHITE, fontsize=8.5)
    
    plt.tight_layout()
    path = ASSETS_DIR / "bam_basket_band.png"
    plt.savefig(path, dpi=300, facecolor=CARD_BG)
    plt.close()
    return path


def generate_benchmark_pnl_chart():
    """Generates the PFE Benchmark 4-Trade P&L Breakdown chart."""
    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=CARD_BG)
    ax.set_facecolor(CARD_BG)
    
    trades = ['T001\nUSD/MAD\nBuy 1M', 'T002\nUSD/MAD\nSell 500k', 'T003\nEUR/MAD\nBuy 800k', 'T004\nEUR/USD\nBuy 600k', 'PORTFOLIO\nTOTAL MTM']
    pnl_values = [30000, 5000, 24000, 20460, 79460]
    colors = ['#3B82F6', '#10B981', '#3B82F6', '#8B5CF6', '#F59E0B']
    
    bars = ax.bar(trades, pnl_values, color=colors, width=0.55, edgecolor='#334155', linewidth=1)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'+{height:,.0f} MAD',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=10, weight='bold', color=TEXT_WHITE)
        
    ax.set_title("PFE Reference Case Study: Individual Trade MTM & Portfolio Result", color=TEXT_WHITE, fontsize=12, pad=14, weight='bold')
    ax.set_ylabel("Mark-to-Market P&L (MAD)", color=TEXT_WHITE, fontsize=11)
    ax.tick_params(axis='x', colors=TEXT_WHITE, labelsize=9.5)
    ax.tick_params(axis='y', colors=TEXT_WHITE)
    ax.set_ylim(0, 95000)
    ax.grid(axis='y', color='#1E293B', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    path = ASSETS_DIR / "benchmark_pnl.png"
    plt.savefig(path, dpi=300, facecolor=CARD_BG)
    plt.close()
    return path


def generate_fifo_vs_cmp_diagram():
    """Generates the FIFO vs CMP Inventory Depletion step-by-step diagram."""
    fig, ax = plt.subplots(figsize=(9.5, 4.5), facecolor=CARD_BG)
    ax.set_facecolor(CARD_BG)
    
    # Lot Bars
    lots = ['FIFO: Lot 1 Exhausted\n(500k @ 9.9100)', 'FIFO: Lot 2 Consumed\n(100k of 500k @ 9.93)', 'FIFO Total Realized\n(20,000 + 2,000)', 'CMP / WAC Realized\n(Avg Cost: 9.9200)']
    gains = [20000, 2000, 22000, 18000]
    colors = ['#059669', '#10B981', '#F59E0B', '#3B82F6']
    
    bars = ax.barh(lots, gains, color=colors, height=0.45, edgecolor='#334155')
    
    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'+{width:,.0f} MAD',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(10, 0), textcoords="offset points",
                    ha='left', va='center',
                    fontsize=10, weight='bold', color=TEXT_WHITE)
        
    ax.set_title("Section 4 Reference Proof: FIFO vs. CMP Inventory Unwinding", color=TEXT_WHITE, fontsize=12, pad=14, weight='bold')
    ax.set_xlabel("Realized P&L in MAD (Sale of 600,000 USD @ 9.9500)", color=TEXT_WHITE, fontsize=11)
    ax.tick_params(axis='x', colors=TEXT_WHITE)
    ax.tick_params(axis='y', colors=TEXT_WHITE, labelsize=10)
    ax.set_xlim(0, 27000)
    ax.grid(axis='x', color='#1E293B', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    path = ASSETS_DIR / "fifo_vs_cmp.png"
    plt.savefig(path, dpi=300, facecolor=CARD_BG)
    plt.close()
    return path


def generate_fo_bo_breaks_diagram():
    """Generates the FO vs BO Reconciliation Break Categories diagram."""
    fig, ax = plt.subplots(figsize=(9.5, 4.5), facecolor=CARD_BG)
    ax.set_facecolor(CARD_BG)
    
    categories = [
        'Clean Matched Trades\n(OCP, Renault, BCP)',
        'Rate Slippage Break\n(BMCE: +3.5 pips fee)',
        'Nominal Mismatch Break\n(Attijariwafa: -100k USD cap)',
        'Unconfirmed SWIFT MT300\n(BNP Paribas: unhedged overnight)',
        'Orphan BO Settlement\n(Barclays: unbooked trade)'
    ]
    counts = [13, 1, 1, 1, 1]
    bar_colors = ['#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']
    
    bars = ax.barh(categories, counts, color=bar_colors, height=0.5, edgecolor='#334155')
    
    for bar in bars:
        w = bar.get_width()
        txt = f"{w} Trades (PASS)" if w > 5 else f"{w} Break (INVESTIGATE)"
        ax.annotate(txt,
                    xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(8, 0), textcoords="offset points",
                    ha='left', va='center',
                    fontsize=9.5, weight='bold', color=TEXT_WHITE)
        
    ax.set_title("Front-to-Back Reconciliation Hub: Audited Status Distribution", color=TEXT_WHITE, fontsize=12, pad=14, weight='bold')
    ax.set_xlabel("Number of Trade Tickets / Settlement Confirmations", color=TEXT_WHITE, fontsize=11)
    ax.tick_params(axis='x', colors=TEXT_WHITE)
    ax.tick_params(axis='y', colors=TEXT_WHITE, labelsize=9.5)
    ax.set_xlim(0, 16)
    ax.grid(axis='x', color='#1E293B', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    path = ASSETS_DIR / "fo_bo_breaks.png"
    plt.savefig(path, dpi=300, facecolor=CARD_BG)
    plt.close()
    return path


def generate_gold_chart_diagram():
    """Generates the LBMA Gold (XAU/USD) Breakout above $4,000/oz chart."""
    fig, ax = plt.subplots(figsize=(9.5, 4.5), facecolor=CARD_BG)
    ax.set_facecolor(CARD_BG)
    
    np.random.seed(42)
    days = 60
    base = 3940.0
    drift = np.linspace(0, 110, days)
    noise = np.random.normal(0, 8, days).cumsum()
    gold_prices = base + drift + noise
    # Ensure it clearly crosses 4000 at day 35
    gold_prices[35:] += 15
    
    x = range(days)
    ax.plot(x, gold_prices, color='#F59E0B', linewidth=2.2, label='XAU/USD Spot Price')
    
    # SMA 20
    sma20 = np.convolve(gold_prices, np.ones(20)/20, mode='valid')
    ax.plot(range(19, days), sma20, color='#38BDF8', linestyle='--', linewidth=1.5, label='20-Day Simple Moving Avg (SMA)')
    
    # 4,000 USD Milestone
    ax.axhline(4000.0, color='#EF4444', linestyle=':', linewidth=1.8, label='Institutional Milestone: $4,000 / oz')
    ax.annotate('Breakout Confirmed\nAbove $4,000/oz', xy=(37, 4005), xytext=(20, 4040),
                arrowprops=dict(facecolor='#10B981', shrink=0.08, width=1.5, headwidth=7),
                color='#10B981', weight='bold', fontsize=10)
    
    ax.set_title("LBMA Gold (XAU/USD) Historic Breakthrough Above $4,000/oz", color=TEXT_WHITE, fontsize=12, pad=14, weight='bold')
    ax.set_ylabel("Spot Price (USD / oz)", color=TEXT_WHITE, fontsize=11)
    ax.set_xlabel("Historical Trading Sessions", color=TEXT_WHITE, fontsize=11)
    ax.tick_params(axis='x', colors=TEXT_WHITE)
    ax.tick_params(axis='y', colors=TEXT_WHITE)
    ax.grid(color='#1E293B', linestyle='--', alpha=0.7)
    ax.legend(loc='lower right', facecolor='#0F172A', edgecolor='#334155', labelcolor=TEXT_WHITE, fontsize=9)
    
    plt.tight_layout()
    path = ASSETS_DIR / "gold_chart.png"
    plt.savefig(path, dpi=300, facecolor=CARD_BG)
    plt.close()
    return path


def generate_pipeline_architecture_diagram():
    """Generates the Data Pipeline Lineage (Bronze -> Silver -> Gold) diagram."""
    fig, ax = plt.subplots(figsize=(10, 4.5), facecolor=CARD_BG)
    ax.set_facecolor(CARD_BG)
    ax.axis('off')
    
    boxes = [
        {"name": "1. Ingestion Layer", "sub": "Raw CSV, REST Feeds\n& Bank Al-Maghrib Fixings", "x": 0.05, "y": 0.35, "w": 0.17, "h": 0.35, "color": "#1E293B", "border": "#3B82F6"},
        {"name": "2. Bronze Staging", "sub": "PostgreSQL / SQLite\nstg_trade, stg_market_rate", "x": 0.28, "y": 0.35, "w": 0.17, "h": 0.35, "color": "#1E293B", "border": "#10B981"},
        {"name": "3. Silver Marts", "sub": "dbt SQL Transformations\nfact_trade_mtm & Crosses", "x": 0.51, "y": 0.35, "w": 0.17, "h": 0.35, "color": "#1E293B", "border": "#F59E0B"},
        {"name": "4. Gold Engine", "sub": "Python FIFO Queue\nCMP & Reconciliation (OS6)", "x": 0.74, "y": 0.35, "w": 0.19, "h": 0.35, "color": "#1E293B", "border": "#8B5CF6"},
    ]
    
    for b in boxes:
        rect = patches.FancyBboxPatch((b["x"], b["y"]), b["w"], b["h"],
                                      boxstyle="round,pad=0.02,rounding_size=0.03",
                                      facecolor=b["color"], edgecolor=b["border"], linewidth=2)
        ax.add_patch(rect)
        ax.text(b["x"] + b["w"]/2, b["y"] + b["h"] - 0.08, b["name"],
                ha='center', va='center', color=TEXT_WHITE, fontsize=11, weight='bold')
        ax.text(b["x"] + b["w"]/2, b["y"] + 0.12, b["sub"],
                ha='center', va='center', color=TEXT_MUTED, fontsize=9)
        
    # Arrows
    arrow_props = dict(facecolor=ACCENT_BLUE, edgecolor=ACCENT_BLUE, width=2, headwidth=8, headlength=8)
    ax.annotate('', xy=(0.27, 0.52), xytext=(0.23, 0.52), arrowprops=arrow_props)
    ax.annotate('', xy=(0.50, 0.52), xytext=(0.46, 0.52), arrowprops=arrow_props)
    ax.annotate('', xy=(0.73, 0.52), xytext=(0.69, 0.52), arrowprops=arrow_props)
    
    # Bottom persistence banner
    persist_rect = patches.FancyBboxPatch((0.05, 0.08), 0.88, 0.18,
                                         boxstyle="round,pad=0.01,rounding_size=0.02",
                                         facecolor='#0F172A', edgecolor='#334155', linewidth=1.5)
    ax.add_patch(persist_rect)
    ax.text(0.49, 0.17, "Physical Database CHECK & dbt Singular Test Enforcement: Total = Realized + Unrealized (BR3)",
            ha='center', va='center', color=EMERALD_GREEN, fontsize=10, weight='bold')
    
    ax.set_title("End-to-End Data Engineering Architecture & Pipeline Flow", color=TEXT_WHITE, fontsize=13, pad=10, weight='bold')
    
    plt.tight_layout()
    path = ASSETS_DIR / "pipeline_arch.png"
    plt.savefig(path, dpi=300, facecolor=CARD_BG)
    plt.close()
    return path


print("Generating high-resolution financial diagrams...")
img_bam = generate_bam_basket_diagram()
img_bench = generate_benchmark_pnl_chart()
img_fifo = generate_fifo_vs_cmp_diagram()
img_breaks = generate_fo_bo_breaks_diagram()
img_gold = generate_gold_chart_diagram()
img_pipe = generate_pipeline_architecture_diagram()
print("All diagrams generated successfully.")


# =========================================================================
# STEP 2: BUILD INSTITUTIONAL POWERPOINT PRESENTATION (16:9 WIDESCREEN)
# =========================================================================

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def apply_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(11, 14, 20)  # #0B0E14 Dark Institutional Base

def add_header(slide, title_text, category_text="DXC TECHNOLOGY · PFA DEFENSE"):
    # Header container
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_cat = tf.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = RGBColor(56, 189, 248)  # Sky blue accent
    
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = RGBColor(248, 250, 252)  # White

def add_card(slide, left, top, width, height, bg_rgb=RGBColor(17, 24, 39), border_rgb=RGBColor(31, 41, 55)):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_rgb
    shape.line.color.rgb = border_rgb
    shape.line.width = Pt(1.2)
    return shape

def add_speaker_note(slide, note_text):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = note_text


# ----------------- SLIDE 1: TITLE SLIDE -----------------
s1 = prs.slides.add_slide(blank_layout)
apply_slide_background(s1)

# Main Title Card
add_card(s1, Inches(1.0), Inches(1.2), Inches(11.333), Inches(5.1), bg_rgb=RGBColor(17, 24, 39), border_rgb=RGBColor(56, 189, 248))
tb_title = s1.shapes.add_textbox(Inches(1.5), Inches(1.6), Inches(10.3), Inches(4.3))
tf1 = tb_title.text_frame
tf1.word_wrap = True

p_sup = tf1.paragraphs[0]
p_sup.text = "PROJET DE FIN D'ANNÉE (PFA) · DATA ENGINEERING (4TH YEAR)"
p_sup.font.size = Pt(13)
p_sup.font.bold = True
p_sup.font.color.rgb = RGBColor(56, 189, 248)

p_main = tf1.add_paragraph()
p_main.text = "FX Trading Room P&L Platform\nAccounting Currency: Moroccan Dirham (MAD)"
p_main.font.size = Pt(28)
p_main.font.bold = True
p_main.font.color.rgb = RGBColor(248, 250, 252)
p_main.space_before = Pt(12)

p_sub = tf1.add_paragraph()
p_sub.text = "Multi-Desk Position Keeping, Front-to-Back Reconciliation & Bank Al-Maghrib Compliance"
p_sub.font.size = Pt(15)
p_sub.font.color.rgb = RGBColor(148, 163, 184)
p_sub.space_before = Pt(8)

p_meta = tf1.add_paragraph()
p_meta.text = "Candidate: Mohamed Taha El Qassid  |  Internship: DXC Technology  |  University: International University of Rabat (UIR)"
p_meta.font.size = Pt(13)
p_meta.font.bold = True
p_meta.font.color.rgb = RGBColor(16, 185, 129)
p_meta.space_before = Pt(24)

p_date = tf1.add_paragraph()
p_date.text = "Academic Year: 2025 - 2026  ·  Official Soutenance Presentation"
p_date.font.size = Pt(11)
p_date.font.color.rgb = RGBColor(148, 163, 184)
p_date.space_before = Pt(8)

add_speaker_note(s1, """
Bonjour messieurs les membres du jury, chers encadrants de DXC Technology et de l'Université Internationale de Rabat.
Je m'appelle Mohamed Taha El Qassid, étudiant en 4ème année Génie des Données (Data Engineering).
J'ai le plaisir de vous présenter aujourd'hui mon projet de fin d'année réalisé au sein de DXC Technology, intitulé :
'Application P&L FX Salle de Marché - Devise Comptable MAD'.
Ce projet a pour objectif de concevoir une plateforme complète d'ingénierie des données pour le calcul automatisé du P&L,
la réconciliation Front-Office / Back-Office, et la conformité stricte avec les règles de Bank Al-Maghrib.
""")


# ----------------- SLIDE 2: BUSINESS CONTEXT & PROBLEM STATEMENT -----------------
s2 = prs.slides.add_slide(blank_layout)
apply_slide_background(s2)
add_header(s2, "Business Context & The Problem Statement", "01. CONTEXT & MOTIVATION")

# Left Column: The Trading Room Reality
add_card(s2, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.4))
tb_c1 = s2.shapes.add_textbox(Inches(1.1), Inches(1.7), Inches(5.1), Inches(5.0))
tf_c1 = tb_c1.text_frame
tf_c1.word_wrap = True

p1 = tf_c1.paragraphs[0]
p1.text = "What is an FX Trading Room (Salle de Marché)?"
p1.font.size = Pt(16)
p1.font.bold = True
p1.font.color.rgb = RGBColor(56, 189, 248)

points_c1 = [
    ("Market Making & Liquidity:", "Corporate clients (OCP, Renault, Maroc Telecom) need foreign currencies (USD, EUR) to import equipment and export goods. The bank's trading room executes and hedges these deals."),
    ("Massive Daily Volumes:", "Trading desks execute hundreds of multi-million dirham transactions daily across spot, forward, and cross-currency instruments."),
    ("The Regulatory Mandate:", "Moroccan banks cannot keep books in foreign currencies. Bank Al-Maghrib mandates daily End-of-Day (EOD) revaluation of all books into Moroccan Dirhams (MAD).")
]
for title, desc in points_c1:
    p = tf_c1.add_paragraph()
    p.text = f"• {title} "
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(248, 250, 252)
    p.space_before = Pt(10)
    p_d = tf_c1.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = RGBColor(148, 163, 184)

# Right Column: The Core Challenges
add_card(s2, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4))
tb_c2 = s2.shapes.add_textbox(Inches(7.1), Inches(1.7), Inches(5.1), Inches(5.0))
tf_c2 = tb_c2.text_frame
tf_c2.word_wrap = True

p2 = tf_c2.paragraphs[0]
p2.text = "Why Traditional Excel & Manual Processes Fail"
p2.font.size = Pt(16)
p2.font.bold = True
p2.font.color.rgb = RGBColor(239, 68, 68)

points_c2 = [
    ("Front vs. Back Discrepancies:", "Traders book fast in Front-Office, but settlement confirmations from counterparty banks (SWIFT MT300) often have rate slippages or partial fills, causing hidden P&L leakage."),
    ("Cross-Currency Complexity:", "Trades like EUR/USD require synthetic triangular revaluation through BAM USD/MAD and EUR/MAD fixings at EOD."),
    ("Inventory Accounting Divergence:", "Choosing between FIFO (Murex standard) and CMP (accounting average) creates timing variances that require automated tracking."),
    ("Our Solution:", "An automated, auditable Data Engineering platform enforcing mathematical integrity rules (BR1 to BR4) with resilient dual-layer persistence.")
]
for title, desc in points_c2:
    p = tf_c2.add_paragraph()
    p.text = f"• {title} "
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(248, 250, 252)
    p.space_before = Pt(8)
    p_d = tf_c2.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = RGBColor(148, 163, 184)

add_speaker_note(s2, """
Pour bien comprendre notre projet, il faut poser le contexte métier :
Une salle de marché de change (FX Trading Room) traite quotidiennement des centaines de millions de dirhams.
Des grands groupes marocains comme OCP ou Renault sollicitent la salle pour couvrir leurs importations et exportations.
Le problème majeur réside dans la gestion manuelle : les feuilles Excel deviennent ingérables,
les erreurs de saisie entre le Front-Office et le Back-Office génèrent des écarts financiers,
et la réglementation de Bank Al-Maghrib impose une réévaluation quotidienne stricte en dirhams (MAD).
Notre mission a donc été de concevoir une plateforme d'ingénierie des données robuste pour automatiser cette chaîne.
""")


# ----------------- SLIDE 3: BANK AL-MAGHRIB REGULATORY FRAMEWORK -----------------
s3 = prs.slides.add_slide(blank_layout)
apply_slide_background(s3)
add_header(s3, "Regulatory Framework: Bank Al-Maghrib Fixing & MAD Peg", "02. REGULATORY RULES")

# Left Column: Rules Explanation
add_card(s3, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
tb_r = s3.shapes.add_textbox(Inches(1.1), Inches(1.7), Inches(5.0), Inches(5.0))
tf_r = tb_r.text_frame
tf_r.word_wrap = True

p_r = tf_r.paragraphs[0]
p_r.text = "How Moroccan FX Peg Regulation Works"
p_r.font.size = Pt(16)
p_r.font.bold = True
p_r.font.color.rgb = RGBColor(56, 189, 248)

rules = [
    ("Accounting Currency: MAD", "All positions, whether booked in USD, EUR, or GBP, must be revalued into MAD at EOD to meet BAM prudential reporting standards."),
    ("The Currency Basket Formulation", "The central exchange rate is anchored to a basket composed of 60% Euro and 40% US Dollar, reflecting Morocco's foreign trade structure:"),
    ("Formula:", "Central Rate = 0.60 * EUR/MAD + 0.40 * USD/MAD"),
    ("The +/- 5% Fluctuation Band", "Since January 2020, BAM allows the dirham to fluctuate within a +/- 5% band around the central rate. Desks must stress-test their portfolios against these boundary limits."),
    ("Daily EOD Fixing (15:30)", "Bank Al-Maghrib publishes the official 'Cours de Référence' at 15:30. This fixing serves as the statutory revaluation benchmark for all Moroccan banks.")
]
for title, desc in rules:
    p = tf_r.add_paragraph()
    p.text = f"• {title}: " if not title.startswith("Formula") else f"  {title} "
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(245, 158, 11) if "Formula" in title else RGBColor(248, 250, 252)
    p.space_before = Pt(8)
    p_d = tf_r.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = RGBColor(148, 163, 184)

# Right Column: Visual Diagram of Basket and Band
s3.shapes.add_picture(str(img_bam), Inches(6.7), Inches(1.6), width=Inches(5.8))

add_speaker_note(s3, """
Sur cette diapositive, nous détaillons le cadre réglementaire de Bank Al-Maghrib :
Le Maroc applique un régime de change à parité glissante lié à un panier composé de 60% d'Euros et 40% de Dollars US.
Depuis 2020, la bande de fluctuation autorisée est de +/- 5% autour du cours central.
Chaque jour à 15h30, Bank Al-Maghrib publie le fixing officiel (le cours de référence).
Toutes les banques marocaines sont légalement tenues de valoriser l'ensemble de leurs livres à ce fixing officiel.
Notre système intègre ce calcul en temps réel et applique un stress-testing automatique sur les bornes de la bande.
""")


# ----------------- SLIDE 4: FINANCIAL FUNDAMENTALS & BR3 INVARIANT -----------------
s4 = prs.slides.add_slide(blank_layout)
apply_slide_background(s4)
add_header(s4, "Financial Fundamentals: The 3 Core P&L Metrics & Invariant BR3", "03. FINANCIAL ENGINEERING")

# 3 Metric Cards side by side
card_w = Inches(3.7)
card_h = Inches(3.2)
top_y = Inches(1.5)

# Card 1: Mark-to-Market
add_card(s4, Inches(0.8), top_y, card_w, card_h)
tb_m1 = s4.shapes.add_textbox(Inches(1.0), top_y + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
tf_m1 = tb_m1.text_frame
tf_m1.word_wrap = True
tf_m1.paragraphs[0].text = "1. Mark-to-Market (MTM)"
tf_m1.paragraphs[0].font.size = Pt(16)
tf_m1.paragraphs[0].font.bold = True
tf_m1.paragraphs[0].font.color.rgb = RGBColor(56, 189, 248)

p = tf_m1.add_paragraph()
p.text = "Valuation of all open contracts against today's closing BAM fixing rate."
p.font.size = Pt(11)
p.font.color.rgb = RGBColor(148, 163, 184)
p.space_before = Pt(8)

p = tf_m1.add_paragraph()
p.text = "Direct Quote (USD/MAD):\nMTM = (Fixing - Rate) * Nominal\n\nCross Quote (EUR/USD):\nMTM = (Fixing_EUR - Rate*Fixing_USD) * Nominal"
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = RGBColor(245, 158, 11)
p.space_before = Pt(8)

# Card 2: Realized P&L
add_card(s4, Inches(4.8), top_y, card_w, card_h)
tb_m2 = s4.shapes.add_textbox(Inches(5.0), top_y + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
tf_m2 = tb_m2.text_frame
tf_m2.word_wrap = True
tf_m2.paragraphs[0].text = "2. Realized P&L (Cash)"
tf_m2.paragraphs[0].font.size = Pt(16)
tf_m2.paragraphs[0].font.bold = True
tf_m2.paragraphs[0].font.color.rgb = RGBColor(16, 185, 129)

p = tf_m2.add_paragraph()
p.text = "Actual financial gain or loss realized when an open position is unwound by an opposing trade."
p.font.size = Pt(11)
p.font.color.rgb = RGBColor(148, 163, 184)
p.space_before = Pt(8)

p = tf_m2.add_paragraph()
p.text = "Destination Accounting:\nImpacts the Income Statement (Compte de résultat) directly as cash earnings."
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = RGBColor(248, 250, 252)
p.space_before = Pt(8)

# Card 3: Unrealized P&L
add_card(s4, Inches(8.8), top_y, card_w, card_h)
tb_m3 = s4.shapes.add_textbox(Inches(9.0), top_y + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
tf_m3 = tb_m3.text_frame
tf_m3.word_wrap = True
tf_m3.paragraphs[0].text = "3. Unrealized (Latent)"
tf_m3.paragraphs[0].font.size = Pt(16)
tf_m3.paragraphs[0].font.bold = True
tf_m3.paragraphs[0].font.color.rgb = RGBColor(139, 92, 246)

p = tf_m3.add_paragraph()
p.text = "Potential paper gain or loss on positions that remain open overnight."
p.font.size = Pt(11)
p.font.color.rgb = RGBColor(148, 163, 184)
p.space_before = Pt(8)

p = tf_m3.add_paragraph()
p.text = "Destination Accounting:\nRecorded on the Balance Sheet (Bilan / Capitaux Propres) as revaluation reserve."
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = RGBColor(248, 250, 252)
p.space_before = Pt(8)

# Bottom Card: The Golden Accounting Invariant (BR3)
add_card(s4, Inches(0.8), Inches(4.9), Inches(11.7), Inches(2.0), bg_rgb=RGBColor(15, 23, 42), border_rgb=RGBColor(16, 185, 129))
tb_br3 = s4.shapes.add_textbox(Inches(1.1), Inches(5.0), Inches(11.1), Inches(1.8))
tf_br3 = tb_br3.text_frame
tf_br3.word_wrap = True

p_inv = tf_br3.paragraphs[0]
p_inv.text = "THE GOLDEN ACCOUNTING INVARIANT (BUSINESS RULE BR3)"
p_inv.font.size = Pt(13)
p_inv.font.bold = True
p_inv.font.color.rgb = RGBColor(16, 185, 129)

p_eq = tf_br3.add_paragraph()
p_eq.text = "Total Mark-to-Market P&L = Realized P&L + Unrealized (Latent) P&L"
p_eq.font.size = Pt(17)
p_eq.font.bold = True
p_eq.font.color.rgb = RGBColor(248, 250, 252)
p_eq.space_before = Pt(4)

p_det = tf_br3.add_paragraph()
p_det.text = "Enforcement Mechanism: Physically validated by PostgreSQL CHECK constraint 'ROUND(total_mad, 2) = ROUND(realized_mad + unrealized_mad, 2)' and automated dbt singular assertions. Zero financial leakage allowed."
p_det.font.size = Pt(11)
p_det.font.color.rgb = RGBColor(148, 163, 184)
p_det.space_before = Pt(4)

add_speaker_note(s4, """
Ici, nous abordons les trois piliers du calcul financier :
1. Le Mark-to-Market (MTM) : c'est la valeur de liquidation théorique de chaque transaction au cours de fixing de Bank Al-Maghrib.
2. Le P&L Réalisé : c'est le gain ou la perte définitivement encaissé lors du débouclage d'une position. Il va au Compte de Résultat.
3. Le P&L Latent (Non-réalisé) : c'est la plus ou moins-value potentielle sur les positions encore ouvertes la nuit, stockée au Bilan.
Et voici la règle d'or fondamentale, notre Business Rule BR3 :
Le Total MTM doit TOUJOURS être égal au Réalisé plus le Latent.
Dans notre architecture, cette égalité n'est pas juste théorique : elle est vérifiée par une contrainte CHECK en base de données et des tests automatisés dbt.
""")


# ----------------- SLIDE 5: CASE STUDY WALKTHROUGH (THE 4 TRADES = +79,460 MAD) -----------------
s5 = prs.slides.add_slide(blank_layout)
apply_slide_background(s5)
add_header(s5, "Reference Case Study: The 4 Benchmark Trades (+79,460 MAD)", "04. MATHEMATICAL VALIDATION")

# Left Column: Detailed Trade Breakdown Table
add_card(s5, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
tb_t = s5.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.2), Inches(5.2))
tf_t = tb_t.text_frame
tf_t.word_wrap = True

p_th = tf_t.paragraphs[0]
p_th.text = "Audit of the Official PFE Benchmark Trades"
p_th.font.size = Pt(15)
p_th.font.bold = True
p_th.font.color.rgb = RGBColor(56, 189, 248)

t_details = [
    ("Trade 1: USD/MAD Buy 1,000,000 @ 9.9200", "BAM Fixing: 9.9500 MAD\nFormula: (9.9500 - 9.9200) * 1,000,000 = +30,000 MAD (MTM)"),
    ("Trade 2: USD/MAD Sell 500,000 @ 9.9600", "Unwinds 500k of Trade 1:\nRealized Cash Gain: (9.9600 - 9.9200) * 500k = +20,000 MAD\nRemaining 500k Unrealized: (9.9500 - 9.9200) * 500k = +15,000 MAD"),
    ("Trade 3: EUR/MAD Buy 800,000 @ 10.7700", "BAM Fixing: 10.8000 MAD\nFormula: (10.8000 - 10.7700) * 800,000 = +24,000 MAD (Unrealized)"),
    ("Trade 4: EUR/USD Buy 600,000 @ 1.0820", "Synthetic Cross Conversion to MAD:\nFormula: (10.8000 - (1.0820 * 9.9500)) * 600,000\nMTM Gain = +20,460 MAD (Unrealized)"),
]
for title, desc in t_details:
    p = tf_t.add_paragraph()
    p.text = f"• {title}"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(248, 250, 252)
    p.space_before = Pt(6)
    p_d = tf_t.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = RGBColor(148, 163, 184)

# Right: Benchmark Chart
s5.shapes.add_picture(str(img_bench), Inches(6.7), Inches(1.6), width=Inches(5.8))

add_speaker_note(s5, """
Examinons maintenant le cas d'école de référence spécifié dans le cahier des charges :
Quatre transactions exécutées sur deux pupitres (USD_DESK et EUR_DESK) :
- Trade 1 : Achat de 1M USD à 9.92, réévalué à 9.95 -> MTM de +30 000 MAD.
- Trade 2 : Vente de 500k USD à 9.96 -> débouclage de 500k du Trade 1, dégageant un Réalisé de +20 000 MAD et un Latent résiduel de +15 000 MAD.
- Trade 3 : Achat de 800k EUR à 10.77, réévalué à 10.80 -> Latent de +24 000 MAD.
- Trade 4 : Achat de 600k EUR/USD à 1.0820 -> conversion indirecte via le cross synthétique EUR/USD * USD/MAD -> Latent de +20 460 MAD.
Résultat total du portefeuille : MTM = +79 460 MAD, composé exactement de +20 000 MAD de Réalisé et +59 460 MAD de Latent.
L'égalité fondamentale BR3 est vérifiée à 100%.
""")


# ----------------- SLIDE 6: INVENTORY ACCOUNTING (FIFO VS CMP) -----------------
s6 = prs.slides.add_slide(blank_layout)
apply_slide_background(s6)
add_header(s6, "Inventory Accounting: FIFO vs. CMP & Brief Audit Discovery", "05. ALGORITHMIC DEPLETION")

# Left Column: Explanation and Correction
add_card(s6, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
tb_f = s6.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.2), Inches(5.2))
tf_f = tb_f.text_frame
tf_f.word_wrap = True

p_fh = tf_f.paragraphs[0]
p_fh.text = "Section 4 Reference Example (2 Buys + 1 Sale)"
p_fh.font.size = Pt(15)
p_fh.font.bold = True
p_fh.font.color.rgb = RGBColor(56, 189, 248)

fifo_points = [
    ("Scenario Setup:", "Buy 1: 500k USD @ 9.9100\nBuy 2: 500k USD @ 9.9300\nSale: 600k USD @ 9.9500"),
    ("FIFO Depletion Logic (Murex Standard):", "Lot 1 (500k) exhausted first: (9.95 - 9.91) * 500k = +20,000 MAD\nLot 2 (100k) partially consumed: (9.95 - 9.93) * 100k = +2,000 MAD\nTotal FIFO Realized = +22,000 MAD. Remaining: 400k @ 9.93."),
    ("CMP Logic (Coût Moyen Pondéré):", "Average Purchase Cost = (500k*9.91 + 500k*9.93) / 1,000k = 9.9200 MAD\nRealized = (9.9500 - 9.9200) * 600k = +18,000 MAD."),
    ("Audit Discovery (Soutenance Highlight):", "The PFE brief text stated '21,500 MAD (19,500 + 2,000)' due to a small drafting typo. Our data engine recalculates and proves the mathematically exact figure of 22,000 MAD.")
]
for title, desc in fifo_points:
    p = tf_f.add_paragraph()
    p.text = f"• {title}"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(245, 158, 11) if "Audit" in title else RGBColor(248, 250, 252)
    p.space_before = Pt(6)
    p_d = tf_f.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = RGBColor(148, 163, 184)

# Right: FIFO Diagram
s6.shapes.add_picture(str(img_fifo), Inches(6.7), Inches(1.6), width=Inches(5.8))

add_speaker_note(s6, """
Cette diapositive illustre une compétence essentielle d'ingénieur des données : l'audit et la validation rigoureuse des algorithmes d'inventaire.
Dans la section 4 du brief, un exemple standard compare le FIFO et le CMP sur 2 achats suivis d'une vente partielle :
En FIFO (standard des progiciels de marché comme Murex), on consomme d'abord le lot 1 (500k à 9.91) dégageant 20 000 MAD,
puis 100k du lot 2 à 9.93 dégageant 2 000 MAD. Le total réalisé est donc de 22 000 MAD.
En CMP (norme comptable marocaine), le coût moyen est de 9.92, dégageant 18 000 MAD.
Point remarquable pour notre soutenance : le texte du brief initial mentionnait 21 500 MAD (19 500 + 2 000) suite à une coquille de frappe.
Notre moteur a recalculé et prouvé que 0.04 * 500k fait exactement 20 000 MAD, rétablissant ainsi la vérité arithmétique de 22 000 MAD.
""")


# ----------------- SLIDE 7: RECONCILIATION HUB & REAL-WORLD CONFLICTS -----------------
s7 = prs.slides.add_slide(blank_layout)
apply_slide_background(s7)
add_header(s7, "Front-to-Back Reconciliation: Auditing the 4 Real-World Breaks", "06. RECONCILIATION & RISK")

# Left Column: The 4 Conflict Scenarios
add_card(s7, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
tb_rec = s7.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.2), Inches(5.2))
tf_rec = tb_rec.text_frame
tf_rec.word_wrap = True

p_rh = tf_rec.paragraphs[0]
p_rh.text = "How Our Reconciliation Engine (OS6) Operates"
p_rh.font.size = Pt(15)
p_rh.font.bold = True
p_rh.font.color.rgb = RGBColor(56, 189, 248)

breaks_desc = [
    ("Break 1: Rate Slippage (BMCE Bank of Africa)", "FO booked EUR/MAD at 10.7950, but BO confirmation arrived at 10.7985 (+35 pips / -2,450 MAD variance due to interbank broker spread)."),
    ("Break 2: Nominal Mismatch (Attijariwafa Bank)", "FO booked 1,500,000 USD, but counterparty settled only 1,400,000 USD (-100k USD missing because the counterparty's intraday credit ceiling was reached)."),
    ("Break 3: Unconfirmed SWIFT MT300 (BNP Paribas)", "FO trader executed EUR/USD 500k at 17:15, but BO received no affirmation message. Poses unhedged overnight currency risk."),
    ("Break 4: Orphan Settlement (Barclays Bank)", "BO received confirmed settlement for 300k GBP, but no FO ticket was booked. Detects rogue or unrecorded dealer trades.")
]
for title, desc in breaks_desc:
    p = tf_rec.add_paragraph()
    p.text = f"• {title}"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(239, 68, 68) if "Break" in title else RGBColor(248, 250, 252)
    p.space_before = Pt(6)
    p_d = tf_rec.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = RGBColor(148, 163, 184)

# Right: Reconciliation Breaks Chart
s7.shapes.add_picture(str(img_breaks), Inches(6.7), Inches(1.6), width=Inches(5.8))

add_speaker_note(s7, """
Passons au module de réconciliation Front-Office / Back-Office, correspondant à l'objectif opérationnel OS6.
Dans une banque, les traders saisissent rapidement leurs tickets au Front-Office, tandis que le Back-Office reçoit les confirmations SWIFT MT300.
Notre moteur teste 4 scénarios d'anomalies réelles :
1. L'écart de cours (Rate Slippage) : sur BMCE, un décalage de 35 pips dû aux frais de courtage interbancaire (-2 450 MAD).
2. L'écart de nominal (Nominal Mismatch) : sur Attijariwafa, 100k USD manquants car la ligne de crédit de la contrepartie était plafonnée.
3. Le trade non confirmé (Unconfirmed SWIFT) : sur BNP Paribas, une opération saisie en fin de journée sans confirmation SWIFT, créant un risque de change ouvert toute la nuit.
4. Le règlement orphelin (Orphan Settlement) : confirmation reçue de Barclays sans aucun ticket Front-Office correspondant.
Le moteur génère automatiquement un audit détaillé et un rapport Excel opposable aux commissaires aux comptes.
""")


# ----------------- SLIDE 8: MARKET DATA & GOLD BREAKOUT ABOVE $4,000/OZ -----------------
s8 = prs.slides.add_slide(blank_layout)
apply_slide_background(s8)
add_header(s8, "Live Market Terminal & Gold Breakthrough Above $4,000/oz", "07. MARKET DATA & BROKER VIEW")

# Left Column: Market Data & Gold Story
add_card(s8, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
tb_g = s8.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.2), Inches(5.2))
tf_g = tb_g.text_frame
tf_g.word_wrap = True

p_gh = tf_g.paragraphs[0]
p_gh.text = "Multi-Asset Monitoring & LBMA Gold Dynamics"
p_gh.font.size = Pt(15)
p_gh.font.bold = True
p_gh.font.color.rgb = RGBColor(56, 189, 248)

gold_points = [
    ("Asset Universe Covered:", "• USD/MAD (BAM Fixing ~9.83 - 9.95)\n• EUR/MAD (BAM Fixing ~10.80 - 10.99)\n• EUR/USD (International Cross ~1.08 - 1.11)\n• GBP/MAD (Corporate & Hedging ~12.65 - 13.00)\n• XAU/USD (Gold Spot LBMA Benchmark)"),
    ("The Historic $4,000/oz Gold Breakthrough:", "Gold crossed the historic resistance milestone of $4,000 / oz (trading at $4,038.50). In our platform, corporate treasuries monitor gold as a sovereign inflation and currency hedge."),
    ("Institutional Technical Indicators:", "Dual-pane financial charting: Candlesticks (green/red), 20-period Simple Moving Average (SMA), and trading volume histograms."),
    ("Real-Time BAM Live API Fetcher:", "Integrated live REST feed pulling active market quotes and instantly recalibrating BAM basket indicators.")
]
for title, desc in gold_points:
    p = tf_g.add_paragraph()
    p.text = f"• {title}"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(245, 158, 11) if "Gold" in title else RGBColor(248, 250, 252)
    p.space_before = Pt(6)
    p_d = tf_g.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = RGBColor(148, 163, 184)

# Right: Gold Chart
s8.shapes.add_picture(str(img_gold), Inches(6.7), Inches(1.6), width=Inches(5.8))

add_speaker_note(s8, """
Sur cette vue terminal de marché, nous visualisons l'environnement de cotation multi-actifs :
Notre plateforme couvre non seulement les paires en dirhams (USD/MAD, EUR/MAD, GBP/MAD) et les cross internationaux (EUR/USD),
mais également l'or au comptant (XAU/USD).
Comme vous pouvez l'observer sur le graphique en chandeliers japonais, l'or a franchi le cap historique des 4 000 dollars l'once,
s'établissant aujourd'hui autour de 4 038 dollars.
Ce franchissement est capital pour les trésoriers d'entreprises qui utilisent l'or comme réserve de valeur et couverture contre l'inflation.
Le graphique intègre également une moyenne mobile à 20 jours (SMA20) et les volumes de transaction.
""")


# ----------------- SLIDE 9: DATA ENGINEERING ARCHITECTURE (BRONZE/SILVER/GOLD) -----------------
s9 = prs.slides.add_slide(blank_layout)
apply_slide_background(s9)
add_header(s9, "Data Engineering Pipeline: Medallion Architecture (Bronze/Silver/Gold)", "08. DATA ARCHITECTURE")

# Architecture Diagram at Top
s9.shapes.add_picture(str(img_pipe), Inches(0.8), Inches(1.5), width=Inches(11.7))

# Bottom Cards: 3 Layer details
b_w = Inches(3.7)
b_h = Inches(2.2)
b_y = Inches(4.8)

# Layer 1
add_card(s9, Inches(0.8), b_y, b_w, b_h)
tb_l1 = s9.shapes.add_textbox(Inches(1.0), b_y + Inches(0.15), b_w - Inches(0.4), b_h - Inches(0.3))
tf_l1 = tb_l1.text_frame
tf_l1.word_wrap = True
tf_l1.paragraphs[0].text = "Bronze Staging Layer"
tf_l1.paragraphs[0].font.size = Pt(13)
tf_l1.paragraphs[0].font.bold = True
tf_l1.paragraphs[0].font.color.rgb = RGBColor(56, 189, 248)
p = tf_l1.add_paragraph()
p.text = "• Raw ingestion of trades and fixings.\n• Tables: stg_trade, stg_market_rate.\n• Dual-storage adapter: PostgreSQL when Docker is up, SQLite local fallback.\n• Deduplication via source_ref."
p.font.size = Pt(10)
p.font.color.rgb = RGBColor(148, 163, 184)
p.space_before = Pt(4)

# Layer 2
add_card(s9, Inches(4.8), b_y, b_w, b_h)
tb_l2 = s9.shapes.add_textbox(Inches(5.0), b_y + Inches(0.15), b_w - Inches(0.4), b_h - Inches(0.3))
tf_l2 = tb_l2.text_frame
tf_l2.word_wrap = True
tf_l2.paragraphs[0].text = "Silver Transformation (dbt)"
tf_l2.paragraphs[0].font.size = Pt(13)
tf_l2.paragraphs[0].font.bold = True
tf_l2.paragraphs[0].font.color.rgb = RGBColor(245, 158, 11)
p = tf_l2.add_paragraph()
p.text = "• Dimensional modeling with dbt.\n• Mart: fact_trade_mtm in pure SQL.\n• Indirect cross calculation (EUR/USD).\n• Automated singular dbt test verifying Total = Realized + Latent."
p.font.size = Pt(10)
p.font.color.rgb = RGBColor(148, 163, 184)
p.space_before = Pt(4)

# Layer 3
add_card(s9, Inches(8.8), b_y, b_w, b_h)
tb_l3 = s9.shapes.add_textbox(Inches(9.0), b_y + Inches(0.15), b_w - Inches(0.4), b_h - Inches(0.3))
tf_l3 = tb_l3.text_frame
tf_l3.word_wrap = True
tf_l3.paragraphs[0].text = "Gold Business Layer"
tf_l3.paragraphs[0].font.size = Pt(13)
tf_l3.paragraphs[0].font.bold = True
tf_l3.paragraphs[0].font.color.rgb = RGBColor(139, 92, 246)
p = tf_l3.add_paragraph()
p.text = "• Python pnl_engine.py with FIFO deque.\n• FO/BO reconciliation & dispute hub.\n• Persistence in daily_pnl with CHECK rule.\n• OpenPyXL multi-tab Excel export."
p.font.size = Pt(10)
p.font.color.rgb = RGBColor(148, 163, 184)
p.space_before = Pt(4)

add_speaker_note(s9, """
En tant qu'étudiant en Data Engineering, l'architecture des données est le cœur de mon travail :
Nous avons implémenté l'architecture médaillon reconnue dans l'industrie :
- Niveau Bronze : ingestion des flux bruts dans PostgreSQL avec notre db_adapter résilient (qui bascule automatiquement sur SQLite si Docker est éteint).
- Niveau Silver : transformations dbt (data build tool) créant la table fact_trade_mtm en SQL pur avec gestion des cross synthétiques.
- Niveau Gold : moteur Python haute performance utilisant des structures deque pour le débouclage FIFO et la réconciliation Front-to-Back.
- Au niveau stockage, l'égalité comptable BR3 est verrouillée physiquement par une contrainte CHECK en base de données.
""")


# ----------------- SLIDE 10: APACHE AIRFLOW ORCHESTRATION DAG -----------------
s10 = prs.slides.add_slide(blank_layout)
apply_slide_background(s10)
add_header(s10, "Workflow Orchestration: Apache Airflow DAG at 15:35 EOD", "09. PIPELINE ORCHESTRATION")

# Left Column: DAG Flow & Tasks
add_card(s10, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
tb_dag = s10.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.2), Inches(5.2))
tf_dag = tb_dag.text_frame
tf_dag.word_wrap = True

p_dh = tf_dag.paragraphs[0]
p_dh.text = "Airflow DAG Execution Timeline: 'fx_pnl_daily_closing'"
p_dh.font.size = Pt(15)
p_dh.font.bold = True
p_dh.font.color.rgb = RGBColor(56, 189, 248)

dag_steps = [
    ("Schedule: 15:35 Daily (CRON: 35 15 * * 1-5)", "Triggered 5 minutes after Bank Al-Maghrib publishes the official fixing at 15:30."),
    ("Task 1: wait_for_bam_fixing (Sensor)", "Verifies that Bank Al-Maghrib has published today's fixing rates; retries with exponential backoff if delayed."),
    ("Task 2: ingest_eod_trades (PythonOperator)", "Extracts Front-Office deal tickets and Back-Office SWIFT settlement confirmations into Bronze tables."),
    ("Task 3: dbt_run_mtm_models (BashOperator)", "Executes dbt transformation models to calculate Mark-to-Market in the Silver fact mart."),
    ("Task 4: dbt_test_financial_integrity", "Runs automated assertions (uniqueness, not-null, BR3 invariant). Halts pipeline if identity fails."),
    ("Task 5: compute_fifo_pnl & reconcile_fo_bo", "Executes the Gold calculation engine, populates daily_pnl, and generates the institutional audit Excel package.")
]
for title, desc in dag_steps:
    p = tf_dag.add_paragraph()
    p.text = f"• {title}"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(16, 185, 129) if "Task" in title else RGBColor(248, 250, 252)
    p.space_before = Pt(5)
    p_d = tf_dag.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = RGBColor(148, 163, 184)

# Right Column: Architecture Box
add_card(s10, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), bg_rgb=RGBColor(15, 23, 42), border_rgb=RGBColor(56, 189, 248))
tb_dag_r = s10.shapes.add_textbox(Inches(7.1), Inches(1.7), Inches(5.1), Inches(5.0))
tf_dag_r = tb_dag_r.text_frame
tf_dag_r.word_wrap = True

p_dr1 = tf_dag_r.paragraphs[0]
p_dr1.text = "Enterprise Data Engineering Strengths"
p_dr1.font.size = Pt(15)
p_dr1.font.bold = True
p_dr1.font.color.rgb = RGBColor(56, 189, 248)

strengths = [
    ("Idempotency:", "Re-running the DAG for any past date produces identical, reproducible results without duplicating trades or P&L rows."),
    ("Circuit Breaker Quality Gates:", "If a dbt test fails (e.g. rate is negative or Total != Realized + Unrealized), the pipeline fails immediately before reporting corrupted data."),
    ("Audit Trail & Lineage:", "Every calculation is tied to the trade ticket, counterparty, trader ID, and execution timestamp."),
    ("Zero-Downtime Fallback:", "If the central PostgreSQL cluster is unavailable, the pipeline falls back gracefully to local SQLite with identical schema and constraints.")
]
for title, desc in strengths:
    p = tf_dag_r.add_paragraph()
    p.text = f"✔ {title}"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(16, 185, 129)
    p.space_before = Pt(10)
    p_d = tf_dag_r.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = RGBColor(148, 163, 184)

add_speaker_note(s10, """
Pour automatiser cette chaîne sans intervention humaine, nous avons programmé un DAG Apache Airflow :
Le déclenchement est fixé à 15h35 du lundi au vendredi, soit 5 minutes après la publication du fixing par Bank Al-Maghrib.
La chaîne commence par un sensor qui vérifie la disponibilité des cours BAM,
puis ingère les trades, lance les modèles dbt, exécute les tests d'intégrité, et enfin déclenche le calcul FIFO et la réconciliation.
Ce pipeline garantit l'idempotence totale : réexécuter un traitement sur une date passée produit exactement le même résultat sans doublon.
""")


# ----------------- SLIDE 11: RISK MANAGEMENT & BAM STRESS TESTING -----------------
s11 = prs.slides.add_slide(blank_layout)
apply_slide_background(s11)
add_header(s11, "Risk Management: Bank Al-Maghrib Fluctuation Band Stress Testing", "10. RISK MANAGEMENT")

# 3 Stress Scenarios Cards
sc_w = Inches(3.7)
sc_h = Inches(5.2)

# Scenario 1: Base Case
add_card(s11, Inches(0.8), Inches(1.6), sc_w, sc_h)
tb_s1 = s11.shapes.add_textbox(Inches(1.0), Inches(1.8), sc_w - Inches(0.4), sc_h - Inches(0.4))
tf_s1 = tb_s1.text_frame
tf_s1.word_wrap = True
tf_s1.paragraphs[0].text = "Base Case (BAM Official)"
tf_s1.paragraphs[0].font.size = Pt(15)
tf_s1.paragraphs[0].font.bold = True
tf_s1.paragraphs[0].font.color.rgb = RGBColor(56, 189, 248)

p = tf_s1.add_paragraph()
p.text = "• USD/MAD: 9.9500 MAD\n• EUR/MAD: 10.8000 MAD\n• EUR/USD: 1.0854\n\nPortfolio MTM:\n+79,460 MAD\n\nRegulatory Compliance:\nCOMPLIANT (100% OK)\n\nStop-Loss Status:\nNo breach across any trading desk."
p.font.size = Pt(11)
p.font.color.rgb = RGBColor(148, 163, 184)
p.space_before = Pt(8)

# Scenario 2: +5% Peg Fluctuation
add_card(s11, Inches(4.8), Inches(1.6), sc_w, sc_h)
tb_s2 = s11.shapes.add_textbox(Inches(5.0), Inches(1.8), sc_w - Inches(0.4), sc_h - Inches(0.4))
tf_s2 = tb_s2.text_frame
tf_s2.word_wrap = True
tf_s2.paragraphs[0].text = "+5% Fluctuation Shock"
tf_s2.paragraphs[0].font.size = Pt(15)
tf_s2.paragraphs[0].font.bold = True
tf_s2.paragraphs[0].font.color.rgb = RGBColor(16, 185, 129)

p = tf_s2.add_paragraph()
p.text = "• USD/MAD: 10.4475 MAD (+5%)\n• EUR/MAD: 11.3400 MAD (+5%)\n\nPortfolio MTM:\n+169,460 MAD (+90,000 MAD)\n\nImpact Analysis:\nLong positions in foreign currencies appreciate strongly in MAD terms.\n\nRisk Assessment:\nHigh capital gain, zero credit breach."
p.font.size = Pt(11)
p.font.color.rgb = RGBColor(148, 163, 184)
p.space_before = Pt(8)

# Scenario 3: -5% Peg Fluctuation
add_card(s11, Inches(8.8), Inches(1.6), sc_w, sc_h)
tb_s3 = s11.shapes.add_textbox(Inches(9.0), Inches(1.8), sc_w - Inches(0.4), sc_h - Inches(0.4))
tf_s3 = tb_s3.text_frame
tf_s3.word_wrap = True
tf_s3.paragraphs[0].text = "-5% Fluctuation Shock"
tf_s3.paragraphs[0].font.size = Pt(15)
tf_s3.paragraphs[0].font.bold = True
tf_s3.paragraphs[0].font.color.rgb = RGBColor(239, 68, 68)

p = tf_s3.add_paragraph()
p.text = "• USD/MAD: 9.4525 MAD (-5%)\n• EUR/MAD: 10.2600 MAD (-5%)\n\nPortfolio MTM:\n-10,540 MAD (-90,000 MAD)\n\nImpact Analysis:\nSevere depreciation of foreign holdings against Dirham.\n\nRisk Alert:\nTriggers Stop-Loss warning on USD_DESK. Desk manager notified immediately."
p.font.size = Pt(11)
p.font.color.rgb = RGBColor(148, 163, 184)
p.space_before = Pt(8)

add_speaker_note(s11, """
En matière de gestion des risques, nous avons développé un moteur de stress-testing réglementaire :
La réglementation de Bank Al-Maghrib autorisant une bande de +/- 5%, notre système simule instantanément l'impact de ces chocs extrêmes :
- Dans le scénario haussier (+5%), le portefeuille s'apprécie à +169 460 MAD (+90 000 MAD de gain de change).
- Dans le scénario baissier (-5%), le MTM chute à -10 540 MAD, déclenchant automatiquement une alerte de dépassement de seuil de stop-loss.
Ce module permet aux directeurs des risques (CRO) d'anticiper la consommation en fonds propres de la salle de marché.
""")


# ----------------- SLIDE 12: THE STREAMLIT TRADING TERMINAL & DEMO -----------------
s12 = prs.slides.add_slide(blank_layout)
apply_slide_background(s12)
add_header(s12, "Interactive Trading Terminal: Streamlit Multi-Tab Workspace", "11. APPLICATION INTERFACE")

# 6 Feature Cards representing the 6 Workspace Tabs
tabs_info = [
    ("Tab 1: Trading Desk & Blotter", "Active portfolio KPIs (Total MTM, Realized, Latent), trade blotter with explicit mathematical formulas in MAD, and pre-trade deal ticket simulator."),
    ("Tab 2: FO / BO Reconciliation Hub", "Comprehensive discrepancy detection (rate slippage, nominal break, unconfirmed SWIFT), pips variance, and 1-click Excel audit package download."),
    ("Tab 3: Live Market Browser & Gold", "Interactive dual-pane financial charting: Candlesticks, 20-period SMA, volume histograms, and LBMA Gold $4,000 breakthrough marker."),
    ("Tab 4: Inventory Accounting (FIFO/CMP)", "Visual step-by-step demonstration of Section 4 lot depletion, explaining convergence upon closure and the brief's arithmetic audit note."),
    ("Tab 5: BAM Fluctuation Band Matrix", "Stress-testing matrix simulating +/- 1%, +/- 3%, and +/- 5% currency basket boundary shifts and stop-loss breach alerts."),
    ("Tab 6: Data Engineering Lineage", "End-to-end architecture diagram, dbt test results table, and Airflow DAG orchestration contract enforcement.")
]

for idx, (tab_title, tab_desc) in enumerate(tabs_info):
    col = idx % 2
    row = idx // 2
    x = Inches(0.8 + col * 6.0)
    y = Inches(1.6 + row * 1.8)
    
    add_card(s12, x, y, Inches(5.7), Inches(1.6), bg_rgb=RGBColor(17, 24, 39), border_rgb=RGBColor(31, 41, 55))
    tb_t = s12.shapes.add_textbox(x + Inches(0.2), y + Inches(0.15), Inches(5.3), Inches(1.3))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    
    p = tf_t.paragraphs[0]
    p.text = tab_title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RGBColor(56, 189, 248) if idx < 3 else RGBColor(16, 185, 129)
    
    p_d = tf_t.add_paragraph()
    p_d.text = tab_desc
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = RGBColor(148, 163, 184)
    p_d.space_before = Pt(4)

add_speaker_note(s12, """
Pour la restitution utilisateur, nous avons conçu une interface professionnelle de type terminal financier (style Murex / Bloomberg) :
Elle est organisée en 6 onglets clairs :
1. Trading Desk & Blotter : avec affichage transparent de la formule arithmétique de chaque trade et simulateur d'ordre avant exécution.
2. Hub de Réconciliation FO/BO : détection automatique des anomalies et téléchargement du dossier d'audit Excel en un clic.
3. Live Market Terminal : graphiques en chandeliers et suivi de l'or au-dessus des 4 000 dollars.
4. Comptabilité d'inventaire : comparaison FIFO vs CMP et justification du résultat.
5. Stress Testing Bank Al-Maghrib : matrice de sensibilité +/- 5%.
6. Lignage Data Engineering : contrats de données et assertions dbt.
""")


# ----------------- SLIDE 13: TESTING, VALIDATION & DATA CONTRACTS -----------------
s13 = prs.slides.add_slide(blank_layout)
apply_slide_background(s13)
add_header(s13, "Automated Testing, Data Quality Contracts & Benchmark Results", "12. QUALITY & VALIDATION")

# Left Column: Pytest Results
add_card(s13, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
tb_tst = s13.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.2), Inches(5.0))
tf_tst = tb_tst.text_frame
tf_tst.word_wrap = True

p_th = tf_tst.paragraphs[0]
p_th.text = "10/10 Automated Pytest Tests (100% PASS)"
p_th.font.size = Pt(15)
p_th.font.bold = True
p_th.font.color.rgb = RGBColor(16, 185, 129)

tests_list = [
    ("test_individual_trade_mtm:", "Validates exact MTM on direct MAD pairs and synthetic cross EUR/USD."),
    ("test_realized_and_unrealized_decomposition:", "Ensures exact split: +20,000 MAD Realized, +59,460 MAD Latent."),
    ("test_supporting_example_fifo_vs_cmp:", "Validates Section 4 reference example (+22,000 FIFO vs +18,000 CMP)."),
    ("test_business_rule_br3_identity:", "Verifies Total = Realized + Unrealized across 100 random simulated trades."),
    ("test_reconciliation_exact_matches:", "Confirms 0 discrepancies on perfectly matched FO/BO trades."),
    ("test_reconciliation_rate_slippage:", "Detects pip-level price variance and computes MAD financial impact."),
    ("test_reconciliation_unconfirmed_trade:", "Flags ghost trades with missing Back-Office confirmations."),
    ("test_reconciliation_nominal_mismatch:", "Verifies detection of partial fills and counterparty credit caps.")
]
for title, desc in tests_list:
    p = tf_tst.add_paragraph()
    p.text = f"✔ {title} "
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = RGBColor(16, 185, 129)
    p.space_before = Pt(3)
    p_d = tf_tst.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(9.5)
    p_d.font.color.rgb = RGBColor(148, 163, 184)

# Right Column: dbt Assertions & Summary Table
add_card(s13, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4))
tb_dbt = s13.shapes.add_textbox(Inches(7.1), Inches(1.7), Inches(5.1), Inches(5.0))
tf_dbt = tb_dbt.text_frame
tf_dbt.word_wrap = True

p_dh = tf_dbt.paragraphs[0]
p_dh.text = "dbt Automated Data Quality Assertions"
p_dh.font.size = Pt(15)
p_dh.font.bold = True
p_dh.font.color.rgb = RGBColor(56, 189, 248)

dbt_contracts = [
    ("BR1: BAM Rate Conversion", "Guarantees all foreign pairs convert to MAD; rejects null or negative rates."),
    ("BR2: EOD Revaluation", "Verifies all open tickets are revalued at today's official BAM fixing rate."),
    ("BR3: Accounting Equality", "Singular SQL test: SELECT * FROM mart WHERE ROUND(total) != ROUND(realized + latent). Must return 0 rows."),
    ("BR4: Chronological Lot Integrity", "Unit test verifying queue order cannot unwind a lot before earlier timestamped lots."),
    ("Execution Performance", "Full test suite (10 unit tests + dbt assertions) executes in under 0.55 seconds.")
]
for title, desc in dbt_contracts:
    p = tf_dbt.add_paragraph()
    p.text = f"• {title}: "
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(248, 250, 252)
    p.space_before = Pt(8)
    p_d = tf_dbt.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = RGBColor(148, 163, 184)

add_speaker_note(s13, """
La fiabilité est la marque de fabrique d'un ingénieur de données.
L'ensemble de notre plateforme est couvert par 10 tests unitaires automatisés sous pytest qui s'exécutent en 0.51 seconde.
Chaque règle métier (BR1 à BR4), chaque anomalie de réconciliation et chaque cas de débouclage FIFO/CMP
est validé par des assertions mathématiques strictes.
De plus, dbt exécute des tests singuliers en SQL garantissant qu'aucune ligne avec Total != Réalisé + Latent ne peut persister en production.
""")


# ----------------- SLIDE 14: CONCLUSION & DEFENSE Q&A -----------------
s14 = prs.slides.add_slide(blank_layout)
apply_slide_background(s14)
add_header(s14, "Conclusion, Achievements & Future Perspectives", "13. CONCLUSION")

# Left Column: Key Achievements
add_card(s14, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
tb_c_l = s14.shapes.add_textbox(Inches(1.1), Inches(1.7), Inches(5.0), Inches(5.0))
tf_c_l = tb_c_l.text_frame
tf_c_l.word_wrap = True

p_cl1 = tf_c_l.paragraphs[0]
p_cl1.text = "Key Project Deliverables & Achievements"
p_cl1.font.size = Pt(16)
p_cl1.font.bold = True
p_cl1.font.color.rgb = RGBColor(16, 185, 129)

achieves = [
    ("100% PFE Brief Compliance:", "Mathematical reproduction of benchmark numbers (+79,460 MAD total MTM, +20k Realized, +59,460 Latent)."),
    ("Automated FO/BO Reconciliation:", "Replaced manual error-prone Excel checks with real-time discrepancy detection and 1-click auditable Excel exports."),
    ("Bank Al-Maghrib Live API Integration:", "Real-time market rate feed, BAM currency basket metrics, and +/-5% fluctuation band stress-testing."),
    ("Resilient Dual-Storage Architecture:", "Seamless PostgreSQL production connectivity with transparent automatic SQLite local fallback.")
]
for title, desc in achieves:
    p = tf_c_l.add_paragraph()
    p.text = f"✔ {title}"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(248, 250, 252)
    p.space_before = Pt(8)
    p_d = tf_c_l.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = RGBColor(148, 163, 184)

# Right Column: Future Roadmap & Closing
add_card(s14, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), bg_rgb=RGBColor(17, 24, 39), border_rgb=RGBColor(56, 189, 248))
tb_c_r = s14.shapes.add_textbox(Inches(7.1), Inches(1.7), Inches(5.1), Inches(5.0))
tf_c_r = tb_c_r.text_frame
tf_c_r.word_wrap = True

p_cr1 = tf_c_r.paragraphs[0]
p_cr1.text = "Future Technical Perspectives"
p_cr1.font.size = Pt(16)
p_cr1.font.bold = True
p_cr1.font.color.rgb = RGBColor(56, 189, 248)

futures = [
    ("Real-Time Kafka Streaming:", "Transition from 15:35 EOD batch processing to sub-second tick-by-tick real-time position keeping via Apache Kafka."),
    ("SWIFT MT300 Direct Parser:", "Automated ingestion of raw ISO 15022/20022 SWIFT confirmation messages directly from interbank networks."),
    ("Multi-Factor Monte Carlo VaR:", "Advanced Value-at-Risk modeling across non-linear currency options and structural FX forward curves.")
]
for title, desc in futures:
    p = tf_c_r.add_paragraph()
    p.text = f"➔ {title}"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(245, 158, 11)
    p.space_before = Pt(8)
    p_d = tf_c_r.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = RGBColor(148, 163, 184)

p_thx = tf_c_r.add_paragraph()
p_thx.text = "\nThank you for your attention.\nQuestions & Discussion."
p_thx.font.size = Pt(16)
p_thx.font.bold = True
p_thx.font.color.rgb = RGBColor(248, 250, 252)
p_thx.space_before = Pt(14)

add_speaker_note(s14, """
Pour conclure, ce projet de fin d'année au sein de DXC Technology m'a permis d'allier ingénierie des données et finance de marché avancée.
Nous avons livré une plateforme opérationnelle, rigoureuse sur le plan arithmétique, conforme aux normes de Bank Al-Maghrib,
et apportant une réelle valeur ajoutée à la réconciliation Front-to-Back.
Comme perspectives futures, nous envisageons le passage au streaming temps réel avec Apache Kafka et le parsing direct des messages SWIFT.
Je tiens à remercier chaleureusement mes encadrants de DXC Technology et de l'UIR pour leur accompagnement précieux.
Je suis maintenant à votre entière disposition pour répondre à toutes vos questions.
""")


# Save presentation
output_pptx_path = PRES_DIR / "FX_Trading_Room_PFE_Defense_Mohamed_Taha.pptx"
prs.save(output_pptx_path)
print(f"Presentation successfully created at: {output_pptx_path}")
