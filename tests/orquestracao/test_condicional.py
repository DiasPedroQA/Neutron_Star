from orquestracao import condicional, pipeline


def test_condicional_executa_apenas_quando_pred_true(monkeypatch):
    calls = []

    def pred_true():
        return True

    def pred_false():
        return False

    # registrar uma etapa simples
    pipeline.ETAPAS_DISPONIVEIS["x"] = lambda: calls.append("x") or "ok"

    res = condicional.executar_condicional({"x": pred_true, "y": pred_false}, etapas=["x", "y"])
    assert "x" in res
    assert "y" not in res
    assert calls == ["x"]
