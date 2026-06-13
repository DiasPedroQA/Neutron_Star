# backend/exporters.py

"""Implementações concretas de exportadores de bookmarks."""

import csv
import json
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import StyleSheet1, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from Atoms.backend.core.interfaces import BookmarkExporter

# Seu código existente adaptado para a interface


class JSONExporter(BookmarkExporter):
    """Exporta bookmarks para JSON."""

    def export(self, bookmarks: list[dict[str, Any]], saida: Path) -> None:
        with open(saida, "w", encoding="utf-8") as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)


class CSVExporter(BookmarkExporter):
    """Exporta bookmarks para CSV."""

    def export(self, bookmarks: list[dict[str, Any]], saida: Path) -> None:
        if not bookmarks:
            return

        with open(saida, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "url", "add_date"])
            writer.writeheader()
            writer.writerows(bookmarks)


class PDFExporter(BookmarkExporter):
    """Exporta bookmarks para PDF (seu código existente)."""

    def export(self, bookmarks: list[dict[str, Any]], saida: Path) -> None:

        doc = SimpleDocTemplate(filename=str(saida), pagesize=letter)
        styles: StyleSheet1 = getSampleStyleSheet()
        story = []

        for bm in bookmarks[:200]:  # limite para não travar
            line = f"<b>{bm['title']}</b><br/>{bm['url']}<br/><i>{bm['add_date']}</i>"
            story.extend(
                [
                    Paragraph(line, styles["Normal"]),
                    Spacer(1, 12),
                ]
            )

        doc.build(story)
