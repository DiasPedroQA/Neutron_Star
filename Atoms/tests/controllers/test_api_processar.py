# Atoms/tests/controllers/test_api_processar.py

"""Integração da rota POST /api/processar: contrato do payload e repasse ao serviço."""

from typing import Any
from unittest.mock import MagicMock

from flask.testing import FlaskClient


def _postar(client: FlaskClient, **extras: Any) -> None:
    payload: dict[str, Any] = {
        "arquivos_selecionados": ["/home/u/a.html"],
        "extensao_destino": "json",
        **extras,
    }
    client.post("/api/processar", json=payload).get_data()  # consome o stream SSE


def test_api_repassa_pasta_saida_ao_servico(client: FlaskClient, mock_servico: MagicMock) -> None:
    """Regressão BUG-001: a pasta escolhida na UI era descartada pelo controller."""
    mock_servico.converter_com_progresso.return_value = iter(())

    _postar(client, pasta_saida="/home/u/saida")

    assert mock_servico.converter_com_progresso.call_args.kwargs["pasta_saida"] == "/home/u/saida"


def test_api_sem_pasta_saida_repassa_none(client: FlaskClient, mock_servico: MagicMock) -> None:
    mock_servico.converter_com_progresso.return_value = iter(())

    _postar(client)

    assert mock_servico.converter_com_progresso.call_args.kwargs["pasta_saida"] is None


def test_api_rejeita_pasta_saida_invalida_com_400(client: FlaskClient) -> None:
    resposta = client.post(
        "/api/processar",
        json={
            "arquivos_selecionados": ["/home/u/a.html"],
            "extensao_destino": "json",
            "pasta_saida": 42,
        },
    )

    assert resposta.status_code == 400
    assert "pasta_saida" in resposta.get_json()["erro"]
