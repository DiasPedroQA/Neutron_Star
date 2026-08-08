# """Adaptadores de saída: clientes HTTP para busca_api e conversao_api.

# Implementam `ClienteBuscaPorta`/`ClienteConversaoPorta` — o caso de uso não
# sabe (nem deveria saber) que a comunicação é via HTTP/httpx.
# """

# from __future__ import annotations

# import httpx

# from dominio.entidades import Bookmark


# class ClienteBuscaHttp:
#     """Implementação de `ClienteBuscaPorta` via HTTP contra o serviço busca_api."""

#     def __init__(self, base_url: str, timeout: float = 10.0) -> None:
#         self._base_url = base_url
#         self._timeout = timeout

#     def buscar(self, pasta: str) -> list[Bookmark]:
#         """Chama `GET /buscar` no busca_api e reconstrói os `Bookmark` recebidos."""
#         resposta = httpx.get(
#             f"{self._base_url}/buscar",
#             params={"pasta": pasta},
#             timeout=self._timeout,
#         )
#         resposta.raise_for_status()
#         dados = resposta.json()
#         return [Bookmark.de_dict(item) for item in dados["bookmarks"]]


# class ClienteConversaoHttp:
#     """Implementação de `ClienteConversaoPorta` via HTTP contra o serviço conversao_api."""

#     def __init__(self, base_url: str, timeout: float = 10.0) -> None:
#         self._base_url = base_url
#         self._timeout = timeout

#     def converter(self, bookmarks: list[Bookmark], formato: str) -> bytes:
#         """Chama `POST /converter` no conversao_api e retorna o conteúdo convertido."""
#         resposta = httpx.post(
#             f"{self._base_url}/converter",
#             json={
#                 "bookmarks": [bookmark.para_dict() for bookmark in bookmarks],
#                 "formato": formato,
#             },
#             timeout=self._timeout,
#         )
#         resposta.raise_for_status()
#         return resposta.content
