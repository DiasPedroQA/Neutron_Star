from orquestracao import contextos


def test_normaliza_extensao():
    assert contextos.normaliza_ext("pdf") == ".pdf"
    assert contextos.normaliza_ext(".json") == ".json"


def test_default_nao_tem_pdf():
    assert ".pdf" not in contextos.DEFAULT_FORMATOS
    assert ".json" in contextos.DEFAULT_FORMATOS
