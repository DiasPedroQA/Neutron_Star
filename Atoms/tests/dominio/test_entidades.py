# tests/dominio/test_entidades.py

from dominio.entidades import TagExtraida


def test_construcao_bookmark() -> None:
    b = TagExtraida(titulo="A", url="http://a")
    assert b.titulo == "A"
    assert b.url == "http://a"
