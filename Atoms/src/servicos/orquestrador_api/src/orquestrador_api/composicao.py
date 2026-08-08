# """Composition root do orquestrador — lê os endereços dos outros serviços do ambiente."""

# from __future__ import annotations

# import os

# from orquestrador_api.adaptadores.saida.clientes_http import ClienteBuscaHttp, ClienteConversaoHttp
# from orquestrador_api.aplicacao.casos_uso import BuscarEConverterBookmarks

# _BUSCA_API_URL = os.environ.get("BUSCA_API_URL", "http://localhost:8001")
# _CONVERSAO_API_URL = os.environ.get("CONVERSAO_API_URL", "http://localhost:8002")


# def obter_buscar_e_converter_bookmarks() -> BuscarEConverterBookmarks:
#     """Fábrica usada pelo FastAPI (`Depends`) para obter o caso de uso já composto."""
#     return BuscarEConverterBookmarks(
#         cliente_busca=ClienteBuscaHttp(_BUSCA_API_URL),
#         cliente_conversao=ClienteConversaoHttp(_CONVERSAO_API_URL),
#     )
