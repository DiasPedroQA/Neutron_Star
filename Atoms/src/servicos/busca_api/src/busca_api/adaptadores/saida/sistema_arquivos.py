"""Adaptador de saída: implementa `RepositorioFavoritos` lendo o disco real.

Assunção: portada do `leitura.py` original, mas simplificada — a extração de
`data_adicao` e `pasta` (que dependiam de atributos específicos das tags
`<H3>`/`<DT>` do Netscape Bookmark) fica marcada como próximo passo, já que
o resumo não detalhou essa lógica auxiliar.
"""

from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup, Tag

from dominio.entidades import Bookmark

_NOMES_SUGESTIVOS = ("bookmark", "favorito", "favorites")


class RepositorioFavoritosHtml:
    """Implementação de `RepositorioFavoritos` que lê arquivos Netscape Bookmark (.html) do disco."""

    def descobrir_arquivos(self, pasta: Path) -> list[Path]:
        """Varre `pasta` recursivamente por arquivos `.html` com nome sugestivo de favoritos."""
        return sorted(
            arquivo
            for arquivo in pasta.rglob("*.html")
            if any(nome in arquivo.name.lower() for nome in _NOMES_SUGESTIVOS)
        )

    def ler_bookmarks(self, arquivo: Path) -> list[Bookmark]:
        """Faz o parsing de um arquivo Netscape Bookmark e retorna os `Bookmark` encontrados."""
        conteudo = arquivo.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(conteudo, "html.parser")
        bookmarks: list[Bookmark] = []
        for tag in soup.find_all("a"):
            bookmark = self._extrair_bookmark_de_tag(tag)
            if bookmark is not None:
                bookmarks.append(bookmark)
        return bookmarks

    @staticmethod
    def _extrair_bookmark_de_tag(tag: Tag) -> Bookmark | None:
        """Extrai um `Bookmark` de uma tag `<a>`, ou `None` se a tag não tiver `href`."""
        url = tag.get("href")
        if not url:
            return None
        return Bookmark(
            titulo=tag.get_text(strip=True) or str(url),
            url=str(url),
            icone=tag.get("icon"),
        )
