# Atoms/backend/infrastructure/exporters/__init__.py

"""Exportadores concretos (CSV, JSON, PDF)."""

import logging

from .csv_exporter import CSVExporter
from .json_exporter import JSONExporter
from .pdf_exporter import PDFExporter

logger: logging.Logger = logging.getLogger(name=__name__)
logger.addHandler(logging.NullHandler())
logger.debug("Pacote 'exporters' carregado.")

__all__: list[str] = ["CSVExporter", "JSONExporter", "PDFExporter"]
