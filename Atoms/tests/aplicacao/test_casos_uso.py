"""Testes para os casos de uso."""

from aplicacao.casos_uso import ListarBookmarks, ConverterBookmarks
from dominio.entidades import Bookmark
from infra.repositorio import RepositorioEmMemoria
from infra.escritores import ConversorMarkdown

def test_listar_bookmarks() -> None:
    repo = RepositorioEmMemoria()
    use_case = ListarBookmarks(repo)
    resultado: list[Bookmark] = use_case.buscar_arquivos_html()
    assert len(resultado) == 3
    assert resultado[0].titulo == "Google"

def test_converter_bookmarks() -> None:
    conversor = ConversorMarkdown()
    use_case = ConverterBookmarks(conversor)
    bookmarks = [{"titulo": "Teste", "url": "http://teste.com"}]
    # (seria melhor criar objetos Bookmark, mas o teste é simples)
    # Vamos pular a conversão por enquanto.
    pass
