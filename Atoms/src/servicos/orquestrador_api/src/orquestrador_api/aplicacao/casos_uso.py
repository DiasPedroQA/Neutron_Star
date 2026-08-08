# """Caso de uso do orquestrador — não depende de httpx diretamente, só das portas.

# Isso é o que torna o caso de uso testável sem rede: nos testes (quando
# formos fazê-los), injetamos fakes de `ClienteBuscaPorta`/`ClienteConversaoPorta`
# em vez de subir os outros dois serviços de verdade.
# """

# from __future__ import annotations

# from dominio.excecoes import PastaInvalidaError

# from orquestrador_api.aplicacao.portas import ClienteBuscaPorta, ClienteConversaoPorta


# class BuscarEConverterBookmarks:
#     """Caso de uso: orquestra busca_api + conversao_api para buscar e converter em um só passo."""

#     def __init__(
#         self, cliente_busca: ClienteBuscaPorta, cliente_conversao: ClienteConversaoPorta
#     ) -> None:
#         self._cliente_busca = cliente_busca
#         self._cliente_conversao = cliente_conversao

#     def executar(self, pasta: str, formato: str) -> bytes:
#         """Busca bookmarks em `pasta` e converte o resultado para `formato`.

#         Lança `PastaInvalidaError` se nenhum bookmark for encontrado
#         (mapeada para 404 no adaptador HTTP, igual ao comportamento original
#         de `buscar-e-converter`).
#         """
#         bookmarks = self._cliente_busca.buscar(pasta)
#         if not bookmarks:
#             raise PastaInvalidaError(f"Nenhum bookmark encontrado em: {pasta}")
#         return self._cliente_conversao.converter(bookmarks, formato)
