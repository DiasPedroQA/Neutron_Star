# Atoms/dependencias.py

"""Configuração de dependências (injeção simples).

Fábricas de dependências para injeção nos casos de uso.
"""
from aplicacao.casos_uso import (
    ConverterTagExtraidas,
    ListarTagExtraidas,
    OrquestrarBuscaEConversao,
)
from infra.clientes_http import ClienteBuscaAPI
from infra.escritores import ConversorMarkdown
from infra.buscador import PastaBuscadora


def obter_listar_arquivos_html() -> ListarTagExtraidas:
    """Fábrica para ListarTagExtraidas com repositório em memória."""
    return ListarTagExtraidas(repo=PastaBuscadora())


def obter_converter_arquivos_html() -> ConverterTagExtraidas:
    """Fábrica para ConverterTagExtraidas com conversor Markdown."""
    return ConverterTagExtraidas(conversor=ConversorMarkdown())


def obter_orquestrar_busca_conversao() -> OrquestrarBuscaEConversao:
    """Fábrica para OrquestrarBuscaEConversao com cliente mock e conversor."""
    return OrquestrarBuscaEConversao(
        cliente=ClienteBuscaAPI(),
        conversor=ConversorMarkdown()
    )
