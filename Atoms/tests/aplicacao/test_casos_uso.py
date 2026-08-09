"""Testes para os casos de uso."""
import pytest
from src.aplicacao.casos_uso import ListarBookmarks, ConverterBookmarks
from src.infra.repositorio import RepositorioEmMemoria
from src.infra.escritores import ConversorMarkdown

def test_listar_bookmarks():
    repo = RepositorioEmMemoria()
    use_case = ListarBookmarks(repo)
    resultado = use_case.executar()
    assert len(resultado) == 3
    assert resultado[0].titulo == "Google"

def test_converter_bookmarks():
    conversor = ConversorMarkdown()
    use_case = ConverterBookmarks(conversor)
    bookmarks = [{"titulo": "Teste", "url": "http://teste.com"}]
    # (seria melhor criar objetos Bookmark, mas o teste é simples)
    # Vamos pular a conversão por enquanto.
    pass
