from collections.abc import Iterator

from dominio.entidades import Bookmark, BookmarkFolder


def _iterar_bookmarks(pasta: BookmarkFolder) -> Iterator[Bookmark]:
    """Itera recursivamente sobre todos os bookmarks de uma hierarquia."""
    for item in pasta.itens:
        if isinstance(item, Bookmark):
            yield item
        elif isinstance(item, BookmarkFolder):
            yield from _iterar_bookmarks(pasta=item)
