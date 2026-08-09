# Atoms/dependencias.py

"""Configuração de dependências (injeção simples).

Fábricas de dependências para injeção nos casos de uso.
"""
from src.aplicacao.casos_uso import ListarBookmarks, ConverterBookmarks, OrquestrarBuscaEConversao
from src.infra.repositorio import RepositorioEmMemoria
from src.infra.escritores import ConversorMarkdown
from src.infra.clientes_http import ClienteBuscaAPI


def obter_listar_bookmarks() -> ListarBookmarks:
    """Fábrica para ListarBookmarks com repositório em memória."""
    return ListarBookmarks(repo=RepositorioEmMemoria())


def obter_converter_bookmarks() -> ConverterBookmarks:
    """Fábrica para ConverterBookmarks com conversor Markdown."""
    return ConverterBookmarks(conversor=ConversorMarkdown())


def obter_orquestrar_busca_conversao() -> OrquestrarBuscaEConversao:
    """Fábrica para OrquestrarBuscaEConversao com cliente mock e conversor."""
    return OrquestrarBuscaEConversao(
        cliente=ClienteBuscaAPI(),
        conversor=ConversorMarkdown()
    )
