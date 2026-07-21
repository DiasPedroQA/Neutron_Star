"""Travessia da hierarquia de bookmarks.

Concentra num único lugar a lógica de percorrer recursivamente pastas e
favoritos — antes reimplementada de forma idêntica em cada exportador
(CSV, JSON, TXT, PDF).
"""

from __future__ import annotations

from collections.abc import Iterator

from dominio.entidades import TagA, VirtualFolder


def iterar_bookmarks(pasta: VirtualFolder) -> Iterator[TagA]:
    """Percorre recursivamente todos os favoritos (TagA) de uma hierarquia.

    Args:
        pasta: Pasta raiz (ou qualquer subpasta) a partir da qual percorrer.

    Returns:
        Iterator[TagA]: Cada favorito encontrado, em profundidade, na ordem original.
    """
    for item in pasta.filhos_da_pasta:
        if isinstance(item, TagA):
            yield item
        elif isinstance(item, VirtualFolder):
            yield from iterar_bookmarks(pasta=item)


def iterar_bookmarks_com_caminho(pasta: VirtualFolder, caminho_atual: str = "") -> Iterator[tuple[str, TagA]]:
    """Como iterar_bookmarks, mas também informa o caminho de pastas até o favorito.

    Útil para exportadores que precisam exibir em qual pasta cada favorito
    está organizado (ex.: coluna "Pasta" numa tabela Markdown).

    Args:
        pasta: Pasta raiz (ou qualquer subpasta) a partir da qual percorrer.
        caminho_atual: Caminho acumulado das pastas visitadas até aqui.

    Returns:
        Iterator[tuple[str, TagA]]: Pares (caminho_da_pasta, favorito),
        em profundidade, na ordem original.
    """
    for item in pasta.filhos_da_pasta:
        if isinstance(item, TagA):
            yield caminho_atual, item
        elif isinstance(item, VirtualFolder):
            novo_caminho: str = f"{caminho_atual}/{item.nome}" if caminho_atual else item.nome
            yield from iterar_bookmarks_com_caminho(pasta=item, caminho_atual=novo_caminho)
