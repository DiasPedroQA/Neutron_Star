import pytest
from orquestracao import pipeline


def test_registrar_e_executar_etapas(monkeypatch):
    calls = []

    @pipeline.registrar_etapa("a")
    def a():
        calls.append("a")
        return 1

    @pipeline.registrar_etapa("b")
    def b():
        calls.append("b")
        return 2

    res = pipeline.executar_etapas(["a", "b"])
    assert res["a"] == 1
    assert res["b"] == 2
    assert calls == ["a", "b"]


def test_executar_sem_etapas_executa_todas(monkeypatch):
    # assume ETAPAS_DISPONIVEIS pode estar vazio ou populado; apenas valida que retorna dict
    res = pipeline.executar_etapas()
    assert isinstance(res, dict)
