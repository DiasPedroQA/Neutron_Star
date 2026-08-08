# """Portas (interfaces) da camada de aplicação do orquestrador."""

# from __future__ import annotations

# from typing import Protocol

# from dominio.entidades import Bookmark


# class ClienteBuscaPorta(Protocol):
#     """Porta de saída: sabe pedir uma busca de bookmarks a um serviço externo."""

#     def buscar(self, pasta: str) -> list[Bookmark]:
#         """Solicita a busca de bookmarks em `pasta` e retorna os encontrados."""
#         ...


# class ClienteConversaoPorta(Protocol):
#     """Porta de saída: sabe pedir a conversão de bookmarks a um serviço externo."""

#     def converter(self, bookmarks: list[Bookmark], formato: str) -> bytes:
#         """Solicita a conversão de `bookmarks` para `formato` e retorna o conteúdo gerado."""
#         ...
