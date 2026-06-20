# Atoms/backend/core/interfaces/file_scanner.py

"""Interface para varredura de diretórios em busca de arquivos HTML."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_diretorio import ModeloPasta

logger: logging.Logger = logging.getLogger(name=__name__)


class FileScanner(ABC):
    """Define as operações de varredura do sistema de arquivos."""

    @abstractmethod
    def varrer_diretorio(self, pasta_raiz: ModeloPasta) -> None:
        """Preenche a estrutura de pastas a partir do diretório raiz."""

    @abstractmethod
    def localizar_arquivos_html(self, pasta: ModeloPasta) -> list[ModeloArquivo]:
        """Retorna todos os arquivos HTML encontrados na árvore de pastas."""

    def scan_directory(self, pasta_home: ModeloPasta) -> None:
        """Alias de compatibilidade para `varrer_diretorio`."""
        logger.debug(
            "Usando alias 'scan_directory' para varrer diretório: %s",
            pasta_home.caminho_absoluto,
        )
        self.varrer_diretorio(pasta_raiz=pasta_home)

    def find_html_files(self, pasta_atual: ModeloPasta) -> list[ModeloArquivo]:
        """Alias de compatibilidade para `localizar_arquivos_html`."""
        logger.debug(
            "Usando alias 'find_html_files' para localizar HTML em: %s",
            pasta_atual.caminho_absoluto,
        )
        return self.localizar_arquivos_html(pasta=pasta_atual)
