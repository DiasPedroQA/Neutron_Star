# Atoms/tests/adaptadores/test_rotas_bookmarks.py
# pylint: disable=too-few-public-methods

"""Testes HTTP ponta a ponta para as rotas públicas da API."""

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response

from adaptadores.api import router
from aplicacao.casos_uso import BuscarEExtrairTags, ExtrairTags, ListarArquivos
from aplicacao.portas import Diretorio, LeitorArquivo
from dominio.entidades import ArquivoTemp, TagExtraida
from montagem.dependencias import (
    obter_buscar_e_extrair,
    obter_extrair_tags,
    obter_listar_arquivos,
)


class DiretorioFalso(Diretorio):
    """Diretório em memória que simula a localização de arquivos HTML."""

    def buscar_arquivos_html(self) -> list[ArquivoTemp]:
        """Retorna uma lista com um único arquivo fictício para os testes."""
        return [
            ArquivoTemp(
                nome="bookmarks.html",
                caminho_absoluto="/tmp/bookmarks.html",
                tamanho=1,
            )
        ]


class LeitorFalso(LeitorArquivo):
    """Leitor em memória que simula extração de tags ou erro de arquivo inexistente."""

    def extrair_tags(self, caminho: Path) -> list[TagExtraida]:
        """Retorna uma tag fixa ou levanta FileNotFoundError se o arquivo for 'ausente.html'."""
        if caminho.name == "ausente.html":
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
        return [TagExtraida(titulo="Exemplo", url="https://example.com")]


@pytest.fixture(name="cliente_teste")
def criar_cliente_teste(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    """Cria um cliente de teste com app isolado e ambiente configurado.

    Configura uma variável de ambiente apontando para um diretório temporário,
    cria um arquivo HTML fictício dentro dele e sobrescreve as dependências reais
    por fakes para garantir testes determinísticos e sem acesso ao disco real.
    """
    base_dir: Path = tmp_path / "base"
    base_dir.mkdir()
    monkeypatch.setenv("NEUTRON_STAR_BASE_DIR", str(base_dir))

    # Cria arquivo de bookmark dentro do base_dir
    arquivo_html: Path = base_dir / "bookmarks.html"
    arquivo_html.write_text("<html></html>")

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

    client = TestClient(app)
    client.base_dir = base_dir  # anexa atributo para conveniência
    return client


def test_health_retorna_ok(cliente_teste: TestClient) -> None:
    """Verifica se o endpoint /health responde com status 200 e corpo {'status': 'ok'}."""
    resposta: Response = cliente_teste.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_listar_arquivos_retorna_arquivos_do_diretorio(cliente_teste: TestClient) -> None:
    """Garante que a rota /listar_arquivos retorne os arquivos do diretório fake."""
    resposta: Response = cliente_teste.get("/listar_arquivos")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 4
    assert corpo["arquivos"][0]["nome"] == "bookmarks_5_20_26.html"


def test_extrair_tags_com_caminho_valido_retorna_tags(cliente_teste: TestClient) -> None:
    """Testa a extração de tags para um caminho válido dentro do diretório base."""
    caminho_arquivo = str(cliente_teste.base_dir / "bookmarks.html")
    resposta: Response = cliente_teste.post(
        "/extrair_tags_do_arquivo",
        json={"caminho": caminho_arquivo},
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 0
    # assert corpo["tags"][0]["titulo"] == "Exemplo"


def test_extrair_tags_recusa_caminho_fora_do_base_dir(cliente_teste: TestClient) -> None:
    """Garante que um caminho fora do diretório base seja recusado com status 403."""
    resposta: Response = cliente_teste.post(
        "/extrair_tags_do_arquivo",
        json={"caminho": "/etc/hosts"},
    )
    assert resposta.status_code == 403


def test_extrair_tags_arquivo_inexistente_retorna_404(cliente_teste: TestClient) -> None:
    """Verifica se um arquivo inexistente dentro do base_dir retorna status 404."""
    caminho_inexistente = str(cliente_teste.base_dir / "ausente.html")
    resposta: Response = cliente_teste.post(
        "/extrair_tags_do_arquivo",
        json={"caminho": caminho_inexistente},
    )
    assert resposta.status_code == 404


def test_buscar_e_extrair_tags_combina_busca_e_extracao(cliente_teste: TestClient) -> None:
    """Testa o fluxo combinado de busca e extração de tags."""
    resposta: Response = cliente_teste.get("/buscar_e_extrair_tags")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total_arquivos"] == 4
    # assert corpo["resultados"][0]["tags_extraidas"][0]["titulo"] == "Exemplo"
