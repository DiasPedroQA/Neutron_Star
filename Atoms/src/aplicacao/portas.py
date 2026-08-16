# Atoms/src/aplicacao/portas.py
# pylint: disable=too-few-public-methods

"""Interfaces abstratas (portas) para a aplicação."""

from abc import ABC, abstractmethod
from pathlib import Path

from src.dominio.entidades import ArquivoTemp, TagExtraida  # Import sem "src"


class Diretorio(ABC):
    """Porta para operações de listagem de arquivos em um diretório."""

    @abstractmethod
    def buscar_arquivos_html(self) -> list[ArquivoTemp]:
        """Retorna uma lista de ArquivoTemp para cada arquivo HTML encontrado.

        Pode lançar:
            FileNotFoundError: se o diretório base não existir.
        """


class LeitorArquivo(ABC):
    """Porta para extração de tags de um arquivo HTML."""

    @abstractmethod
    def extrair_tags(self, caminho: Path) -> list[TagExtraida]:
        """Extrai todas as tags <a> do arquivo e retorna uma lista.

        Pode lançar:
            FileNotFoundError: se o arquivo não existir.
            ValueError: se o conteúdo não for HTML válido.
        """
