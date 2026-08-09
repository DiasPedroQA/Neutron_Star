# Atoms/infra/clientes_http.py

"""Clientes HTTP para consumir APIs externas."""

from aplicacao.portas import OrquestradorClient
from dominio.entidades import Bookmark


class ClienteBuscaAPI(OrquestradorClient):
    """Cliente que chama a própria busca_api (exemplo)."""

    def buscar(self) -> list[Bookmark]:
        """Faz uma requisição GET para a busca_api e retorna os bookmarks.

        Implementação mock para testes e desenvolvimento.
        """
        # Simula uma chamada externa (mock)
        return [
            Bookmark(titulo="Exemplo Externo", url="https://exemplo.com"),
        ]
