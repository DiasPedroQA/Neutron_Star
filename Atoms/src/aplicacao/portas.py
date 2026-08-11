# Atoms/src/aplicacao/portas.py
# pylint: disable=too-few-public-methods

"""Interfaces abstratas (portas) para a aplicação."""

from abc import ABC, abstractmethod
from pathlib import Path

from dominio.entidades import ArquivoTemp, TagExtraida


class Diretorio(ABC):
    """Porta para operações de listagem de arquivos em um diretório."""

    @abstractmethod
    def buscar_arquivos_html(self) -> list[ArquivoTemp]:
        """Retorna uma lista de ArquivoTemp para cada arquivo HTML encontrado."""


class LeitorArquivo(ABC):
    """Porta para extração de tags de um arquivo HTML."""

    @abstractmethod
    def extrair_tags(self, caminho: Path) -> list[TagExtraida]:
        """Extrai todas as tags <a> do arquivo e retorna uma lista."""
