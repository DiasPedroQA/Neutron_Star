"""Adaptador de exportação de bookmarks para texto simples.

Implementa um exportador concreto que gera uma listagem em texto puro
com títulos e URLs de cada favorito, adequada para leitura rápida ou uso em scripts.
"""

from pathlib import Path

from aplicacao.portas.exportador import Exportador
from dominio.entidades import BookmarkFolder

from adaptadores.exportadores.iterador import _iterar_bookmarks


class ExportadorTXT(Exportador):  # pylint: disable=too-few-public-methods
    """Exportador de bookmarks para texto simples."""

    def exportar(self, raiz: BookmarkFolder, caminho_saida: Path | None = None) -> str | None:
        """Exporta bookmarks como texto simples (ver Exportador.exportar)."""
        linhas: list[str] = [f"{bm.titulo}\n{bm.url}" for bm in _iterar_bookmarks(pasta=raiz)]
        conteudo: str = "\n\n".join(linhas)
        if caminho_saida:
            caminho_saida.write_text(data=conteudo, encoding="utf-8")
        return conteudo
