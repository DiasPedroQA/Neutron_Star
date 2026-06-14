# core/interfaces/file_scanner.py

"""Interface para escaneamento de diretórios em busca de arquivos HTML."""

from __future__ import annotations

from abc import ABC, abstractmethod

from Atoms.backend.core.entidades.entidade_arquivo import ModeloArquivo
from Atoms.backend.core.entidades.entidade_diretorio import ModeloPasta


class FileScanner(ABC):
    """Define as operações de varredura do sistema de arquivos."""

    @abstractmethod
    def scan_directory(self, pasta_home: ModeloPasta) -> None:
        """Preenche a estrutura de pastas a partir do diretório raiz."""

    @abstractmethod
    def find_html_files(self, pasta: ModeloPasta) -> list[ModeloArquivo]:
        """Retorna todos os arquivos HTML encontrados na árvore de pastas."""
