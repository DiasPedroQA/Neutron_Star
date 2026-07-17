from abc import ABC, abstractmethod
from pathlib import Path

from dominio.entidades import BookmarkFolder


class Exportador(ABC):  # pylint: disable=too-few-public-methods
    """Interface (Strategy) para exportadores de bookmarks."""

    @abstractmethod
    def exportar(self, raiz: BookmarkFolder, caminho_saida: Path | None = None) -> str | None:
        """Exporta a hierarquia de bookmarks para um formato específico.

        Args:
            raiz: Pasta raiz que contém toda a hierarquia de bookmarks.
            caminho_saida: Caminho onde o resultado será gravado, se fornecido.

        Returns:
            Conteúdo exportado como string, ou None para exportadores binários.
        """
