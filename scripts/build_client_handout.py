#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "outputs" / "reference_v1_1_report.json"
DESTINATION = ROOT / "output" / "pdf" / "A2_Client_Case_Study.pdf"
NAVY = colors.HexColor("#071b31")
INK = colors.HexColor("#10243e")
BLUE = colors.HexColor("#177ddc")
AMBER = colors.HexColor("#a45f00")
MUTED = colors.HexColor("#637083")
LINE = colors.HexColor("#d9e0e8")
PALE_BLUE = colors.HexColor("#eef5fb")
PALE_AMBER = colors.HexColor("#fff8e9")
pdfmetrics.registerFont(TTFont("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 15 * mm, 192 * mm, 15 * mm)
    canvas.setFont("DejaVuSans", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 10.5 * mm, "A2 V1.1 | Public portfolio demonstration | Shofi Ahmed Uddin | 2026")
    canvas.drawRightString(192 * mm, 10.5 * mm, f"{doc.page}")
    canvas.restoreState()


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def build() -> Path:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    metrics = report["metrics"]
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], fontName="DejaVuSans-Bold", fontSize=26, leading=29, textColor=INK, alignment=TA_LEFT, spaceAfter=5 * mm)
    deck = ParagraphStyle("deck", parent=styles["BodyText"], fontName="DejaVuSans", fontSize=12, leading=17, textColor=MUTED, spaceAfter=5 * mm)
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontName="DejaVuSans-Bold", fontSize=16, leading=19, textColor=INK, spaceBefore=4 * mm, spaceAfter=2.5 * mm)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName="DejaVuSans-Bold", fontSize=11, leading=14, textColor=BLUE, spaceBefore=2 * mm, spaceAfter=1.5 * mm)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontName="DejaVuSans", fontSize=9.3, leading=13.2, textColor=INK, spaceAfter=2.3 * mm)
    small = ParagraphStyle("small", parent=body, fontSize=7.6, leading=10, textColor=MUTED)
    callout = ParagraphStyle("callout", parent=body, fontName="DejaVuSans-Bold", fontSize=11.5, leading=16, textColor=INK, leftIndent=4 * mm, rightIndent=4 * mm, spaceBefore=2 * mm, spaceAfter=2 * mm)
    status = ParagraphStyle("status", parent=body, fontName="DejaVuSans-Bold", fontSize=9.2, leading=13, textColor=INK, spaceBefore=2 * mm, spaceAfter=2 * mm)

    doc = SimpleDocTemplate(str(DESTINATION), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=17 * mm, bottomMargin=20 * mm, title="A2 Evidence-Governed Agentic Data Scientist - Client Case Study", author="Shofi Ahmed Uddin")
    story = []
    story.append(paragraph("PROJECT A PRO / A2 V1.1", ParagraphStyle("eyebrow", parent=small, fontName="DejaVuSans-Bold", textColor=BLUE)))
    story.append(paragraph("Evidence before execution", title))
    story.append(paragraph("A working Data Science system that separates model performance, evidence sufficiency and authority to act.", deck))
    plate = Image(str(ROOT / "portfolio" / "A2_ARCHITECTURE_PLATE.png"), width=174 * mm, height=97.875 * mm)
    story.append(plate)
    story.append(Spacer(1, 4 * mm))
    summary = Table([
        [paragraph("FINAL DISPOSITION", small), paragraph("ANALYSIS COMPLETE", small), paragraph("ACTION AUTHORISED", small)],
        [paragraph("REQUEST_HUMAN_REVIEW", status), paragraph("TRUE", callout), paragraph("FALSE", callout)],
    ], colWidths=[74 * mm, 50 * mm, 50 * mm])
    summary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE_AMBER), ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#d59635")),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#ead2aa")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(summary)
    story.append(paragraph("What this proves", h1))
    story.append(paragraph("A2 did not merely produce a predictive model. It detected where apparently useful statistical evidence stopped justifying execution. The system excluded post-contact leakage, exposed severe temporal shift and high-band miscalibration, and kept the final decision at accountable human review.", body))
    story.append(PageBreak())

    story.append(paragraph("The evidence and the boundary", title))
    story.append(paragraph("A reproducible technical demonstration using 41,188 pinned historical campaign records from the UCI Bank Marketing dataset.", deck))
    data = [
        ["Measure", "Result", "What it supports"],
        ["ROC AUC", f"{metrics['roc_auc']:.3f}", "Bounded retrospective ranking value"],
        ["Average precision", f"{metrics['average_precision']:.3f}", "Minority-class discrimination"],
        ["Brier score", f"{metrics['brier_score']:.3f} vs {metrics['baseline_brier_score']:.3f}", "Improvement over prior baseline"],
        ["Calibration ECE", f"{metrics['calibration']['expected_calibration_error']:.3f}", "Material probability error remains"],
        ["Worst bin gap", f"{metrics['calibration']['maximum_calibration_error']:.3f}", "High-score overconfidence"],
        ["Train / holdout prevalence", "6.4% / 30.8%", "Severe temporal shift; no deployment claim"],
    ]
    table = Table(data, colWidths=[48 * mm, 42 * mm, 84 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans-Bold"), ("FONTNAME", (0, 1), (-1, -1), "DejaVuSans"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.2), ("LEADING", (0, 0), (-1, -1), 10.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE_BLUE]),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(paragraph("Controls demonstrated", h1))
    controls = [
        [paragraph("PROVENANCE", h2), paragraph("Pinned source and analytical-file hashes; schema and target validation.", body)],
        [paragraph("ADMISSIBILITY", h2), paragraph("Call duration removed because it is unavailable at the pre-contact decision moment.", body)],
        [paragraph("HARDENING", h2), paragraph("Calibration, threshold and subgroup diagnostics plus hostile target-copy and corrupted-label tests.", body)],
        [paragraph("AUTHORITY", h2), paragraph("Analytical completion is distinct from permission. Critical evidence failure remains non-authorising even when approval is supplied.", body)],
    ]
    controls_table = Table(controls, colWidths=[38 * mm, 136 * mm])
    controls_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(controls_table)
    story.append(paragraph("Commercial application", h1))
    story.append(paragraph("The control pattern can be applied to one bounded workflow in financial services, fraud operations, insurance, health, public services, safety assurance or autonomous-system review. A client engagement would reconstruct the decision moment, permissible evidence, uncertainty, authority boundary, safe-stop conditions and replay record before production integration is considered.", body))
    boundary = Table([[paragraph("This is not a deployable banking product, causal study, fairness audit, security certification, legal opinion, independent validation or autonomous decision engine.", callout)]], colWidths=[174 * mm])
    boundary.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE_AMBER), ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#d59635")), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(boundary)
    story.append(Spacer(1, 3 * mm))
    story.append(paragraph("Dataset: S. Moro, P. Rita and P. Cortez, Bank Marketing, UCI Machine Learning Repository, DOI 10.24432/C5K306, CC BY 4.0. Code: MIT. Material generative-AI assistance is disclosed; Shofi Ahmed Uddin remains responsible for architecture, statistical judgement, claims and publication.", small))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return DESTINATION


if __name__ == "__main__":
    print(build())
