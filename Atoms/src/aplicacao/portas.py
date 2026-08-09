# Atoms/aplicacao/portas.py
# pylint: disable=too-few-public-methods

"""Interfaces abstratas (portas) para a aplicação."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from dominio.entidades import TagExtraida


class Diretorio(ABC):
    """Contrato para repositórios de arquivos html."""
    @abstractmethod
    def buscar_arquivos_html(self) -> Sequence[TagExtraida]:
        """Retorna todos os arquivos html."""


class Conversor(ABC):
    """Contrato para conversão de arquivos html para outros formatos."""
    @abstractmethod
    def converter(self, arquivos_html: Sequence[TagExtraida]) -> str:
        """Converte uma lista de arquivos html para string (ex: Markdown)."""


class OrquestradorClient(ABC):
    """Contrato para cliente HTTP que chama outras APIs."""
    @abstractmethod
    def buscar(self) -> Sequence[TagExtraida]:
        """Busca arquivos html de uma fonte externa."""
