# core/interfaces.py
# pylint: disable=unnecessary-pass

"""Contratos (interfaces) para o núcleo da aplicação."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from Atoms.backend.core.entities import ModeloArquivo, ModeloPasta


class FileScanner(ABC):
    """Interface: O QUE faz escaneamento de arquivos HTML."""

    @abstractmethod
    def scan_directory(self, pasta_home: ModeloPasta) -> None:
        """Escaneia diretório e preenche a estrutura de pastas/arquivos."""
        pass

    @abstractmethod
    def find_html_files(self, pasta: ModeloPasta) -> list[ModeloArquivo]:
        """Retorna lista de todos os arquivos HTML encontrados."""
        pass


class BookmarkParser(ABC):
    """Interface: O QUE extrai bookmarks de arquivos HTML."""

    @abstractmethod
    def parse_file(self, arquivo: ModeloArquivo) -> list[dict[str, Any]]:
        """Extrai bookmarks de um arquivo HTML."""
        pass


class BookmarkExporter(ABC):
    """Interface: O QUE exporta bookmarks para diferentes formatos."""

    @abstractmethod
    def export(self, bookmarks: list[dict[str, Any]], saida: Path) -> None:
        """Exporta bookmarks para um arquivo."""
        pass


class BookmarkRepository(ABC):
    """Interface: ONDE salvar/bookmarks (opcional, para persistência)."""

    @abstractmethod
    def save(self, bookmarks: list[dict[str, Any]], identifier: str) -> None:
        """Salva bookmarks com um identificador."""
        pass

    @abstractmethod
    def load(self, identifier: str) -> list[dict[str, Any]]:
        """Carrega bookmarks salvos anteriormente."""
        pass
