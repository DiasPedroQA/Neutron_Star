# pylint: disable=too-few-public-methods

"""Testes HTTP ponta a ponta para as rotas públicas da API."""

import os
from pathlib import Path

import pytest
from adaptadores.api import router
from aplicacao.casos_uso import BuscarEExtrairTags, ExtrairTags, ListarArquivos
from aplicacao.portas import Diretorio, LeitorArquivo
from dominio.entidades import ArquivoTemp, TagExtraida
from fastapi import FastAPI
from fastapi.testclient import TestClient
from montagem.dependencias import (
    obter_buscar_e_extrair,
    obter_extrair_tags,
    obter_listar_arquivos,
)

os.environ["NEUTRON_STAR_BASE_DIR"] = "/tmp"


Path("/tmp/bookmarks.html").touch()


class DiretorioFalso(Diretorio):
    """Diretório em memória com um arquivo de bookmark para os testes."""

    def buscar_arquivos_html(self) -> list[ArquivoTemp]:
        """Retorna o único arquivo previsto pelo cenário de teste."""
        return [
            ArquivoTemp(
                nome="bookmarks.html",
                caminho_absoluto="/tmp/bookmarks.html",
                tamanho=1,
            )
        ]


class LeitorFalso(LeitorArquivo):
    """Leitor em memória que simula extração e arquivo inexistente."""

    def extrair_tags(self, caminho: Path) -> list[TagExtraida]:
        """Retorna uma tag ou levanta FileNotFoundError para o caminho ausente."""
        if caminho.name == "ausente.html":
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
        return [TagExtraida(titulo="Exemplo", url="https://example.com")]


@pytest.fixture(name="app_teste")
def criar_app_teste() -> FastAPI:
    """Cria uma aplicação isolada com dependências controladas para os testes HTTP."""
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[obter_listar_arquivos] = lambda: ListarArquivos(
        diretorio=DiretorioFalso()
    )
    app.dependency_overrides[obter_extrair_tags] = lambda: ExtrairTags(leitor=LeitorFalso())
    app.dependency_overrides[obter_buscar_e_extrair] = lambda: BuscarEExtrairTags(
        listar_arquivos=ListarArquivos(diretorio=DiretorioFalso()),
        extrair_tags=ExtrairTags(leitor=LeitorFalso()),
    )
    return app


def test_health_retorna_ok(app_teste: FastAPI) -> None:
    """O endpoint de health deve responder 200 com status ok, sem tocar no disco."""
    cliente = TestClient(app_teste)

    resposta = cliente.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_listar_arquivos_retorna_arquivos_do_diretorio(app_teste: FastAPI) -> None:
    """A rota de listagem deve devolver os arquivos encontrados pela porta injetada."""
    cliente = TestClient(app_teste)

    resposta = cliente.get("/listar_arquivos")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 1
    assert corpo["arquivos"][0]["nome"] == "bookmarks.html"


def test_extrair_tags_com_caminho_valido_retorna_tags(app_teste: FastAPI) -> None:
    """Um caminho dentro do base_dir e existente deve retornar as tags extraídas.

    Este e o teste que pega a regressao da env var NEUTRON_STAR_BASE_DIR mal
    escrita em _get_base_dir(): com o bug, _get_base_dir() sempre caia em
    Path.home() e ignorava o /tmp configurado no topo deste arquivo, entao
    /tmp/bookmarks.html (fora do home) era incorretamente recusado com 403.
    """
    cliente = TestClient(app_teste)

    resposta = cliente.post("/extrair_tags_do_arquivo", json={"caminho": "/tmp/bookmarks.html"})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 1
    assert corpo["tags"][0]["titulo"] == "Exemplo"


def test_extrair_tags_recusa_caminho_fora_do_base_dir(app_teste: FastAPI) -> None:
    """Caminhos fora de NEUTRON_STAR_BASE_DIR devem ser recusados com 403."""
    cliente = TestClient(app_teste)

    resposta = cliente.post("/extrair_tags_do_arquivo", json={"caminho": "/etc/hosts"})

    assert resposta.status_code == 403


def test_extrair_tags_arquivo_inexistente_retorna_404(app_teste: FastAPI) -> None:
    """Um caminho dentro do base_dir mas inexistente deve retornar 404."""
    cliente = TestClient(app_teste)

    resposta = cliente.post("/extrair_tags_do_arquivo", json={"caminho": "/tmp/ausente.html"})

    assert resposta.status_code == 404


def test_buscar_e_extrair_tags_combina_busca_e_extracao(app_teste: FastAPI) -> None:
    """A rota combinada deve listar arquivos e extrair tags de cada um."""
    cliente = TestClient(app_teste)

    resposta = cliente.get("/buscar_e_extrair_tags")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total_arquivos"] == 1
    assert corpo["resultados"][0]["tags_extraidas"][0]["titulo"] == "Exemplo"
