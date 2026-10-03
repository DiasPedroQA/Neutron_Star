# Atoms/tests/controllers/test_api_processar.py

"""Integração da rota POST /api/processar: contrato do payload e repasse ao serviço."""

import json
from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock

from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from src.models.entidades import StatusConversao


def _postar(client: FlaskClient, **extras: Any) -> TestResponse:
    """Envia payload válido e consome o stream da resposta SSE."""
    payload: dict[str, Any] = {
        "arquivos_selecionados": ["/home/u/a.html"],
        "extensao_destino": "json",
        **extras,
    }
    resposta: TestResponse = client.post("/api/processar", json=payload)
    resposta.get_data()
    return resposta


def test_api_repassa_pasta_saida_ao_servico(client: FlaskClient, mock_servico: MagicMock) -> None:
    """Regressão BUG-001: a pasta escolhida na UI era descartada pelo controller."""
    mock_servico.converter_com_progresso.return_value = iter(())

    _postar(client, pasta_saida="/home/u/saida")

    assert mock_servico.converter_com_progresso.call_args.kwargs["pasta_saida"] == "/home/u/saida"


def test_api_sem_pasta_saida_repassa_none(client: FlaskClient, mock_servico: MagicMock) -> None:
    """Regressão BUG-001: a pasta escolhida na UI era descartada pelo controller."""
    mock_servico.converter_com_progresso.return_value = iter(())

    _postar(client)

    assert mock_servico.converter_com_progresso.call_args.kwargs["pasta_saida"] is None


def test_api_rejeita_pasta_saida_invalida_com_400(client: FlaskClient) -> None:
    """Rejeita payload com pasta_saida não string, com mensagem de contrato do validador."""
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


def test_api_rejeita_payload_ausente_com_400(client: FlaskClient) -> None:
    """Rejeita requisições sem JSON com a mensagem de contrato do validador."""
    resposta = client.post("/api/processar")

    assert resposta.status_code == 400
    assert resposta.get_json() == {"erro": "O payload da requisição deve ser um objeto JSON."}


def test_api_rejeita_formato_nao_suportado_com_400(client: FlaskClient) -> None:
    """Rejeita extensões não suportadas antes de abrir o fluxo SSE."""
    resposta = client.post(
        "/api/processar",
        json={"arquivos_selecionados": ["a.html"], "extensao_destino": "xml"},
    )

    assert resposta.status_code == 400
    assert "Formato de destino inválido" in resposta.get_json()["erro"]


def test_api_transmite_eventos_sse_serializados(
    client: FlaskClient, mock_servico: MagicMock
) -> None:
    """Retorna os eventos do serviço em JSON e mantém os cabeçalhos SSE."""
    evento: StatusConversao = {
        "progresso": 100,
        "arquivo_atual": "",
        "arquivos_convertidos": [],
        "erros": [],
        "concluido": True,
        "sucesso": True,
    }
    mock_servico.converter_com_progresso.return_value = iter([evento])

    resposta: TestResponse = _postar(client)
    conteudo: str = resposta.get_data(as_text=True)

    assert resposta.status_code == 200
    assert resposta.mimetype == "text/event-stream"
    assert resposta.headers["Cache-Control"] == "no-cache"
    assert resposta.headers["X-Accel-Buffering"] == "no"
    assert conteudo == f"data: {json.dumps(evento, ensure_ascii=False)}\n\n"


def test_api_transmite_evento_de_erro_quando_servico_falha(
    client: FlaskClient, mock_servico: MagicMock
) -> None:
    """Converte falha durante o consumo do gerador em evento SSE final de erro."""

    def gerar_falha() -> Iterator[StatusConversao]:
        """Simula erro assíncrono disparado ao consumir eventos do serviço."""
        yield from ()
        raise RuntimeError("falha simulada")

    mock_servico.converter_com_progresso.return_value = gerar_falha()

    resposta: TestResponse = _postar(client)
    linha_evento: str = resposta.get_data(as_text=True).removeprefix("data: ").strip()
    evento_erro: dict[str, Any] = json.loads(linha_evento)

    assert resposta.status_code == 200
    assert evento_erro["concluido"] is True
    assert evento_erro["sucesso"] is False
    assert evento_erro["erros"] == [{"arquivo": "geral", "erro": "falha simulada"}]
