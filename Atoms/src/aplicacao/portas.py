# Atoms/aplicacao/portas.py
# pylint: disable=too-few-public-methods

"""Interfaces abstratas (portas) para a aplicação."""

from abc import ABC, abstractmethod
from typing import Sequence
from dominio.entidades import Bookmark


class BookmarkRepositorio(ABC):
    """Contrato para repositórios de bookmarks."""
    @abstractmethod
    def buscar_arquivos_html(self) -> Sequence[Bookmark]:
        """Retorna todos os bookmarks."""


class Conversor(ABC):
    """Contrato para conversão de bookmarks para outros formatos."""
    @abstractmethod
    def converter(self, bookmarks: Sequence[Bookmark]) -> str:
        """Converte uma lista de bookmarks para string (ex: Markdown)."""


class OrquestradorClient(ABC):
    """Contrato para cliente HTTP que chama outras APIs."""
    @abstractmethod
    def buscar(self) -> Sequence[Bookmark]:
        """Busca bookmarks de uma fonte externa."""
