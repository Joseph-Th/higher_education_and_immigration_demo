"""Build the reviewer-facing PowerPoint management briefing.

The deck is a downstream presentation artifact. All metrics are read from the
validated CSV/JSON outputs produced by the analytical pipeline; the PPTX never
becomes an analytical authority.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
DELIVERABLE = ROOT / "deliverables" / "management_briefing_deck.pptx"
PUBLIC_COPY = ROOT / "site" / "downloads" / "management_briefing_deck.pptx"
MANIFEST = ROOT / "deliverables" / "management_briefing_manifest.json"

SOURCE_PATHS = (
    "data/processed/national_year.csv",
    "data/processed/state_change_summary.csv",
    "data/processed/control_year.csv",
    "data/processed/institution_change_summary.csv",
    "data/undergraduate_shift_baseline.csv",
    "data/findings.json",
    "data/latest_update_review.json",
    "data/qa_resolution_summary.json",
    "data/medium_qa_resolution_summary.json",
)

SLIDE_W = 13.333
SLIDE_H = 7.5
FONT = "Aptos"

NAVY = RGBColor(0x10, 0x26, 0x3C)
INK = RGBColor(0x14, 0x26, 0x39)
INK_SOFT = RGBColor(0x5D, 0x6D, 0x7E)
ACCENT = RGBColor(0x0B, 0x77, 0x6E)
ACCENT_DARK = RGBColor(0x07, 0x56, 0x4F)
ACCENT_LIGHT = RGBColor(0xE8, 0xF3, 0xF1)
WARM = RGBColor(0xC7, 0x6B, 0x3B)
WARM_LIGHT = RGBColor(0xFA, 0xEE, 0xE8)
PAPER = RGBColor(0xFB, 0xFC, 0xFD)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
WASH = RGBColor(0xF0, 0xF4, 0xF7)
LINE = RGBColor(0xD9, 0xE1, 0xE8)
MUTED = RGBColor(0x9F, 0xB0, 0xC0)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fmt_int(value: int, signed: bool = False) -> str:
    if signed:
        return f"{value:+,}"
    return f"{value:,}"


def fmt_pct(value: float, signed: bool = False) -> str:
    if signed:
        return f"{value:+.1f}%"
    return f"{value:.1f}%"


def add_box(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fill: RGBColor = WHITE,
    line: RGBColor = LINE,
    radius: bool = True,
):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        Inches(x),
        Inches(y),
        Inches(w),
        Inches(h),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line
    shape.line.width = Pt(0.8)
    return shape


def add_text(
    slide,
    text: str,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    size: float = 18,
    color: RGBColor = INK,
    bold: bool = False,
    align: PP_ALIGN = PP_ALIGN.LEFT,
    valign: MSO_ANCHOR = MSO_ANCHOR.TOP,
    margin: float = 0.0,
    font: str = FONT,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(margin)
    frame.margin_right = Inches(margin)
    frame.margin_top = Inches(margin)
    frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = valign
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    paragraph.space_after = Pt(0)
    run = paragraph.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def add_rule(slide, x: float, y: float, w: float, color: RGBColor = LINE, width: float = 1.0) -> None:
    connector = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT,
        Inches(x),
        Inches(y),
        Inches(x + w),
        Inches(y),
    )
    connector.line.color.rgb = color
    connector.line.width = Pt(width)


def add_footer(slide, number: int, source: str = "IPEDS Fall Enrollment · portfolio demonstration") -> None:
    add_rule(slide, 0.65, 7.12, 12.0, LINE, 0.8)
    add_text(slide, source, 0.68, 7.16, 9.8, 0.18, size=7.5, color=INK_SOFT)
    add_text(slide, str(number), 12.15, 7.14, 0.45, 0.2, size=8, color=INK_SOFT, align=PP_ALIGN.RIGHT)


def add_heading(slide, kicker: str, title: str, subtitle: str | None = None) -> None:
    add_text(slide, kicker.upper(), 0.68, 0.46, 4.0, 0.24, size=9, color=ACCENT_DARK, bold=True)
    if len(title) > 62:
        title_y, title_h, title_size, subtitle_y = 0.78, 0.82, 24, 1.62
    else:
        title_y, title_h, title_size, subtitle_y = 0.82, 0.62, 28, 1.42
    add_text(
        slide,
        title,
        0.68,
        title_y,
        11.75,
        title_h,
        size=title_size,
        color=NAVY,
        bold=True,
    )
    if subtitle:
        add_text(slide, subtitle, 0.68, subtitle_y, 11.65, 0.3, size=12.5, color=INK_SOFT)


def add_kpi_card(slide, x: float, y: float, w: float, label: str, value: str, detail: str, *, dark: bool = False) -> None:
    fill = NAVY if dark else WHITE
    line = NAVY if dark else LINE
    label_color = MUTED if dark else INK_SOFT
    value_color = WHITE if dark else NAVY
    detail_color = RGBColor(0xD4, 0xDE, 0xE7) if dark else INK_SOFT
    add_box(slide, x, y, w, 1.33, fill=fill, line=line)
    add_text(slide, label.upper(), x + 0.18, y + 0.16, w - 0.36, 0.24, size=8, color=label_color, bold=True)
    add_text(slide, value, x + 0.18, y + 0.49, w - 0.36, 0.42, size=23, color=value_color, bold=True)
    add_text(slide, detail, x + 0.18, y + 0.98, w - 0.36, 0.2, size=8.5, color=detail_color)


def add_bullet(slide, x: float, y: float, w: float, title: str, body: str, *, index: str | None = None) -> None:
    if index:
        add_text(slide, index, x, y + 0.02, 0.34, 0.24, size=9, color=ACCENT_DARK, bold=True)
        tx = x + 0.42
        tw = w - 0.42
    else:
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y + 0.08), Inches(0.09), Inches(0.09))
        dot.fill.solid()
        dot.fill.fore_color.rgb = ACCENT
        dot.line.color.rgb = ACCENT
        tx = x + 0.18
        tw = w - 0.18
    add_text(slide, title, tx, y, tw, 0.27, size=12, color=NAVY, bold=True)
    add_text(slide, body, tx, y + 0.31, tw, 0.5, size=9.5, color=INK_SOFT)


def add_horizontal_bar(
    slide,
    *,
    label: str,
    value: int,
    max_abs: int,
    x: float,
    y: float,
    w: float,
    positive_color: RGBColor = ACCENT,
    negative_color: RGBColor = WARM,
) -> None:
    add_text(slide, label, x, y, 0.58, 0.22, size=9, color=NAVY, bold=True)
    track_x = x + 0.72
    track_w = w - 1.65
    add_box(slide, track_x, y + 0.02, track_w, 0.16, fill=WASH, line=WASH, radius=False)
    bar_w = max(0.06, track_w * abs(value) / max_abs)
    add_box(
        slide,
        track_x,
        y + 0.02,
        bar_w,
        0.16,
        fill=positive_color if value >= 0 else negative_color,
        line=positive_color if value >= 0 else negative_color,
        radius=False,
    )
    add_text(slide, fmt_int(value, signed=True), x + w - 0.9, y - 0.02, 0.88, 0.24, size=8.5, color=INK_SOFT, bold=True, align=PP_ALIGN.RIGHT)


def add_diverging_change_row(
    slide,
    *,
    label: str,
    value: int,
    max_abs: int,
    x: float,
    y: float,
    w: float,
    net: bool = False,
) -> None:
    label_w = 1.34
    value_w = 1.02
    track_x = x + label_w + 0.18
    track_w = w - label_w - value_w - 0.38
    center_x = track_x + track_w / 2
    half_w = track_w / 2 - 0.04
    extent = max(0.05, half_w * abs(value) / max_abs)
    bar_x = center_x if value >= 0 else center_x - extent
    bar_color = NAVY if net else (ACCENT if value >= 0 else WARM)

    add_text(slide, label, x, y - 0.02, label_w, 0.24, size=9.2, color=NAVY, bold=True)
    add_box(slide, track_x, y + 0.02, track_w, 0.16, fill=WASH, line=WASH, radius=False)
    center = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT,
        Inches(center_x),
        Inches(y - 0.02),
        Inches(center_x),
        Inches(y + 0.22),
    )
    center.line.color.rgb = MUTED
    center.line.width = Pt(0.8)
    add_box(slide, bar_x, y + 0.02, extent, 0.16, fill=bar_color, line=bar_color, radius=False)
    add_text(
        slide,
        fmt_int(value, signed=True),
        x + w - value_w,
        y - 0.03,
        value_w,
        0.24,
        size=9.0,
        color=NAVY if net else INK_SOFT,
        bold=True,
        align=PP_ALIGN.RIGHT,
    )


def add_line_chart(slide, rows: list[dict[str, str]], x: float, y: float, w: float, h: float) -> None:
    values = [int(row["nonresident_enrollment"]) for row in rows]
    years = [int(row["year"]) for row in rows]
    low = min(values) - 20_000
    high = max(values) + 20_000
    grid_values = [850_000, 950_000, 1_050_000]

    plot_x = x + 0.74
    plot_y = y + 0.36
    plot_w = w - 1.02
    plot_h = h - 0.92

    for grid in grid_values:
        gy = plot_y + plot_h - ((grid - low) / (high - low)) * plot_h
        add_rule(slide, plot_x, gy, plot_w, LINE, 0.7)
        add_text(slide, f"{grid / 1_000_000:.2f}m", x + 0.02, gy - 0.08, 0.56, 0.18, size=7.5, color=INK_SOFT, align=PP_ALIGN.RIGHT)

    points: list[tuple[float, float]] = []
    for index, value in enumerate(values):
        px = plot_x + (plot_w * index / (len(values) - 1))
        py = plot_y + plot_h - ((value - low) / (high - low)) * plot_h
        points.append((px, py))
        if index in {0, len(values) - 1} or years[index] in {2020, 2022}:
            add_text(slide, str(years[index]), px - 0.25, plot_y + plot_h + 0.1, 0.5, 0.18, size=7.5, color=INK_SOFT, align=PP_ALIGN.CENTER)

    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        connector = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT,
            Inches(x1),
            Inches(y1),
            Inches(x2),
            Inches(y2),
        )
        connector.line.color.rgb = ACCENT
        connector.line.width = Pt(2.6)

    for index, (px, py) in enumerate(points):
        marker = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(px - 0.055), Inches(py - 0.055), Inches(0.11), Inches(0.11))
        marker.fill.solid()
        marker.fill.fore_color.rgb = WHITE if index != len(points) - 1 else ACCENT
        marker.line.color.rgb = ACCENT
        marker.line.width = Pt(1.4)

    latest_x, latest_y = points[-1]
    add_text(slide, fmt_int(values[-1]), latest_x - 0.5, latest_y - 0.42, 1.0, 0.25, size=10.5, color=NAVY, bold=True, align=PP_ALIGN.CENTER)


def make_deck() -> tuple[Presentation, dict[str, object]]:
    national = read_csv(PROCESSED / "national_year.csv")
    findings = json.loads((DATA / "findings.json").read_text(encoding="utf-8"))
    update = json.loads((DATA / "latest_update_review.json").read_text(encoding="utf-8"))
    qa_resolution = json.loads((DATA / "qa_resolution_summary.json").read_text(encoding="utf-8"))
    medium_qa_resolution = json.loads((DATA / "medium_qa_resolution_summary.json").read_text(encoding="utf-8"))
    undergraduate_baseline = read_csv(DATA / "undergraduate_shift_baseline.csv")

    headline = findings["headline"]
    latest = national[-1]
    prior = national[-2]
    recovery = findings["recovery"]
    level = findings["level_decomposition"]
    control = findings["institution_control"]["changes"]
    dynamics = findings["institution_dynamics"]["decade"]
    if len(undergraduate_baseline) != 51:
        raise RuntimeError("Management deck requires the complete 51-state/DC undergraduate baseline")
    baseline_undergraduate_change = sum(int(row["undergraduate_change"]) for row in undergraduate_baseline)
    baseline_positive_states = sum(int(row["undergraduate_change"]) > 0 for row in undergraduate_baseline)
    baseline_public_change = sum(int(row["public_undergraduate_change"]) for row in undergraduate_baseline)
    if baseline_undergraduate_change != update["national"]["undergraduate_change"]:
        raise RuntimeError("Management deck undergraduate baseline does not reconcile to latest-year change")
    total_claim_holds = qa_resolution["hold_for_confirmation"] + medium_qa_resolution["hold_for_confirmation"]

    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)
    prs.core_properties.title = "U.S. Nonresident Enrollment Management Briefing"
    prs.core_properties.subject = "Portfolio management briefing generated from validated IPEDS outputs"
    prs.core_properties.author = "Portfolio demonstration"
    prs.core_properties.keywords = "IPEDS, analyst, PowerPoint, management briefing, portfolio"
    prs.core_properties.comments = "Downstream presentation artifact; validated CSV/JSON outputs remain authoritative."
    prs.core_properties.created = datetime(2026, 10, 13, tzinfo=timezone.utc)
    prs.core_properties.modified = datetime(2026, 10, 13, tzinfo=timezone.utc)

    blank = prs.slide_layouts[6]

    # Slide 1: executive summary
    slide = prs.slides.add_slide(blank)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = PAPER
    add_heading(slide, "U.S. nonresident enrollment · executive summary", "2024 growth shifted toward undergraduates.", "Long-run recovery is still graduate-heavy and uneven across states.")
    add_kpi_card(slide, 0.68, 2.05, 2.85, "2024 enrollment", fmt_int(int(latest["nonresident_enrollment"])), f"{fmt_pct(float(latest['nonresident_share_pct']))} of total enrollment", dark=True)
    add_kpi_card(slide, 3.68, 2.05, 2.85, "2023 → 2024", fmt_int(update["national"]["absolute_change"], signed=True), fmt_pct(update["national"]["pct_change"], signed=True))
    add_kpi_card(slide, 6.68, 2.05, 2.85, "Undergraduate change", fmt_int(update["national"]["undergraduate_change"], signed=True), f"{baseline_positive_states} of 51 states/DC increased")
    add_kpi_card(slide, 9.68, 2.05, 2.85, "2015 → 2024", fmt_int(headline["change_since_2015"], signed=True), fmt_pct(headline["change_since_2015_pct"], signed=True))

    add_box(slide, 0.68, 3.7, 7.55, 2.75, fill=WHITE, line=LINE)
    add_text(slide, "What changed from 2023 to 2024?", 0.98, 3.98, 4.6, 0.32, size=15, color=NAVY, bold=True)
    add_text(slide, "Change in U.S. nonresident enrollment by student level", 0.98, 4.31, 5.5, 0.22, size=9, color=INK_SOFT)
    latest_max = max(abs(update["national"]["undergraduate_change"]), abs(update["national"]["graduate_change"]), abs(update["national"]["absolute_change"]))
    add_diverging_change_row(slide, label="Undergraduate", value=update["national"]["undergraduate_change"], max_abs=latest_max, x=0.98, y=4.76, w=6.85)
    add_diverging_change_row(slide, label="Graduate", value=update["national"]["graduate_change"], max_abs=latest_max, x=0.98, y=5.27, w=6.85)
    add_diverging_change_row(slide, label="Net change", value=update["national"]["absolute_change"], max_abs=latest_max, x=0.98, y=5.78, w=6.85, net=True)

    add_box(slide, 8.48, 3.7, 4.2, 2.75, fill=NAVY, line=NAVY)
    add_text(slide, "LATEST-YEAR READ", 8.8, 3.98, 2.8, 0.22, size=8.5, color=RGBColor(0x8E, 0xD9, 0xD0), bold=True)
    add_text(slide, fmt_int(baseline_public_change, signed=True), 8.8, 4.4, 2.4, 0.4, size=22, color=WHITE, bold=True)
    add_text(slide, "undergraduate change at public institutions", 8.8, 4.82, 3.2, 0.35, size=9.2, color=RGBColor(0xD4, 0xDE, 0xE7))
    add_rule(slide, 8.8, 5.3, 3.1, RGBColor(0x3A, 0x4B, 0x5B), 1.0)
    add_text(slide, fmt_int(update["institution_accounting"]["continuing_change"], signed=True), 8.8, 5.55, 2.4, 0.38, size=20, color=RGBColor(0x8E, 0xD9, 0xD0), bold=True)
    add_text(slide, "change at continuing institutions", 8.8, 5.92, 3.2, 0.3, size=9.2, color=RGBColor(0xD4, 0xDE, 0xE7))
    add_footer(slide, 1)

    # Slide 2: national trend
    slide = prs.slides.add_slide(blank)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = PAPER
    add_heading(slide, "National trend", "Enrollment recovered above 2015 levels after the 2020 shock.", "The decade result is positive, but the student-level mix changed substantially.")
    add_box(slide, 0.68, 1.98, 8.25, 4.82, fill=WHITE, line=LINE)
    add_text(slide, "U.S. nonresident enrollment, 2015–2024", 0.98, 2.18, 5.2, 0.3, size=13, color=NAVY, bold=True)
    add_text(slide, "students", 0.98, 2.5, 1.0, 0.18, size=8, color=INK_SOFT)
    add_line_chart(slide, national, 0.96, 2.62, 7.62, 3.74)
    add_box(slide, 9.15, 1.98, 3.53, 4.82, fill=NAVY, line=NAVY)
    add_text(slide, "DECADE COMPOSITION", 9.48, 2.27, 2.8, 0.22, size=8.5, color=RGBColor(0x8E, 0xD9, 0xD0), bold=True)
    add_text(slide, "Graduate", 9.48, 2.82, 1.5, 0.24, size=10, color=MUTED, bold=True)
    add_text(slide, fmt_int(level["graduate_change_students"], signed=True), 9.48, 3.08, 2.75, 0.45, size=23, color=WHITE, bold=True)
    add_text(slide, fmt_pct(level["graduate_change_pct"], signed=True), 9.48, 3.5, 2.5, 0.22, size=9.5, color=RGBColor(0xD4, 0xDE, 0xE7))
    add_rule(slide, 9.48, 3.93, 2.75, RGBColor(0x3A, 0x4B, 0x5B), 1.0)
    add_text(slide, "Undergraduate", 9.48, 4.24, 1.8, 0.24, size=10, color=MUTED, bold=True)
    add_text(slide, fmt_int(level["undergraduate_change_students"], signed=True), 9.48, 4.5, 2.75, 0.45, size=23, color=WHITE, bold=True)
    add_text(slide, fmt_pct(level["undergraduate_change_pct"], signed=True), 9.48, 4.92, 2.5, 0.22, size=9.5, color=RGBColor(0xD4, 0xDE, 0xE7))
    add_text(slide, "Net decade change", 9.48, 5.55, 1.8, 0.22, size=9, color=MUTED, bold=True)
    add_text(slide, fmt_int(level["net_change_students"], signed=True), 9.48, 5.84, 2.75, 0.42, size=22, color=RGBColor(0x8E, 0xD9, 0xD0), bold=True)
    add_footer(slide, 2)

    # Slide 3: geography
    slide = prs.slides.add_slide(blank)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = PAPER
    add_heading(slide, "Geography", "Recovery is broad, but not uniform across states.", "Change below is relative to the 2019 pre-pandemic baseline.")
    add_box(slide, 0.68, 1.95, 12.0, 4.92, fill=WHITE, line=LINE)
    add_box(slide, 0.98, 2.2, 2.2, 0.72, fill=ACCENT_LIGHT, line=ACCENT_LIGHT)
    add_text(slide, f"{recovery['states_at_or_above_baseline']} of 51", 1.13, 2.37, 1.9, 0.25, size=16, color=ACCENT_DARK, bold=True)
    add_text(slide, "at or above 2019", 1.13, 2.62, 1.9, 0.18, size=8.5, color=ACCENT_DARK)
    add_text(slide, "Largest gains", 0.98, 3.18, 4.2, 0.28, size=13, color=NAVY, bold=True)
    gains = recovery["largest_gains"][:5]
    gain_max = max(abs(item["absolute_change"]) for item in gains)
    for idx, item in enumerate(gains):
        add_horizontal_bar(slide, label=item["state"], value=item["absolute_change"], max_abs=gain_max, x=0.98, y=3.65 + idx * 0.5, w=5.25)

    add_text(slide, "Largest shortfalls", 6.75, 3.18, 4.2, 0.28, size=13, color=NAVY, bold=True)
    shortfalls = recovery["largest_shortfalls"][:5]
    short_max = max(abs(item["absolute_change"]) for item in shortfalls)
    for idx, item in enumerate(shortfalls):
        add_horizontal_bar(slide, label=item["state"], value=item["absolute_change"], max_abs=short_max, x=6.75, y=3.65 + idx * 0.5, w=5.25)
    add_text(slide, "Interpretation: the national recovery does not imply a uniform state pattern. California remains the largest absolute shortfall from 2019, while Illinois and Texas show the largest gains.", 0.98, 6.25, 10.95, 0.4, size=9.5, color=INK_SOFT)
    add_footer(slide, 3)

    # Slide 4: drivers
    slide = prs.slides.add_slide(blank)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = PAPER
    add_heading(slide, "Drivers", "Private nonprofit growth offset declines in the other control sectors.", "Institution-universe accounting shows where the decade increase actually came from.")
    add_box(slide, 0.68, 1.98, 5.7, 4.82, fill=WHITE, line=LINE)
    add_text(slide, "Change by institutional control, 2015–2024", 0.98, 2.23, 4.8, 0.3, size=13, color=NAVY, bold=True)
    max_control = max(abs(item["absolute_change"]) for item in control)
    for idx, item in enumerate(control):
        add_horizontal_bar(slide, label=item["control"].replace("Private ", "Priv. "), value=item["absolute_change"], max_abs=max_control, x=0.98, y=2.95 + idx * 0.72, w=4.95)
    add_text(slide, "Private nonprofit institutions increased by 82,825 students and shifted the national control mix toward nonprofit institutions.", 0.98, 5.55, 4.9, 0.8, size=10, color=INK_SOFT)

    add_box(slide, 6.62, 1.98, 6.06, 4.82, fill=NAVY, line=NAVY)
    add_text(slide, "INSTITUTION-UNIVERSE ACCOUNTING", 6.98, 2.26, 4.9, 0.22, size=8.5, color=RGBColor(0x8E, 0xD9, 0xD0), bold=True)
    add_text(slide, "Continuing institutions", 6.98, 2.85, 2.25, 0.22, size=9.5, color=MUTED, bold=True)
    add_text(slide, fmt_int(dynamics["continuing_change"], signed=True), 9.6, 2.68, 2.5, 0.45, size=23, color=WHITE, bold=True, align=PP_ALIGN.RIGHT)
    add_rule(slide, 6.98, 3.38, 4.7, RGBColor(0x3A, 0x4B, 0x5B), 1.0)
    add_text(slide, "Universe entry / exit", 6.98, 3.76, 2.35, 0.22, size=9.5, color=MUTED, bold=True)
    add_text(slide, fmt_int(dynamics["entry_exit_net"], signed=True), 9.6, 3.59, 2.5, 0.45, size=23, color=WHITE, bold=True, align=PP_ALIGN.RIGHT)
    add_rule(slide, 6.98, 4.29, 4.7, RGBColor(0x3A, 0x4B, 0x5B), 1.0)
    add_text(slide, "National decade change", 6.98, 4.69, 2.35, 0.22, size=9.5, color=RGBColor(0xD4, 0xDE, 0xE7), bold=True)
    add_text(slide, fmt_int(dynamics["national_change"], signed=True), 9.6, 4.49, 2.5, 0.48, size=25, color=RGBColor(0x8E, 0xD9, 0xD0), bold=True, align=PP_ALIGN.RIGHT)
    add_text(slide, "The increase was created inside continuing institutions, not by adding more institutions to the analytic universe.", 6.98, 5.45, 4.75, 0.85, size=10.5, color=RGBColor(0xD4, 0xDE, 0xE7))
    add_footer(slide, 4)

    # Slide 5: publication decision / QA
    slide = prs.slides.add_slide(blank)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = PAPER
    add_heading(slide, "Publication judgment", "The aggregate result is publishable. Ten institution claims remain held.", "Automated flags trigger evidence review; unresolved institution interpretation stays out of public narrative.")
    add_kpi_card(slide, 0.68, 2.02, 3.75, "High-priority reviewed", f"{qa_resolution['reviewed_count']}/{qa_resolution['high_priority_total']}", f"{qa_resolution['safe_with_context']} safe with context · {qa_resolution['hold_for_confirmation']} held")
    add_kpi_card(slide, 4.62, 2.02, 3.75, "Medium-priority reviewed", f"{medium_qa_resolution['reviewed_count']}/{medium_qa_resolution['medium_priority_total']}", f"{medium_qa_resolution['safe_with_context']} safe with context · {medium_qa_resolution['hold_for_confirmation']} held")
    add_kpi_card(slide, 8.56, 2.02, 4.12, "Institution-specific claims held", str(total_claim_holds), "retained in aggregates · excluded from unsupported narrative", dark=True)

    add_box(slide, 0.68, 3.67, 5.85, 3.05, fill=WHITE, line=LINE)
    add_text(slide, "What can be used now", 1.0, 3.94, 4.8, 0.32, size=14, color=NAVY, bold=True)
    add_bullet(slide, 1.0, 4.48, 4.75, "Aggregate direction", f"2024 enrollment increased {fmt_int(update['national']['absolute_change'], signed=True)} ({fmt_pct(update['national']['pct_change'], signed=True)}), led by undergraduate growth.")
    add_bullet(slide, 1.0, 5.2, 4.75, "Geographic context", f"{recovery['states_at_or_above_baseline']} states/DC are at or above 2019; {recovery['states_below_baseline']} remain below.")
    add_bullet(slide, 1.0, 5.92, 4.75, "Next-release persistence gate", "Call the undergraduate shift broadly persistent only if the next complete release is positive nationally and in at least 26 of 51 states/DC.")

    add_box(slide, 6.78, 3.67, 5.9, 3.05, fill=WASH, line=LINE)
    add_text(slide, "Guardrails before reuse", 7.1, 3.94, 4.9, 0.32, size=14, color=NAVY, bold=True)
    guardrails = [
        ("Population", "IPEDS U.S. nonresident is not interchangeable with immigrant-origin, undocumented, refugee/asylee, or all international-student populations."),
        ("Vintage", "2024 is treated as provisional and can differ slightly from earlier Digest releases built from earlier files."),
        ("Authority", "CSV/JSON outputs remain authoritative; this PPTX, the Excel workbook, PDF, and website are downstream presentation artifacts."),
    ]
    for idx, (title, body) in enumerate(guardrails):
        add_bullet(slide, 7.1, 4.48 + idx * 0.72, 4.75, title, body, index=f"0{idx + 1}")
    add_footer(slide, 5)

    metrics = {
        "latest_nonresident": int(latest["nonresident_enrollment"]),
        "latest_year": int(latest["year"]),
        "latest_yoy_change": int(latest["nonresident_enrollment"]) - int(prior["nonresident_enrollment"]),
        "states_recovered": recovery["states_at_or_above_baseline"],
        "undergraduate_positive_states": baseline_positive_states,
        "undergraduate_latest_change": baseline_undergraduate_change,
        "decade_change": headline["change_since_2015"],
        "high_priority_reviewed": qa_resolution["reviewed_count"],
        "medium_priority_reviewed": medium_qa_resolution["reviewed_count"],
        "institution_claim_holds": total_claim_holds,
        "slide_count": len(prs.slides),
    }
    return prs, metrics


def main() -> int:
    DELIVERABLE.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_COPY.parent.mkdir(parents=True, exist_ok=True)

    prs, metrics = make_deck()
    prs.save(DELIVERABLE)
    payload = DELIVERABLE.read_bytes()
    if len(payload) < 40_000:
        raise RuntimeError(f"Generated PowerPoint is unexpectedly small: {len(payload)} bytes")
    if not payload.startswith(b"PK"):
        raise RuntimeError("Generated PowerPoint is not a ZIP-based Office package")

    shutil.copy2(DELIVERABLE, PUBLIC_COPY)
    if DELIVERABLE.read_bytes() != PUBLIC_COPY.read_bytes():
        raise RuntimeError("Public PowerPoint copy does not match canonical deliverable")

    source_hashes = {path: sha256(ROOT / path) for path in SOURCE_PATHS}
    manifest = {
        "builder": "scripts/build_management_deck.py",
        "builder_sha256": sha256(Path(__file__)),
        "source_sha256": source_hashes,
        "pptx_sha256": hashlib.sha256(payload).hexdigest(),
        "pptx_bytes": len(payload),
        "slide_count": len(prs.slides),
        "metrics": metrics,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {DELIVERABLE} ({len(payload):,} bytes; {len(prs.slides)} slides)")
    print(f"Wrote {MANIFEST}")
    print(f"Published exact copy to {PUBLIC_COPY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
