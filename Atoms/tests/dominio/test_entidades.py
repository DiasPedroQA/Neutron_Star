# tests/dominio/test_entidades.py

from src.dominio.entidades import Bookmark


def test_construcao_bookmark() -> None:
    b = Bookmark(titulo="A", url="http://a")
    assert b.titulo == "A"
    assert b.url == "http://a"
