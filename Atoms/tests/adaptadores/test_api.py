# Atoms/tests/adaptadores/test_api.py

"""Testes de integração do Blueprint Flask (``src/adaptadores/api.py``).

Escopo: contrato HTTP das rotas (status, corpo, repasse de argumentos ao caso de
uso). As regras de negócio são testadas em ``tests/aplicacao``.
"""

import json
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from src.dominio.excecoes import DiretorioInexistenteError, PathInseguroError

CAMINHO_FAVORITOS = "/home/usuario/favoritos.html"


def _corpo_json(resposta: TestResponse) -> dict[str, Any]:
    """Converte o corpo da resposta em dicionário."""
    corpo: Any = resposta.get_json()
    assert isinstance(corpo, dict)
    return corpo


def _eventos_sse(resposta: TestResponse) -> list[dict[str, Any]]:
    """Decodifica o corpo ``text/event-stream`` em uma lista de eventos JSON."""
    blocos: list[str] = resposta.get_data(as_text=True).split("\n\n")
    return [json.loads(bloco.removeprefix("data: ")) for bloco in blocos if bloco.strip()]


# ===========================================================================
# GET /api/sistema
# ===========================================================================


def test_sistema_sucesso_retorna_200_e_repassa_dados_do_caso_de_uso(
    client: FlaskClient, caso_uso_info: MagicMock
) -> None:
    """A rota deve devolver, sem alterações, o dicionário do caso de uso."""
    dados_esperados: dict[str, Any] = {
        "so": "Linux (6.1)",
        "usuario": "usuario",
        "pasta_home": "/home/usuario",
        "atalhos_sugeridos": [],
    }
    caso_uso_info.executar.return_value = dados_esperados

    resposta: TestResponse = client.get("/api/sistema")

    assert resposta.status_code == 200
    assert _corpo_json(resposta) == dados_esperados


def test_sistema_erro_inesperado_retorna_500_com_chave_erro(
    client: FlaskClient, caso_uso_info: MagicMock
) -> None:
    """Exceção genérica no caso de uso deve virar 500 com a chave ``erro``."""
    caso_uso_info.executar.side_effect = RuntimeError("falha simulada")

    resposta: TestResponse = client.get("/api/sistema")

    assert resposta.status_code == 500
    assert "erro" in _corpo_json(resposta)


# ===========================================================================
# GET /api/escanear
# ===========================================================================


def test_escanear_sem_parametros_usa_padroes_documentados(
    client: FlaskClient, caso_uso_escanear: MagicMock
) -> None:
    """Sem query string: caminho ``~/``, extensão ``.html`` e profundidade 5."""
    caso_uso_escanear.executar.return_value = {"total_arquivos": 0}

    resposta: TestResponse = client.get("/api/escanear")

    assert resposta.status_code == 200
    caso_uso_escanear.executar.assert_called_once_with(
        caminho_str="~/", extensao=".html", profundidade=5
    )


def test_escanear_repassa_parametros_informados_e_retorna_200(
    client: FlaskClient, caso_uso_escanear: MagicMock
) -> None:
    """Parâmetros da query string devem chegar ao caso de uso convertidos."""
    caso_uso_escanear.executar.return_value = {"total_arquivos": 1}

    resposta: TestResponse = client.get(
        "/api/escanear?caminho=~/Documentos&extensao=.htm&profundidade=2"
    )

    assert resposta.status_code == 200
    assert _corpo_json(resposta) == {"total_arquivos": 1}
    caso_uso_escanear.executar.assert_called_once_with(
        caminho_str="~/Documentos", extensao=".htm", profundidade=2
    )


@pytest.mark.parametrize("profundidade_invalida", ["abc", "", "1.5"])
def test_escanear_profundidade_invalida_usa_fallback_5(
    client: FlaskClient, caso_uso_escanear: MagicMock, profundidade_invalida: str
) -> None:
    """Profundidade não numérica não pode derrubar a rota: cai para 5."""
    caso_uso_escanear.executar.return_value = {"total_arquivos": 0}

    resposta: TestResponse = client.get(f"/api/escanear?profundidade={profundidade_invalida}")

    assert resposta.status_code == 200
    assert caso_uso_escanear.executar.call_args.kwargs["profundidade"] == 5


@pytest.mark.parametrize(
    ("excecao", "status_esperado", "trecho_da_mensagem"),
    [
        (PathInseguroError(caminho="../../etc"), 403, "Acesso Proibido"),
        (DiretorioInexistenteError(caminho="~/Inexistente"), 404, "não existe no disco local"),
        (RuntimeError("falha simulada"), 500, "Falha no escaneamento"),
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
    """Cada exceção de domínio deve virar o status HTTP correspondente."""
    caso_uso_escanear.executar.side_effect = excecao

    resposta: TestResponse = client.get("/api/escanear?caminho=~/qualquer")

    assert resposta.status_code == status_esperado
    assert trecho_da_mensagem in _corpo_json(resposta)["erro"]


# ===========================================================================
# POST /api/processar
# ===========================================================================


def test_processar_payload_invalido_retorna_400_sem_acionar_caso_de_uso(
    client: FlaskClient, caso_uso_converter: MagicMock
) -> None:
    """Payload reprovado pelo schema deve ser rejeitado antes do caso de uso."""
    payload: dict[str, Any] = {"arquivos_selecionados": [], "extensao_destino": "xml"}

    resposta: TestResponse = client.post("/api/processar", json=payload)

    assert resposta.status_code == 400
    assert "erro" in _corpo_json(resposta)
    caso_uso_converter.executar_com_progresso.assert_not_called()


def test_processar_transmite_eventos_sse_e_repassa_argumentos(
    client: FlaskClient, caso_uso_converter: MagicMock
) -> None:
    """Deve responder ``text/event-stream`` com um evento por progresso."""

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

    assert resposta.status_code == 200
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
    """Ausência de ``pasta_saida`` significa gravar ao lado do original (``None``)."""
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
    """Falha durante o pipeline não pode derrubar a conexão: gera evento de erro."""
    caso_uso_converter.executar_com_progresso.side_effect = RuntimeError("falha crítica")
    payload: dict[str, Any] = {
        "arquivos_selecionados": [CAMINHO_FAVORITOS],
        "extensao_destino": "json",
    }

    resposta: TestResponse = client.post("/api/processar", json=payload)

    assert resposta.status_code == 200
    (evento_erro,) = _eventos_sse(resposta)
    assert "Erro crítico no pipeline" in evento_erro["erro"]


@pytest.mark.xfail(
    strict=True,
    reason="BUG confirmado: corpo não-JSON retorna HTML (415/400) em vez de JSON {'erro': ...}.",
)
@pytest.mark.parametrize(
    ("corpo", "content_type"),
    [("texto puro", "text/plain"), ("{quebrado", "application/json")],
    ids=["content_type_errado", "json_malformado"],
)
def test_processar_corpo_nao_json_retorna_erro_em_json(
    client: FlaskClient, corpo: str, content_type: str
) -> None:
    """Contrato da API: todo erro 4xx deve ser JSON com a chave ``erro``."""
    resposta: TestResponse = client.post("/api/processar", data=corpo, content_type=content_type)

    assert resposta.status_code in {400, 415}
    assert resposta.mimetype == "application/json"
    assert "erro" in _corpo_json(resposta)
