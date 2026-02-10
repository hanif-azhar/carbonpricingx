from __future__ import annotations

from io import BytesIO
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _summary_table(summary: Dict[str, Any]):
    rows = [["Metric", "Value"]]
    for key, value in summary.items():
        rows.append([str(key), str(value)])
    table = Table(rows, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0A7A5D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    return table


def build_pdf_report(payload: Dict[str, Any]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("CarbonPricingX Simulation Report", styles["Title"]))
    story.append(Spacer(1, 12))

    summary = payload.get("summary", {})
    if summary:
        story.append(Paragraph("Summary", styles["Heading2"]))
        story.append(_summary_table(summary))
        story.append(Spacer(1, 12))

    sections = payload.get("sections", {})
    for section_name, section_data in sections.items():
        story.append(Paragraph(str(section_name), styles["Heading3"]))
        if isinstance(section_data, dict):
            story.append(_summary_table(section_data))
        else:
            story.append(Paragraph(str(section_data), styles["BodyText"]))
        story.append(Spacer(1, 8))

    doc.build(story)
    return buffer.getvalue()
