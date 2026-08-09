# Atoms/dominio/entidades.py

"""Entidades centrais do domínio de arquivos html."""

from dataclasses import dataclass


@dataclass
class TagExtraida:
    """Representa um marcador (favorito) com título e URL."""
    titulo: str
    url: str


@dataclass
class ArquivoTemp:
    """Representa um arquivo temporário com nome e conteúdo."""
    nome: str
    tamanho: int
    conteudo: str
