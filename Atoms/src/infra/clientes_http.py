# Atoms/infra/clientes_http.py
# pylint: disable=too-few-public-methods

"""Clientes HTTP para consumir APIs externas."""

from aplicacao.portas import OrquestradorClient
from dominio.entidades import TagExtraida


class ClienteBuscaAPI(OrquestradorClient):
    """Cliente que chama a própria busca_api (exemplo)."""

    def buscar(self) -> list[TagExtraida]:
        """Faz uma requisição GET para a busca_api e retorna os arquivos html.

        Implementação mock para testes e desenvolvimento.
        """
        # Simula uma chamada externa (mock)
        return [
            TagExtraida(titulo="Exemplo Externo", url="https://exemplo.com"),
        ]
