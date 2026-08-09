"""Testes para o repositório em memória."""
from dominio.entidades import Bookmark
from infra.repositorio import RepositorioEmMemoria

def test_repositorio_retorna_lista() -> None:
    repo = RepositorioEmMemoria()
    lista: list[Bookmark] = repo.listar_todos()
    assert len(lista) > 0
