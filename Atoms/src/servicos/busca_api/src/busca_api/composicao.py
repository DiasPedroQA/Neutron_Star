"""Composition root do busca_api: monta o adaptador concreto e injeta no caso de uso."""

from __future__ import annotations

from busca_api.adaptadores.saida.sistema_arquivos import RepositorioFavoritosHtml
from busca_api.aplicacao.casos_uso import BuscarBookmarks


def obter_buscar_bookmarks() -> BuscarBookmarks:
    """Fábrica usada pelo FastAPI (`Depends`) para obter o caso de uso já composto."""
    repositorio = RepositorioFavoritosHtml()
    return BuscarBookmarks(repositorio)
