# Atoms/backend/core/interfaces/bookmark_parser.py

"""Interface para análise de arquivos de favoritos."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_bookmark import Favorito

logger: logging.Logger = logging.getLogger(name=__name__)


class FavoritoParser(ABC):
    """Define como extrair favoritos de um arquivo."""

    @abstractmethod
    def analisar_arquivo(self, arquivo: ModeloArquivo) -> list[Favorito]:
        """Extrai todos os favoritos de um arquivo HTML."""

    @abstractmethod
    def suporta_arquivo(self, arquivo: ModeloArquivo) -> bool:
        """Verifica se o analisador é capaz de processar o arquivo informado."""

    def parse_file(self, arquivo_atual: ModeloArquivo) -> list[Favorito]:
        """Alias de compatibilidade para `analisar_arquivo`."""
        logger.debug(
            "Usando alias 'parse_file' para analisar %s", arquivo_atual.caminho_arquivo
        )
        return self.analisar_arquivo(arquivo=arquivo_atual)

    def supports_file(self, arquivo_atual: ModeloArquivo) -> bool:
        """Alias de compatibilidade para `suporta_arquivo`."""
        logger.debug(
            "Usando alias 'supports_file' para verificar %s",
            arquivo_atual.caminho_arquivo,
        )
        return self.suporta_arquivo(arquivo=arquivo_atual)
