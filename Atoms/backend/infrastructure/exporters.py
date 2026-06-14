# Atoms/backend/infrastructure/exporters.py

"""Implementações concretas de exportadores de bookmarks."""

import csv
import json
import logging
from pathlib import Path

from reportlab.lib.styles import StyleSheet1

from Atoms.backend.core.entidades.entidade_bookmark import Bookmark
from Atoms.backend.core.interfaces.bookmark_exporter import BookmarkExporter

logger: logging.Logger = logging.getLogger(name=__name__)


class JSONExporter(BookmarkExporter):
    """Exporta bookmarks para JSON."""

    def get_supported_formats(self) -> list[str]:
        """Retorna os formatos suportados por este exportador."""
        return ["json"]

    def export(self, bookmarks: list[Bookmark], saida: Path) -> None:
        """Grava bookmarks em um arquivo JSON legível."""
        data: list[dict[str, str]] = [
            {
                "title": bm.title,
                "url": bm.url,
                "add_date": bm.add_date.isoformat(),
            }
            for bm in bookmarks
        ]
        with open(file=saida, mode="w", encoding="utf-8") as f:
            json.dump(obj=data, fp=f, indent=4, ensure_ascii=False)
        logger.info("Exportados %d bookmarks para JSON: %s", len(bookmarks), saida)


class CSVExporter(BookmarkExporter):
    """Exporta bookmarks para CSV."""

    def get_supported_formats(self) -> list[str]:
        """Retorna os formatos suportados por este exportador."""
        return ["csv"]

    def export(self, bookmarks: list[Bookmark], saida: Path) -> None:
        """Grava bookmarks em um arquivo CSV com cabeçalho."""
        if not bookmarks:
            logger.warning("Nenhum bookmark para exportar em CSV.")
            return

        with open(file=saida, mode="w", newline="", encoding="utf-8") as f:
            writer: csv.DictWriter[str] = csv.DictWriter(f, fieldnames=["title", "url", "add_date"])
            writer.writeheader()
            for bm in bookmarks:
                writer.writerow(
                    rowdict={
                        "title": bm.title,
                        "url": bm.url,
                        "add_date": bm.add_date.isoformat(),
                    }
                )
        logger.info("Exportados %d bookmarks para CSV: %s", len(bookmarks), saida)


class PDFExporter(BookmarkExporter):
    """Exporta bookmarks para PDF."""

    def get_supported_formats(self) -> list[str]:
        """Retorna os formatos suportados por este exportador."""
        return ["pdf"]

    def export(self, bookmarks: list[Bookmark], saida: Path) -> None:  # pylint: disable=import-outside-toplevel,too-many-locals
        """Gera um PDF contendo os bookmarks extraídos.

        O exportador carrega a dependência reportlab apenas no momento da execução.
        """
        try:
            from reportlab.lib.pagesizes import letter  # pylint: disable=import-outside-toplevel
            from reportlab.lib.styles import getSampleStyleSheet  # pylint: disable=import-outside-toplevel
            from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Spacer  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            logger.error("Dependência reportlab não encontrada: %s", exc)
            raise RuntimeError("PDF export requires the reportlab package.") from exc

        doc = SimpleDocTemplate(filename=str(saida), pagesize=letter)
        styles: StyleSheet1 = getSampleStyleSheet()
        story: list[Flowable] = []

        for bm in bookmarks[:200]:  # limite para não travar
            line: str = f"<b>{bm.title}</b><br/>" f"{bm.url}<br/>" f"<i>{bm.add_date.strftime('%Y-%m-%d %H:%M:%S')}</i>"
            story.extend(
                [
                    Paragraph(text=line, style=styles["Normal"]),
                    Spacer(width=1, height=12),
                ]
            )

        doc.build(flowables=story)
        logger.info("Exportados %d bookmarks para PDF: %s", len(bookmarks), saida)
