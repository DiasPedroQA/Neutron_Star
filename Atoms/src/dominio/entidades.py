# Atoms/dominio/entidades.py

"""Entidades centrais do domínio de bookmarks."""

from dataclasses import dataclass


@dataclass
class Bookmark:
    """Representa um marcador (favorito) com título e URL."""
    titulo: str
    url: str


@dataclass
class ArquivoTemp:
    """Representa um arquivo temporário com nome e conteúdo."""
    nome: str
    tamanho: int
    conteudo: str
