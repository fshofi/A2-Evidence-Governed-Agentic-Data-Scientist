#!/usr/bin/env python3
"""Render deterministic static portfolio previews from the reference report."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / "portfolio"
REPORT = ROOT / "outputs" / "reference_v1_1_report.json"
REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD if bold else REGULAR, size)


def box(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], fill: str = "white", outline: str = "#d8e0e8", radius: int = 14) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=2)


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int, fill: str = "#10243e", bold: bool = False, anchor: str | None = None) -> None:
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor)


def architecture(report: dict) -> None:
    image = Image.new("RGB", (1600, 900), "#f3f6f9")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1600, 210), fill="#071b31")
    text(draw, (90, 52), "PROJECT A PRO · A2 V1.1", 18, "#91c5ef", True)
    text(draw, (90, 94), "Evidence before execution", 48, "white", True)
    text(draw, (90, 158), "Model performance, evidence sufficiency and authority are separate decisions.", 22, "#c7d9e9")
    box(draw, (1260, 66, 1510, 154), "#12334f", "#8eb8db")
    text(draw, (1283, 83), "FINAL STATE", 14, "#b9d1e5", True)
    text(draw, (1283, 113), "HUMAN REVIEW", 23, "#ffd185", True)

    text(draw, (90, 250), "RECONSTRUCTABLE EVIDENCE PATH", 15, "#657587", True)
    nodes = [
        (90, "1 · Verified source", "Pinned archive + CSV hashes", "Schema and provenance"),
        (365, "2 · Admissibility", "Decision moment fixed", "Post-call duration excluded"),
        (640, "3 · Model", "Transparent preprocessing", "Logistic model + baseline"),
        (915, "4 · Validation", "Ordered holdout + calibration", "Thresholds + subgroups"),
    ]
    for x, title, first, second in nodes:
        box(draw, (x, 305, x + 245, 435))
        text(draw, (x + 25, 330), title, 18, bold=True)
        text(draw, (x + 25, 371), first, 14, "#5c6e80")
        text(draw, (x + 25, 397), second, 14, "#5c6e80")
        if x < 915:
            draw.line((x + 247, 370, x + 267, 370), fill="#4d6983", width=3)
            draw.polygon([(x + 267, 364), (x + 277, 370), (x + 267, 376)], fill="#4d6983")
    box(draw, (1190, 305, 1510, 435), "#fff8e9", "#d59635")
    text(draw, (1215, 330), "5 · Authority gate", 18, "#8d5400", True)
    text(draw, (1215, 371), "Evidence does not grant permission", 14, "#5c6e80")
    text(draw, (1215, 397), "No external action connector", 14, "#5c6e80")
    draw.line((1162, 370, 1182, 370), fill="#4d6983", width=3)
    draw.polygon([(1182, 364), (1190, 370), (1182, 376)], fill="#4d6983")

    metrics = report["metrics"]
    box(draw, (90, 485, 1060, 797))
    text(draw, (122, 520), "REFERENCE RUN · 41,188 RECORDS", 15, "#657587", True)
    draw.line((122, 558, 1028, 558), fill="#d8e0e8", width=2)
    values = [
        (122, f"{metrics['roc_auc']:.3f}", "ROC AUC", "#10243e"),
        (318, f"{metrics['average_precision']:.3f}", "Average precision", "#10243e"),
        (540, f"{metrics['brier_score']:.3f}", "Brier score", "#10243e"),
        (742, "24.5 pp", "Prevalence shift", "#8d5400"),
        (912, f"{metrics['calibration']['maximum_calibration_error']:.3f}", "Worst calibration gap", "#8d5400"),
    ]
    for x, value, label, colour in values:
        text(draw, (x, 584), value, 27, colour, True)
        text(draw, (x, 624), label, 13, "#657587")
    box(draw, (122, 688, 1028, 765), "#eef5fb", "#eef5fb", 10)
    text(draw, (146, 704), "BOUNDED CONCLUSION", 14, "#174f7c", True)
    text(draw, (146, 734), "Retrospective ranking value exists; deployment and probability-reliability claims do not.", 16, "#36536d")

    box(draw, (1094, 485, 1510, 797), "#071b31", "#071b31")
    text(draw, (1125, 520), "GOVERNANCE RESULT", 14, "#91c5ef", True)
    text(draw, (1125, 574), "Analysis complete", 20, "#c7d9e9")
    text(draw, (1475, 574), "TRUE", 20, "#58c49b", True, "ra")
    draw.line((1125, 616, 1475, 616), fill="#35516b", width=2)
    text(draw, (1125, 646), "Action authorised", 20, "#c7d9e9")
    text(draw, (1475, 646), "FALSE", 20, "#ffd185", True, "ra")
    box(draw, (1125, 704, 1475, 766), "#142f49", "#d59635", 9)
    text(draw, (1300, 735), "REQUEST_HUMAN_REVIEW", 17, "#ffd185", True, "mm")
    text(draw, (90, 845), "Public portfolio demonstration · AI assistance disclosed · No production, causal, fairness or independent-validation claim", 13, "#657587")
    text(draw, (1510, 845), "Shofi Ahmed Uddin · 2026", 13, "#657587", anchor="ra")
    image.save(PORTFOLIO / "A2_ARCHITECTURE_PLATE.png", optimize=True)


def dashboard(report: dict) -> None:
    image = Image.new("RGB", (1440, 1720), "#f4f7fa")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1440, 220), fill="#071b31")
    text(draw, (60, 45), "PROJECT A PRO · A2 V1.1", 16, "#91c5ef", True)
    text(draw, (60, 80), "Evidence-Governed Data Science", 42, "white", True)
    text(draw, (60, 145), "Performance, evidence sufficiency and authority remain separate.", 20, "#c7d9e9")
    metrics = report["metrics"]
    cards = [
        ("DECISION STATUS", "HUMAN REVIEW", "#a45f00"),
        ("ANALYSIS COMPLETE", "TRUE", "#10243e"),
        ("ACTION AUTHORISED", "FALSE", "#a45f00"),
        ("CALIBRATION ECE", f"{metrics['calibration']['expected_calibration_error']:.3f}", "#10243e"),
        ("PREVALENCE SHIFT", "24.5 pp", "#a45f00"),
    ]
    for i, (label, value, colour) in enumerate(cards):
        x = 60 + i * 266
        box(draw, (x, 250, x + 246, 370))
        text(draw, (x + 18, 272), label, 12, "#657587", True)
        text(draw, (x + 18, 312), value, 23, colour, True)
    box(draw, (60, 400, 1380, 510), "#fff8e9", "#d59635")
    text(draw, (85, 425), "AUTHORITY BOUNDARY", 15, "#8d5400", True)
    text(draw, (85, 461), "The model completes analysis, but temporal shift and high-band miscalibration prevent authority to act.", 18, "#493a24")

    box(draw, (60, 540, 690, 920))
    text(draw, (85, 565), "Validation evidence", 22, bold=True)
    chart_x, chart_y, chart_w, chart_h = 110, 650, 520, 210
    draw.line((chart_x, chart_y, chart_x, chart_y + chart_h), fill="#9aa8b5", width=2)
    draw.line((chart_x, chart_y + chart_h, chart_x + chart_w, chart_y + chart_h), fill="#9aa8b5", width=2)
    bar_values = [("ROC AUC", metrics["roc_auc"]), ("Avg precision", metrics["average_precision"]), ("Balanced acc.", metrics["balanced_accuracy_at_0_5"])]
    for i, (label, value) in enumerate(bar_values):
        x0 = chart_x + 45 + i * 165
        height = int(value * chart_h)
        draw.rounded_rectangle((x0, chart_y + chart_h - height, x0 + 85, chart_y + chart_h), radius=5, fill=["#177ddc", "#16815d", "#a45f00"][i])
        text(draw, (x0 + 42, chart_y + chart_h - height - 28), f"{value:.3f}", 14, anchor="ma")
        text(draw, (x0 + 42, chart_y + chart_h + 17), label, 12, "#657587", anchor="ma")

    box(draw, (720, 540, 1380, 920))
    text(draw, (745, 565), "Calibration reliability", 22, bold=True)
    left, top, width, height = 790, 635, 500, 220
    draw.line((left, top, left, top + height), fill="#9aa8b5", width=2)
    draw.line((left, top + height, left + width, top + height), fill="#9aa8b5", width=2)
    draw.line((left, top + height, left + width, top), fill="#9aa8b5", width=2)
    bins = metrics["calibration"]["bins"]
    points = [(left + int(b["mean_prediction"] * width), top + height - int(b["observed_rate"] * height)) for b in bins]
    if len(points) > 1:
        draw.line(points, fill="#177ddc", width=4)
    for x, y in points:
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill="#177ddc")
    text(draw, (745, 875), "Worst bin gap 0.321 · high scores are overconfident", 15, "#8d5400", True)

    box(draw, (60, 950, 1380, 1290))
    text(draw, (85, 975), "Threshold consequences — illustrative, not authorised", 22, bold=True)
    rows = metrics["threshold_analysis"]["rows"]
    headers = [(90, "Threshold"), (260, "Flagged"), (455, "Precision"), (650, "Recall"), (845, "Specificity"), (1070, "Illustrative cost")]
    for x, label in headers:
        text(draw, (x, 1025), label.upper(), 12, "#657587", True)
    for i, row in enumerate(rows[:5]):
        y = 1060 + i * 42
        if i % 2 == 0:
            draw.rectangle((80, y - 8, 1360, y + 30), fill="#f4f7fa")
        values = [f"{row['threshold']:.2f}", f"{row['flagged_count']:,}", f"{row['precision']:.3f}", f"{row['recall']:.3f}", f"{row['specificity']:.3f}", f"{row['illustrative_cost']:,.0f}"]
        for (x, _), value in zip(headers, values):
            text(draw, (x, y), value, 14)

    box(draw, (60, 1320, 1380, 1645), "#071b31", "#071b31")
    text(draw, (90, 1350), "WHAT A2 PROVED", 15, "#91c5ef", True)
    text(draw, (90, 1395), "A2 found bounded retrospective ranking value.", 24, "white", True)
    text(draw, (90, 1440), "It also found where the evidence ceased to justify execution.", 24, "#ffd185", True)
    bullets = [
        "Post-contact duration excluded before fitting",
        "24.5-point train/holdout prevalence shift preserved as a warning",
        "Target copies and corrupted labels fail closed even with approval",
        "Final state: REQUEST_HUMAN_REVIEW",
    ]
    for i, value in enumerate(bullets):
        text(draw, (110, 1500 + i * 34), "• " + value, 16, "#c7d9e9")
    image.save(PORTFOLIO / "dashboard-preview.png", optimize=True)


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    PORTFOLIO.mkdir(exist_ok=True)
    architecture(report)
    dashboard(report)
    print(PORTFOLIO / "A2_ARCHITECTURE_PLATE.png")
    print(PORTFOLIO / "dashboard-preview.png")


if __name__ == "__main__":
    main()
