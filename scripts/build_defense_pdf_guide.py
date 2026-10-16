"""
Generates an Executive PDF Defense Guide for Mohamed Taha El Qassid's PFE Project.
Topic: Application P&L FX Salle de Marché — Devise Comptable MAD (DXC Technology / UIR).
"""
import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# ----------------- Numbered Canvas for "Page X of Y" -----------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "DXC Technology / UIR — FX Trading Room P&L Engine (MAD Base Currency)")
            self.drawRightString(612 - 54, 750, "Mohamed Taha El Qassid — PFE Defense Guide")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 612 - 54, 742)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)
        self.drawString(54, 32, "Confidential — Prepared for PFE Graduation Defense | Track: Data Engineering (4th Year)")
        self.drawRightString(612 - 54, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    C_NAVY = colors.HexColor("#0A192F")
    C_BLUE = colors.HexColor("#1E3A8A")
    C_TEXT = colors.HexColor("#1E293B")
    C_MUTED = colors.HexColor("#64748B")
    C_BG_BOX = colors.HexColor("#F8FAFC")
    C_BORDER = colors.HexColor("#CBD5E1")
    C_GREEN = colors.HexColor("#059669")

    # Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=C_NAVY,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=C_BLUE,
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        "SectionH1",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=C_NAVY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        "SectionH2",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=C_BLUE,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        "BodyDark",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=C_TEXT,
        spaceAfter=6
    )
    body_bold = ParagraphStyle(
        "BodyDarkBold",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=C_TEXT,
        spaceAfter=4
    )
    bullet_style = ParagraphStyle(
        "BulletDark",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=C_TEXT,
        leftIndent=12,
        spaceAfter=3
    )
    code_style = ParagraphStyle(
        "CodeText",
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )
    table_cell = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=C_TEXT
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=C_NAVY
    )
    table_head = ParagraphStyle(
        "TableHead",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.white
    )

    story = []

    # ================= PAGE 1: TITLE & EXECUTIVE SUMMARY =================
    story.append(Paragraph("DXC Technology & International University of Rabat (UIR)", subtitle_style))
    story.append(Paragraph("FX Trading Room P&L Engine — Defense Executive Guide", title_style))
    story.append(Paragraph("<b>Author:</b> Mohamed Taha El Qassid | <b>Track:</b> Data Engineering (4th Year) | <b>Base Currency:</b> MAD", body_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_BLUE, spaceBefore=4, spaceAfter=10))

    # Meta callout box
    meta_data = [
        [Paragraph("<b>Project Scope:</b> Institutional FX Trading Room Position Keeping & Mark-to-Market Engine", table_cell),
         Paragraph("<b>Primary Fixing:</b> Bank Al-Maghrib (BAM) Official Fixing (15:30)", table_cell)],
        [Paragraph("<b>Core Accounting:</b> Multi-Currency P&L in MAD (FIFO vs. CMP/WAC)", table_cell),
         Paragraph("<b>Storage Architecture:</b> PostgreSQL 16 (Docker) + SQLite 3 Resilient Fallback", table_cell)],
        [Paragraph("<b>Pipeline Orchestration:</b> Apache Airflow 2.9.3 + dbt Data Transformation", table_cell),
         Paragraph("<b>Verification Status:</b> 10/10 PyTest Passed | 6/6 dbt Tests Passed", table_cell)],
    ]
    t_meta = Table(meta_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_BG_BOX),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Section 1
    story.append(Paragraph("1. Executive Summary & The Core Problem", h1_style))
    story.append(Paragraph(
        "A corporate treasury or commercial bank operating in Morocco cannot manage foreign exchange risk across disparate, non-standardized systems. "
        "Trading desks execute transactions in multiple global currencies (USD, EUR, GBP), but Moroccan accounting standards require every single position, "
        "realized gain, and balance sheet provision to be reported strictly in <b>Moroccan Dirham (MAD)</b> based on Bank Al-Maghrib central fixings.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The 3 Fundamental Operational Challenges Solved:</b>",
        body_bold
    ))
    story.append(Paragraph("• <b>Currency Conversion & Peg Compliance (BR1 & BR2):</b> Real-time conversion of direct MAD pairs and synthetic cross-rates (EUR/USD) into MAD, with daily MTM revaluation against BAM's 60/40 currency basket.", bullet_style))
    story.append(Paragraph("• <b>Inventory Depletion Ambiguity (BR4):</b> FIFO (First-In, First-Out) recognizes trading gains earlier, whereas CMP (Weighted Average Cost) smooths volatile exchange rate spikes across reporting periods.", bullet_style))
    story.append(Paragraph("• <b>Front-to-Back Office Discrepancies (BR5):</b> Automatic detection of rate slippages, partial nominal fills, unconfirmed SWIFT MT300 affirmations, and orphan back-office settlement tickets.", bullet_style))
    story.append(Paragraph("• <b>Mathematical Accounting Balance (BR3):</b> Strictly enforces and mathematically verifies that <code>Total P&L = Realized P&L + Unrealized P&L</code> with zero tolerance for discrepancies.", bullet_style))

    story.append(Spacer(1, 8))

    # Section 2
    story.append(Paragraph("2. The Medallion Data Engineering Pipeline", h1_style))
    story.append(Paragraph(
        "Our data architecture follows the industry-standard Medallion model, orchestrated end-to-end by Apache Airflow:",
        body_style
    ))

    pipe_data = [
        [Paragraph("Pipeline Stage", table_head), Paragraph("Technology", table_head), Paragraph("Role & Transformations Performed", table_head)],
        [Paragraph("<b>1. Raw Ingestion</b>", table_cell_bold), Paragraph("Python / REST / CSV", table_cell), Paragraph("Pulls trades from Front-Office blotters and official Bank Al-Maghrib daily fixings.", table_cell)],
        [Paragraph("<b>2. Bronze Staging</b>", table_cell_bold), Paragraph("PostgreSQL / SQLite", table_cell), Paragraph("Raw immutable persistence into <code>stg_trade</code> and <code>stg_market_rate</code>.", table_cell)],
        [Paragraph("<b>3. Silver SQL Marts</b>", table_cell_bold), Paragraph("dbt (Data Build Tool)", table_cell), Paragraph("SQL transformations building <code>fact_trade_mtm</code>: computes synthetic EUR/USD cross into MAD.", table_cell)],
        [Paragraph("<b>4. Gold P&L Engine</b>", table_cell_bold), Paragraph("Python (deque / math)", table_cell), Paragraph("Chronological FIFO queue lot matching and WAC rolling cost calculations.", table_cell)],
        [Paragraph("<b>5. Persistence & Mart</b>", table_cell_bold), Paragraph("PostgreSQL / SQLite", table_cell), Paragraph("Upserts into <code>daily_pnl</code> with physical database <code>CHECK</code> constraints.", table_cell)],
        [Paragraph("<b>6. Quality Assertions</b>", table_cell_bold), Paragraph("dbt test & PyTest", table_cell), Paragraph("6 automated dbt tests + 10 unit tests halting the pipeline upon any anomaly.", table_cell)],
    ]
    t_pipe = Table(pipe_data, colWidths=[110, 110, 284])
    t_pipe.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_NAVY),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_BOX]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_pipe)

    story.append(PageBreak())

    # ================= PAGE 2: STEP-BY-STEP RUNNING GUIDE =================
    story.append(Paragraph("3. Step-by-Step Running Guide (Mac & Windows)", h1_style))
    story.append(Paragraph(
        "You can run the application in two modes: <b>Option A (Instant Zero-Docker)</b> or <b>Option B (Full Enterprise Stack)</b>.",
        body_style
    ))

    story.append(Paragraph("Option A: Instant Zero-Docker Run (Fastest for Defense / Laptops)", h2_style))
    story.append(Paragraph(
        "Uses the local SQLite database (<code>db/fx_trading_room.db</code>) with all 72 Moroccan trades already populated. Requires zero Docker containers.",
        body_style
    ))

    cmd_box_a = [
        [Paragraph("<b>Terminal Commands (Mac / Windows):</b>", table_cell_bold)],
        [Paragraph("<code>git pull origin main</code><br/>"
                   "<code>pip install -r requirements.txt</code><br/>"
                   "<code>streamlit run dashboard/app.py</code>", code_style)],
        [Paragraph("<i>Result: Dashboard opens instantly at <b>http://localhost:8501</b> with all trades, charts, and blotters.</i>", table_cell)]
    ]
    t_box_a = Table(cmd_box_a, colWidths=[504])
    t_box_a.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_BG_BOX),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#38BDF8")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_box_a)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Option B: Full Enterprise Stack (PostgreSQL 16 + Airflow + dbt)", h2_style))
    story.append(Paragraph(
        "Runs the complete containerized architecture with PostgreSQL on port 5432 and Apache Airflow on port 8080.",
        body_style
    ))

    cmd_box_b = [
        [Paragraph("<b>Terminal Commands:</b>", table_cell_bold)],
        [Paragraph("<code># 1. Start Docker containers in background</code><br/>"
                   "<code>docker compose up -d</code><br/>"
                   "<code># 2. Access Apache Airflow Web UI</code><br/>"
                   "<code>Open http://localhost:8080 (Username: admin | Password: admin)</code><br/>"
                   "<code># 3. Launch Streamlit (automatically detects live PostgreSQL)</code><br/>"
                   "<code>streamlit run dashboard/app.py</code>", code_style)],
        [Paragraph("<i>Result: Sidebar displays <b>'Storage Engine: PostgreSQL 16 (Live Docker Container)'</b>.</i>", table_cell)]
    ]
    t_box_b = Table(cmd_box_b, colWidths=[504])
    t_box_b.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_BG_BOX),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#4F46E5")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_box_b)
    story.append(Spacer(1, 10))

    # Section 4
    story.append(Paragraph("4. Live Terminal Verification Commands (For the Jury)", h1_style))
    story.append(Paragraph(
        "If a jury member asks to see live tests in the terminal, run these exact commands:",
        body_style
    ))

    demo_commands = [
        [Paragraph("Audit Objective", table_head), Paragraph("Command to Run in Terminal", table_head), Paragraph("Expected Clean Output", table_head)],
        [
            Paragraph("<b>dbt Data Quality Tests</b><br/>(6 Pipeline Checks)", table_cell),
            Paragraph("<code>docker exec fx-pnl-airflow bash -c \"cd /opt/airflow/fx_pnl_dbt && dbt test\"</code><br/><i>(or <code>cd fx_pnl_dbt && dbt test</code>)</i>", code_style),
            Paragraph("<b>Done. PASS=6 WARN=0 ERROR=0</b><br/>Tests BR3 identity, positive nominals, positive rates, unique IDs.", table_cell)
        ],
        [
            Paragraph("<b>PyTest Full Test Suite</b><br/>(10 Python Unit Tests)", table_cell),
            Paragraph("<code>pytest -v</code>", code_style),
            Paragraph("<b>10 passed in 0.55s (100%)</b><br/>Validates MTM math, FIFO deque, CMP cost, and FO/BO matching.", table_cell)
        ],
        [
            Paragraph("<b>SQL Integrity Check</b><br/>(Zero Accounting Breaks)", table_cell),
            Paragraph("<code>sqlite3 db/fx_trading_room.db \"SELECT * FROM daily_pnl WHERE ROUND(total_mad, 2) != ROUND(realized_mad + unrealized_mad, 2);\"</code>", code_style),
            Paragraph("<b>(0 rows)</b><br/>Mathematically proves zero balance sheet discrepancies exist.", table_cell)
        ],
    ]
    t_demo = Table(demo_commands, colWidths=[120, 204, 180])
    t_demo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_NAVY),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_BOX]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_demo)

    story.append(PageBreak())

    # ================= PAGE 3: INTERACTIVE UI & JURY DEFENSE Q&A =================
    story.append(Paragraph("5. Interactive UI Demo Tour (What to Click & Show)", h1_style))
    story.append(Paragraph(
        "Demonstrate the platform's professional capabilities following this exact sequence:",
        body_style
    ))

    ui_tour = [
        [Paragraph("UI Component", table_head), Paragraph("Action / Click", table_head), Paragraph("Key Financial & Technical Concept to Highlight", table_head)],
        [
            Paragraph("<b>Sidebar: Storage Engine Switcher</b>", table_cell_bold),
            Paragraph("Switch between <i>PostgreSQL</i> and <i>SQLite</i>", table_cell),
            Paragraph("Proves <b>resilient dual-engine architecture</b>: zero crash fallback when offline, enterprise containerization when online.", table_cell)
        ],
        [
            Paragraph("<b>Trading Period Calendar Filter</b>", table_cell_bold),
            Paragraph("Select <i>Filter by Month</i> or <i>Specific Day</i>", table_cell),
            Paragraph("Shows dynamic KPI recalculation (Total MTM, Realized, Latent) across 72 institutional trades (August to October 2026).", table_cell)
        ],
        [
            Paragraph("<b>PFE Benchmark Button</b>", table_cell_bold),
            Paragraph("Select <i>PFE Benchmark (2026-09-07)</i>", table_cell),
            Paragraph("Reproduces the exact brief benchmark: <b>+79,460 MAD Total MTM</b> (+20,000 Realized, +59,460 Latent).", table_cell)
        ],
        [
            Paragraph("<b>Tab 1: Active Trade Blotter</b>", table_cell_bold),
            Paragraph("Show formulas column", table_cell),
            Paragraph("Full mathematical transparency: displays exact arithmetic formula in MAD for every trade (e.g. <code>(close - trade) * nominal</code>).", table_cell)
        ],
        [
            Paragraph("<b>Tab 2: FO/BO Reconciliation Hub</b>", table_cell_bold),
            Paragraph("Filter by <i>Breaks Only</i>", table_cell),
            Paragraph("Detects <b>4 authentic banking breaks</b>: rate slippage (+3.5 pips), partial nominal cut, unconfirmed SWIFT MT300, and orphan settlement.", table_cell)
        ],
        [
            Paragraph("<b>Tab 3: BAM Market Fixings Terminal</b>", table_cell_bold),
            Paragraph("Toggle USD/MAD, EUR/MAD, EUR/USD", table_cell),
            Paragraph("Pure institutional FX candlestick charting with 20-period Simple Moving Average and central bank fixing indicators.", table_cell)
        ],
        [
            Paragraph("<b>Tab 4: FIFO vs. CMP Inventory</b>", table_cell_bold),
            Paragraph("Review Section 4 proof", table_cell),
            Paragraph("Demonstrates lot unwinding: FIFO Realized = <b>+22,000 MAD</b> vs. CMP Realized = <b>+18,000 MAD</b> (explains the brief typo).", table_cell)
        ],
        [
            Paragraph("<b>Tab 5: BAM Fluctuation Band</b>", table_cell_bold),
            Paragraph("View +/-5% Stress Test Matrix", table_cell),
            Paragraph("Evaluates desk stop-loss compliance against Bank Al-Maghrib peg boundaries (60% EUR / 40% USD basket).", table_cell)
        ],
        [
            Paragraph("<b>Tab 6: Airflow & Data Engineering</b>", table_cell_bold),
            Paragraph("Click <i>Trigger Airflow DAG</i>", table_cell),
            Paragraph("Executes the full pipeline live and provides direct hyperlink to Airflow Web UI on port 8080.", table_cell)
        ],
    ]
    t_ui = Table(ui_tour, colWidths=[110, 110, 284])
    t_ui.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_NAVY),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_BOX]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_ui)
    story.append(Spacer(1, 10))

    # Section 6
    story.append(Paragraph("6. Anticipated Jury Questions & Winning Answers", h1_style))

    story.append(Paragraph("<b>Q1: Why is FIFO realized profit (+22,000 MAD) higher than CMP (+18,000 MAD)?</b>", body_bold))
    story.append(Paragraph(
        "<i>Answer:</i> 'In a rising exchange rate market, FIFO depletes the oldest, cheaper lots first (purchased at 9.9100), yielding a higher immediate realized gain on sale (+22k MAD). "
        "CMP averages all purchase prices (9.9200), yielding +18k MAD. This is purely a timing difference: upon complete liquidation of the book, cumulative P&L converges to identical values.'",
        body_style
    ))

    story.append(Paragraph("<b>Q2: How do you value currency pairs without a direct BAM fixing (e.g. EUR/USD)?</b>", body_bold))
    story.append(Paragraph(
        "<i>Answer:</i> 'We construct a synthetic cross-rate via triangular arbitrage: <code>EUR/USD = (EUR/MAD) / (USD/MAD)</code>. "
        "This guarantees consistent Mark-to-Market revaluation in MAD without introducing cross-rate arbitrage breaks.'",
        body_style
    ))

    story.append(Paragraph("<b>Q3: Why test data quality at both the database level (CHECK) and the pipeline level (dbt)?</b>", body_bold))
    story.append(Paragraph(
        "<i>Answer:</i> 'We apply Defense-in-Depth: database CHECK constraints prevent physically corrupt rows from being stored, while dbt tests act as automated quality gates in Airflow. "
        "If an upstream market feed sends invalid data, dbt detects it and halts the pipeline before incorrect figures reach risk managers.'",
        body_style
    ))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built at: {output_path}")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_file = out_dir / "FX_Trading_Room_PFE_Executive_Guide.pdf"
    build_pdf(str(pdf_file))
