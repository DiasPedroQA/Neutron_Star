"""
Entidades do domínio de bookmarks.

Camada de domínio: não importa nada de `aplicacao` ou `adaptadores`,
não faz I/O e não conhece bibliotecas de parsing HTML ou de dados
(bs4, pandas). Apenas estrutura de dados e regras puras.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BookmarkNode:
    """Representa um nó na árvore de bookmarks (pasta ou link)."""

    tipo: str  # 'pasta' ou 'link'
    nome: str
    url: str | None = None
    data_adicao: str | None = None
    icone: str | None = None
    filhos: list[BookmarkNode] = field(default_factory=list)
