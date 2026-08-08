# """Portas (interfaces) da camada de aplicação do serviço de conversão."""

# from __future__ import annotations

# from typing import Protocol

# from dominio.entidades import Bookmark


# class ExportadorPorta(Protocol):
#     """Porta de saída: sabe converter uma lista de bookmarks para bytes em um formato dado."""

#     def exportar(self, bookmarks: list[Bookmark], formato: str) -> bytes:
#         """Serializa `bookmarks` no `formato` indicado e retorna o conteúdo em bytes."""
#         ...
