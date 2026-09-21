# Atoms/tests/adaptadores/test_api.py
# pylint: disable=missing-function-docstring

"""Testes de integração do Blueprint Flask (``src/adaptadores/api.py``)."""

import http
import json
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from src.dominio.excecoes import DiretorioInexistenteError, PathInseguroError

CAMINHO_FAVORITOS = "/home/usuario/favoritos.html"
PROFUNDIDADE_PADRAO = 5


def _corpo_json(resposta: TestResponse) -> dict[str, Any]:
    """Converte o corpo da resposta em dicionário."""
    corpo: Any = resposta.get_json()
    assert isinstance(corpo, dict)
    return corpo


def _eventos_sse(resposta: TestResponse) -> list[dict[str, Any]]:
    """Decodifica o corpo ``text/event-stream`` em uma lista de eventos JSON."""
    blocos: list[str] = resposta.get_data(as_text=True).split("\n\n")
    return [json.loads(bloco.removeprefix("data: ")) for bloco in blocos if bloco.strip()]


def test_sistema_sucesso_retorna_200_e_repassa_dados_do_caso_de_uso(
    client: FlaskClient, caso_uso_info: MagicMock
) -> None:
    dados_esperados: dict[str, Any] = {
        "so": "Linux (6.1)",
        "usuario": "usuario",
        "pasta_home": "/home/usuario",
        "atalhos_sugeridos": [],
    }
    caso_uso_info.executar.return_value = dados_esperados

    resposta: TestResponse = client.get("/api/sistema")

    assert resposta.status_code == http.HTTPStatus.OK
    assert _corpo_json(resposta) == dados_esperados


def test_sistema_erro_inesperado_retorna_500_com_chave_erro(
    client: FlaskClient, caso_uso_info: MagicMock
) -> None:
    caso_uso_info.executar.side_effect = RuntimeError("falha simulada")

    resposta: TestResponse = client.get("/api/sistema")

    assert resposta.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
    assert "erro" in _corpo_json(resposta)


def test_escanear_sem_parametros_usa_padroes_documentados(
    client: FlaskClient, caso_uso_escanear: MagicMock
) -> None:
    caso_uso_escanear.executar.return_value = {"total_arquivos": 0}

    resposta: TestResponse = client.get("/api/escanear")

    assert resposta.status_code == http.HTTPStatus.OK
    caso_uso_escanear.executar.assert_called_once_with(
        caminho_str="~/", extensao=".html", profundidade=PROFUNDIDADE_PADRAO
    )


def test_escanear_repassa_parametros_informados_e_retorna_200(
    client: FlaskClient, caso_uso_escanear: MagicMock
) -> None:
    caso_uso_escanear.executar.return_value = {"total_arquivos": 1}

    resposta: TestResponse = client.get(
        "/api/escanear?caminho=~/Documentos&extensao=.htm&profundidade=2"
    )

    assert resposta.status_code == http.HTTPStatus.OK
    assert _corpo_json(resposta) == {"total_arquivos": 1}
    caso_uso_escanear.executar.assert_called_once_with(
        caminho_str="~/Documentos", extensao=".htm", profundidade=2
    )


@pytest.mark.parametrize("profundidade_invalida", ["abc", "", "1.5"])
def test_escanear_profundidade_invalida_usa_fallback_5(
    client: FlaskClient, caso_uso_escanear: MagicMock, profundidade_invalida: str
) -> None:
    caso_uso_escanear.executar.return_value = {"total_arquivos": 0}

    resposta: TestResponse = client.get(f"/api/escanear?profundidade={profundidade_invalida}")

    assert resposta.status_code == http.HTTPStatus.OK
    assert caso_uso_escanear.executar.call_args.kwargs["profundidade"] == PROFUNDIDADE_PADRAO


@pytest.mark.parametrize(
    ("excecao", "status_esperado", "trecho_da_mensagem"),
    [
        (PathInseguroError(caminho="../../etc"), http.HTTPStatus.FORBIDDEN, "Acesso Proibido"),
        (
            DiretorioInexistenteError(caminho="~/Inexistente"),
            http.HTTPStatus.NOT_FOUND,
            "não existe no disco local",
        ),
        (
            RuntimeError("falha simulada"),
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
            "Falha no escaneamento",
        ),
    ],
    ids=["path_traversal_403", "diretorio_inexistente_404", "erro_inesperado_500"],
)
def test_escanear_mapeia_excecoes_para_status_http(
    client: FlaskClient,
    caso_uso_escanear: MagicMock,
    excecao: Exception,
    status_esperado: int,
    trecho_da_mensagem: str,
) -> None:
    caso_uso_escanear.executar.side_effect = excecao

    resposta: TestResponse = client.get("/api/escanear?caminho=~/qualquer")

    assert resposta.status_code == status_esperado
    assert trecho_da_mensagem in _corpo_json(resposta)["erro"]


def test_processar_payload_invalido_retorna_400_sem_acionar_caso_de_uso(
    client: FlaskClient, caso_uso_converter: MagicMock
) -> None:
    payload: dict[str, Any] = {"arquivos_selecionados": [], "extensao_destino": "xml"}

    resposta: TestResponse = client.post("/api/processar", json=payload)

    assert resposta.status_code == http.HTTPStatus.BAD_REQUEST
    assert "erro" in _corpo_json(resposta)
    caso_uso_converter.executar_com_progresso.assert_not_called()


def test_processar_transmite_eventos_sse_e_repassa_argumentos(
    client: FlaskClient, caso_uso_converter: MagicMock
) -> None:
    def _progresso_simulado(**_kwargs: Any) -> Generator[dict[str, Any], None, None]:
        yield {"progresso": 50, "arquivo_atual": "fav.html", "concluido": False}
        yield {"progresso": 100, "arquivo_atual": "fav.html", "concluido": True}

    caso_uso_converter.executar_com_progresso.side_effect = _progresso_simulado
    payload: dict[str, Any] = {
        "arquivos_selecionados": [CAMINHO_FAVORITOS],
        "extensao_destino": "json",
        "pasta_saida": "~/Saida",
    }

    resposta: TestResponse = client.post("/api/processar", json=payload)

    assert resposta.status_code == http.HTTPStatus.OK
    assert resposta.mimetype == "text/event-stream"
    eventos: list[dict[str, Any]] = _eventos_sse(resposta)
    assert [evento["progresso"] for evento in eventos] == [50, 100]
    assert eventos[-1]["concluido"] is True
    caso_uso_converter.executar_com_progresso.assert_called_once_with(
        arquivos_selecionados=[CAMINHO_FAVORITOS],
        extensao_destino="json",
        pasta_saida="~/Saida",
    )


def test_processar_sem_pasta_saida_repassa_none(
    client: FlaskClient, caso_uso_converter: MagicMock
) -> None:
    caso_uso_converter.executar_com_progresso.return_value = iter(())
    payload: dict[str, Any] = {
        "arquivos_selecionados": [CAMINHO_FAVORITOS],
        "extensao_destino": "csv",
    }

    client.post("/api/processar", json=payload)

    assert caso_uso_converter.executar_com_progresso.call_args.kwargs["pasta_saida"] is None


def test_processar_erro_no_stream_vira_evento_sse_de_erro(
    client: FlaskClient, caso_uso_converter: MagicMock
) -> None:
    caso_uso_converter.executar_com_progresso.side_effect = RuntimeError("falha crítica")
    payload: dict[str, Any] = {
        "arquivos_selecionados": [CAMINHO_FAVORITOS],
        "extensao_destino": "json",
    }

    resposta: TestResponse = client.post("/api/processar", json=payload)

    assert resposta.status_code == http.HTTPStatus.OK
    (evento_erro,) = _eventos_sse(resposta)
    assert "Erro crítico no pipeline" in evento_erro["erro"]
