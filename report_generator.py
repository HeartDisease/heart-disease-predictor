# report_generator.py
# Generates a downloadable PDF report for the Heart Disease Risk Predictor

import io
import re
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)


# ── Colour palette ──────────────────────────────────────────────────────────
DARK_BLUE    = colors.HexColor("#1a3a5c")
MID_BLUE     = colors.HexColor("#1a6fa8")
LIGHT_BLUE   = colors.HexColor("#e8f4fd")
RED          = colors.HexColor("#d73027")
ORANGE       = colors.HexColor("#fc8d59")
GREEN        = colors.HexColor("#1a9850")
LIGHT_RED    = colors.HexColor("#fde8e8")
LIGHT_ORANGE = colors.HexColor("#fff3e0")
LIGHT_GREEN  = colors.HexColor("#e8f5e9")
GREY         = colors.HexColor("#666666")
LIGHT_GREY   = colors.HexColor("#f5f5f5")
WHITE        = colors.white
BLACK        = colors.black


def _styles():
    base   = getSampleStyleSheet()
    custom = {}

    custom["title"] = ParagraphStyle(
        "title",
        parent=base["Normal"],
        fontSize=18,
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    custom["subtitle"] = ParagraphStyle(
        "subtitle",
        parent=base["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#cce4f7"),
        alignment=TA_CENTER,
        spaceAfter=2,
        fontName="Helvetica",
    )
    custom["section_header"] = ParagraphStyle(
        "section_header",
        parent=base["Normal"],
        fontSize=13,
        textColor=WHITE,
        fontName="Helvetica-Bold",
        spaceAfter=0,
        spaceBefore=0,
    )
    custom["body"] = ParagraphStyle(
        "body",
        parent=base["Normal"],
        fontSize=10,
        textColor=BLACK,
        fontName="Helvetica",
        spaceAfter=4,
        leading=15,
    )
    custom["body_bold"] = ParagraphStyle(
        "body_bold",
        parent=base["Normal"],
        fontSize=10,
        textColor=BLACK,
        fontName="Helvetica-Bold",
        spaceAfter=4,
    )
    custom["small"] = ParagraphStyle(
        "small",
        parent=base["Normal"],
        fontSize=8,
        textColor=GREY,
        fontName="Helvetica",
        spaceAfter=2,
        leading=11,
    )
    custom["disclaimer"] = ParagraphStyle(
        "disclaimer",
        parent=base["Normal"],
        fontSize=8,
        textColor=GREY,
        fontName="Helvetica-Oblique",
        alignment=TA_CENTER,
        spaceAfter=2,
        leading=11,
    )
    custom["rec_urgent"] = ParagraphStyle(
        "rec_urgent",
        parent=base["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#7b0000"),
        fontName="Helvetica",
        spaceAfter=3,
        leading=13,
    )
    custom["rec_important"] = ParagraphStyle(
        "rec_important",
        parent=base["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#7a4000"),
        fontName="Helvetica",
        spaceAfter=3,
        leading=13,
    )
    custom["rec_maintain"] = ParagraphStyle(
        "rec_maintain",
        parent=base["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#1a5c2a"),
        fontName="Helvetica",
        spaceAfter=3,
        leading=13,
    )

    return custom


def _section_header(text, styles):
    header_para = Paragraph(text, styles["section_header"])
    tbl = Table([[header_para]], colWidths=[170 * mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), MID_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return tbl


def _clean_rec(text):
    """Strips emoji bullets and markdown bold (**) from recommendation strings."""
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = text.replace("**", "")
    return text.strip()


def generate_pdf_report(
    male, age, currentSmoker, cigsPerDay, BPMeds,
    prevalentStroke, prevalentHyp, diabetes,
    totChol, sysBP, diaBP, BMI, heartRate, glucose,
    risk_pct, risk_label, risk_color_hex,
    bench_rows,
    shap_data,
    recs,
):
    buffer = io.BytesIO()
    page_w, page_h = A4
    margin = 20 * mm

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles  = _styles()
    content = []

    # ── 1. HEADER BANNER ─────────────────────────────────────────────────────
    header_data = [[
        Paragraph("Heart Disease Risk Report", styles["title"]),
    ]]
    header_table = Table(header_data, colWidths=[170 * mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DARK_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 28),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    content.append(header_table)

    subtitle_data = [[
        Paragraph(
            "Based on the Framingham Heart Study  |  10-Year Cardiovascular Risk Assessment",
            styles["subtitle"]
        ),
    ]]
    sub_table = Table(subtitle_data, colWidths=[170 * mm])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DARK_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    content.append(sub_table)
    content.append(Spacer(1, 5 * mm))

    now = datetime.now().strftime("%d %B %Y, %H:%M")
    content.append(Paragraph(f"Report generated: {now}", styles["small"]))
    content.append(Spacer(1, 3 * mm))

    # ── 2. PATIENT DETAILS ───────────────────────────────────────────────────
    content.append(_section_header("  Patient Details", styles))
    content.append(Spacer(1, 3 * mm))

    gender_str   = "Male"   if male == 1           else "Female"
    smoker_str   = "Yes"    if currentSmoker == 1  else "No"
    bpmeds_str   = "Yes"    if BPMeds == 1         else "No"
    stroke_str   = "Yes"    if prevalentStroke == 1 else "No"
    hyp_str      = "Yes"    if prevalentHyp == 1   else "No"
    diabetes_str = "Yes"    if diabetes == 1       else "No"

    detail_data = [
        ["Gender",            gender_str,           "Age",             f"{age} years"],
        ["Smoker",            smoker_str,            "Cigarettes/Day",  str(cigsPerDay)],
        ["BP Medication",     bpmeds_str,            "Hypertension Hx", hyp_str],
        ["Stroke History",    stroke_str,            "Diabetes",        diabetes_str],
        ["Total Cholesterol", f"{totChol} mg/dL",   "Systolic BP",     f"{sysBP} mmHg"],
        ["Diastolic BP",      f"{diaBP} mmHg",      "BMI",             f"{BMI:.1f}"],
        ["Heart Rate",        f"{heartRate} bpm",   "Glucose",         f"{glucose} mg/dL"],
    ]

    col_w = [42*mm, 43*mm, 42*mm, 43*mm]
    detail_table = Table(detail_data, colWidths=col_w)
    detail_table.setStyle(TableStyle([
        ("FONTNAME",         (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",         (0, 0), (-1, -1), 9),
        ("FONTNAME",         (0, 0), (0, -1),  "Helvetica-Bold"),
        ("FONTNAME",         (2, 0), (2, -1),  "Helvetica-Bold"),
        ("BACKGROUND",       (0, 0), (-1, -1), LIGHT_GREY),
        ("BACKGROUND",       (0, 0), (0, -1),  LIGHT_BLUE),
        ("BACKGROUND",       (2, 0), (2, -1),  LIGHT_BLUE),
        ("ROWBACKGROUNDS",   (0, 0), (-1, -1), [WHITE, LIGHT_GREY]),
        ("GRID",             (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("TOPPADDING",       (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",    (0, 0), (-1, -1), 5),
        ("LEFTPADDING",      (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",     (0, 0), (-1, -1), 8),
        ("VALIGN",           (0, 0), (-1, -1), "MIDDLE"),
    ]))
    content.append(detail_table)
    content.append(Spacer(1, 5 * mm))

    # ── 3. RISK SCORE ────────────────────────────────────────────────────────
    content.append(_section_header("  Predicted Risk Score", styles))
    content.append(Spacer(1, 3 * mm))

    risk_color_obj = colors.HexColor(risk_color_hex)

    if risk_pct >= 20:
        risk_description = (
            "This is in the HIGH risk range. "
            "Please consult your doctor promptly."
        )
    elif risk_pct >= 10:
        risk_description = (
            "This is in the MODERATE risk range. "
            "Work on the factors below to reduce it."
        )
    else:
        risk_description = (
            "This is in the LOW risk range. "
            "Keep maintaining your healthy habits."
        )

    risk_data = [[
        Paragraph(f"{risk_pct}%", ParagraphStyle(
            "big_risk",
            fontSize=36,
            textColor=risk_color_obj,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
        )),
        Paragraph(
            f"<b>{risk_label}</b><br/><br/>"
            f"Your predicted 10-year risk of developing coronary heart disease "
            f"is <b>{risk_pct}%</b>.<br/><br/>"
            f"{risk_description}",
            styles["body"],
        ),
    ]]
    risk_table = Table(risk_data, colWidths=[45*mm, 125*mm])
    risk_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, 0), LIGHT_GREY),
        ("BACKGROUND",    (1, 0), (1, 0), WHITE),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (0, 0), (0, 0),  "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    content.append(risk_table)
    content.append(Spacer(1, 5 * mm))

    # ── 4. HEALTH BENCHMARKS ─────────────────────────────────────────────────
    content.append(_section_header("  Health Benchmarks", styles))
    content.append(Spacer(1, 3 * mm))

    bench_header = [
        Paragraph("<b>Health Metric</b>", styles["body_bold"]),
        Paragraph("<b>Your Value</b>",    styles["body_bold"]),
        Paragraph("<b>Normal Range</b>",  styles["body_bold"]),
        Paragraph("<b>Status</b>",        styles["body_bold"]),
    ]
    bench_table_data = [bench_header]

    for r in bench_rows:
        # Strip emojis from status for PDF rendering
        status_clean = re.sub(r'[^\x00-\x7F]+', '', r["Status"]).strip()
        bench_table_data.append([
            Paragraph(r["Metric"],       styles["body"]),
            Paragraph(r["Your Value"],   styles["body"]),
            Paragraph(r["Normal Range"], styles["body"]),
            Paragraph(status_clean,      styles["body"]),
        ])

    bench_col_w = [50*mm, 38*mm, 42*mm, 40*mm]
    bench_table = Table(bench_table_data, colWidths=bench_col_w)

    bench_style = [
        ("BACKGROUND",    (0, 0), (-1, 0), MID_BLUE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]

    for i, r in enumerate(bench_rows, start=1):
        if "✅" in r["Status"]:
            bench_style.append(("BACKGROUND", (0, i), (-1, i), LIGHT_GREEN))
        elif "🔴" in r["Status"]:
            bench_style.append(("BACKGROUND", (0, i), (-1, i), LIGHT_RED))
        else:
            bench_style.append(("BACKGROUND", (0, i), (-1, i), LIGHT_ORANGE))

    bench_table.setStyle(TableStyle(bench_style))
    content.append(bench_table)
    content.append(Spacer(1, 5 * mm))

    # ── 5. SHAP FACTOR BREAKDOWN ─────────────────────────────────────────────
    content.append(_section_header("  Risk Factor Breakdown (AI Explanation)", styles))
    content.append(Spacer(1, 3 * mm))
    content.append(Paragraph(
        "The table below shows how much each health factor <b>increased</b> (+) or "
        "<b>decreased</b> (-) your predicted risk score, as calculated by the AI model.",
        styles["body"],
    ))
    content.append(Spacer(1, 3 * mm))

    shap_header = [
        Paragraph("<b>Risk Factor</b>", styles["body_bold"]),
        Paragraph("<b>SHAP Value</b>",  styles["body_bold"]),
        Paragraph("<b>Direction</b>",   styles["body_bold"]),
    ]
    shap_table_data = [shap_header]

    for feat, val in shap_data:
        direction = "Increases Risk" if val > 0 else "Decreases Risk"
        shap_table_data.append([
            Paragraph(feat,           styles["body"]),
            Paragraph(f"{val:+.4f}", styles["body"]),
            Paragraph(direction,      styles["body"]),
        ])

    shap_col_w = [80*mm, 45*mm, 45*mm]
    shap_table = Table(shap_table_data, colWidths=shap_col_w)

    shap_style = [
        ("BACKGROUND",    (0, 0), (-1, 0), MID_BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]

    for i, (feat, val) in enumerate(shap_data, start=1):
        if val > 0:
            shap_style.append(("BACKGROUND", (0, i), (-1, i), LIGHT_RED))
        else:
            shap_style.append(("BACKGROUND", (0, i), (-1, i), LIGHT_GREEN))

    shap_table.setStyle(TableStyle(shap_style))
    content.append(shap_table)
    content.append(Spacer(1, 5 * mm))

    # ── 6. RECOMMENDATIONS ──────────────────────────────────────────────────
    content.append(_section_header("  Personalised Health Recommendations", styles))
    content.append(Spacer(1, 3 * mm))

    if recs["urgent"]:
        content.append(Paragraph(
            "<b>URGENT — Please Discuss With Your Doctor</b>",
            ParagraphStyle("urg_hd", fontSize=11, textColor=RED,
                           fontName="Helvetica-Bold", spaceAfter=4)
        ))
        for item in recs["urgent"]:
            clean = _clean_rec(item)
            rec_data = [[Paragraph(clean, styles["rec_urgent"])]]
            rec_tbl  = Table(rec_data, colWidths=[170*mm])
            rec_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_RED),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                ("TOPPADDING",    (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("BOX",           (0, 0), (-1, -1), 1, RED),
            ]))
            content.append(rec_tbl)
            content.append(Spacer(1, 2*mm))

    if recs["important"]:
        content.append(Spacer(1, 2*mm))
        content.append(Paragraph(
            "<b>IMPORTANT — Work on Improving These</b>",
            ParagraphStyle("imp_hd", fontSize=11,
                           textColor=colors.HexColor("#e65c00"),
                           fontName="Helvetica-Bold", spaceAfter=4)
        ))
        for item in recs["important"]:
            clean = _clean_rec(item)
            rec_data = [[Paragraph(clean, styles["rec_important"])]]
            rec_tbl  = Table(rec_data, colWidths=[170*mm])
            rec_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_ORANGE),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                ("TOPPADDING",    (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("BOX",           (0, 0), (-1, -1), 1, ORANGE),
            ]))
            content.append(rec_tbl)
            content.append(Spacer(1, 2*mm))

    if recs["maintain"]:
        content.append(Spacer(1, 2*mm))
        content.append(Paragraph(
            "<b>KEEP IT UP — These Look Good</b>",
            ParagraphStyle("mnt_hd", fontSize=11, textColor=GREEN,
                           fontName="Helvetica-Bold", spaceAfter=4)
        ))
        for item in recs["maintain"]:
            clean = _clean_rec(item)
            rec_data = [[Paragraph(clean, styles["rec_maintain"])]]
            rec_tbl  = Table(rec_data, colWidths=[170*mm])
            rec_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_GREEN),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                ("TOPPADDING",    (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("BOX",           (0, 0), (-1, -1), 1, GREEN),
            ]))
            content.append(rec_tbl)
            content.append(Spacer(1, 2*mm))

    content.append(Spacer(1, 6 * mm))

    # ── 7. DISCLAIMER ────────────────────────────────────────────────────────
    content.append(HRFlowable(width="100%", thickness=0.5, color=GREY))
    content.append(Spacer(1, 3 * mm))
    content.append(Paragraph(
        "DISCLAIMER: This report is generated by an AI-based educational tool trained on the "
        "Framingham Heart Study dataset. It is NOT a medical diagnosis and should NOT replace "
        "professional medical advice. Always consult a licensed physician or cardiologist for "
        "clinical decisions. The model has an AUC of ~0.70, meaning predictions carry uncertainty.",
        styles["disclaimer"],
    ))

    # ── BUILD ─────────────────────────────────────────────────────────────────
    doc.build(content)
    buffer.seek(0)
    return buffer.read()