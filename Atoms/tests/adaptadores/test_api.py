"""Testes de integração da API FastAPI que expõe operações de bookmarks.

Verifica o comportamento dos endpoints de saúde, busca e conversão de arquivos, cobrindo cenários de sucesso e erro."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from src.adaptadores.api import app

client = TestClient(app)


@pytest.fixture
def pasta_com_bookmarks(caminho_de_destino: Path) -> Path:
    """Cria uma pasta temporária contendo um arquivo de bookmarks mínimo em HTML.

    Gera um arquivo 'bookmarks.html' com um único link, usado como entrada pelos testes de busca e conversão.
    """
    (caminho_de_destino / "bookmarks.html").write_text(
        data="<DL><DT><A HREF='https://x.com'>X</A></DL>"
    )
    return caminho_de_destino


def test_saude() -> None:
    """Valida que o endpoint de saúde responde com status 200 e JSON indicando serviço OK.

    Garante que a API está acessível e retornando o payload esperado na rota '/saude'.
    """
    resposta: Any = client.get(url="/saude")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_buscar_encontra_arquivos(pasta_com_bookmarks: Path) -> None:
    """Verifica que o endpoint de busca encontra arquivos de bookmarks em um diretório válido.

    Usa a pasta temporária com um arquivo de bookmarks e valida que a resposta indica sucesso e contabiliza corretamente o total de links.
    """
    resposta: Any = client.get(url="/buscar", params={"origem": str(pasta_com_bookmarks)})
    assert resposta.status_code == 200
    corpo: list[dict[str, Any]] = resposta.json()
    assert len(corpo) == 1
    assert corpo[0]["status"] == "sucesso"
    assert corpo[0]["total_links"] == 1


def test_buscar_pasta_inexistente() -> None:
    """Garante que a busca retorna erro ao receber um diretório de origem inexistente.

    Verifica que o endpoint '/buscar' responde com status 400 quando o caminho informado não existe no sistema de arquivos.
    """
    resposta: Any = client.get(url="/buscar", params={"origem": "/pasta/nao/existe"})
    assert resposta.status_code == 400


def test_converter_gera_arquivos(pasta_com_bookmarks: Path) -> None:
    """Confere que o endpoint de conversão gera arquivos de saída quando recebe um caminho válido.

    Usa um arquivo de bookmarks existente e verifica que a resposta inclui ao menos um arquivo gerado e que ele foi criado em disco.
    """
    entrada: Path = pasta_com_bookmarks / "bookmarks.html"
    resposta: Any = client.post(
        url="/converter",
        json={
            "caminhos": [str(entrada)],
            "formatos": [".csv"],
        },
    )
    assert resposta.status_code == 200
    corpo: dict[str, Any] = resposta.json()
    assert len(corpo["arquivos_gerados"]) == 1
    assert Path(corpo["arquivos_gerados"][0]).exists()


def test_converter_arquivo_ausente() -> None:
    """Valida que a conversão retorna erro quando recebe caminho de arquivo inexistente.

    Garante que o endpoint '/converter' responde com status 400 ao tentar processar um caminho inválido.
    """
    resposta: Any = client.post(
        url="/converter",
        json={
            "caminhos": ["/arquivo/nao/existe.html"],
        },
    )
    assert resposta.status_code == 400
