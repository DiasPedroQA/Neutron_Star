"""Portas (interfaces) da camada de aplicação do serviço de busca.

Regra de dependência do Clean Architecture: `aplicacao` depende só destas
abstrações, nunca de FastAPI, `pathlib` real ou bibliotecas de parsing.
Quem implementa a porta são os adaptadores de saída.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from dominio.entidades import Bookmark


class RepositorioFavoritos(Protocol):
    """Porta de saída: sabe descobrir e ler arquivos de favoritos em uma pasta."""

    def descobrir_arquivos(self, pasta: Path) -> list[Path]:
        """Retorna os caminhos dos arquivos de favoritos encontrados em `pasta`."""
        ...

    def ler_bookmarks(self, arquivo: Path) -> list[Bookmark]:
        """Faz o parsing de um arquivo de favoritos e retorna os `Bookmark` encontrados."""
        ...
