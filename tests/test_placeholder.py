"""Teste da estrutura do projeto."""


def test_estrutura_importa() -> None:
    """Teste mínimo para validar que o pacote src é importável."""
    import src

    assert src is not None
