"""Testes HTTP ponta a ponta para as rotas públicas da API."""

# pylint: disable=too-few-public-methods

import asyncio
from pathlib import Path

import httpx
import pytest
from adaptadores.api import router
from aplicacao.casos_uso import BuscarEExtrairTags, ExtrairTags, ListarArquivos
from aplicacao.portas import Diretorio, LeitorArquivo
from dominio.entidades import ArquivoTemp, TagExtraida
from fastapi import FastAPI
from montagem.dependencias import (
    obter_buscar_e_extrair,
    obter_extrair_tags,
    obter_listar_arquivos,
)


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
            raise FileNotFoundError("arquivo ausente")
        return [TagExtraida(titulo="Exemplo", url="https://example.com")]


@pytest.fixture(name="app_teste")
def criar_app_teste() -> FastAPI:
    """Cria uma aplicação isolada com dependências controladas para os testes HTTP."""
    app = FastAPI()
    app.include_router(router)
    diretorio = DiretorioFalso()
    leitor = LeitorFalso()

    async def fornecer_listar_arquivos() -> ListarArquivos:
        """Fornece o caso de uso de listagem com dados controlados."""
        return ListarArquivos(diretorio)

    async def fornecer_extrair_tags() -> ExtrairTags:
        """Fornece o caso de uso de extração com dados controlados."""
        return ExtrairTags(leitor)

    async def fornecer_buscar_e_extrair() -> BuscarEExtrairTags:
        """Fornece o caso de uso completo com dependências controladas."""
        return BuscarEExtrairTags(diretorio, leitor)

    app.dependency_overrides[obter_listar_arquivos] = fornecer_listar_arquivos
    app.dependency_overrides[obter_extrair_tags] = fornecer_extrair_tags
    app.dependency_overrides[obter_buscar_e_extrair] = fornecer_buscar_e_extrair
    return app


async def enviar_requisicao(
    app: FastAPI, metodo: str, url: str, corpo: dict[str, str] | None = None
) -> httpx.Response:
    """Envia uma requisição HTTP ao aplicativo ASGI sem abrir uma porta de rede."""
    transporte = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transporte, base_url="http://testserver"
    ) as cliente:
        return await cliente.request(method=metodo, url=url, json=corpo)


def test_health_retorna_estado_ok(app_teste: FastAPI) -> None:
    """A rota de saúde responde HTTP 200 com o estado esperado."""
    resposta: httpx.Response = asyncio.run(
        main=enviar_requisicao(app=app_teste, metodo="GET", url="/health")
    )

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_listar_arquivos_retorna_metadados(app_teste: FastAPI) -> None:
    """A rota de listagem devolve um resumo tipado do arquivo localizado."""
    resposta: httpx.Response = asyncio.run(
        main=enviar_requisicao(app=app_teste, metodo="GET", url="/listar_arquivos")
    )

    assert resposta.status_code == 200
    assert resposta.json()["total"] == 1
    assert resposta.json()["arquivos"][0]["nome"] == "bookmarks.html"


def test_extrair_tags_retorna_bookmarks(app_teste: FastAPI) -> None:
    """A rota de extração retorna os bookmarks encontrados no arquivo."""
    resposta: httpx.Response = asyncio.run(
        main=enviar_requisicao(
            app=app_teste,
            metodo="POST",
            url="/extrair_tags_do_arquivo",
            corpo={"caminho": "/tmp/bookmarks.html"},
        )
    )

    assert resposta.status_code == 200
    assert resposta.json()["total"] == 1
    assert resposta.json()["tags"][0]["url"] == "https://example.com"


def test_extrair_tags_retorna_404_para_arquivo_ausente(app_teste: FastAPI) -> None:
    """A rota converte a ausência do arquivo em resposta HTTP 404."""
    resposta: httpx.Response = asyncio.run(
        main=enviar_requisicao(
            app=app_teste,
            metodo="POST",
            url="/extrair_tags_do_arquivo",
            corpo={"caminho": "/tmp/ausente.html"},
        )
    )

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "arquivo ausente"


def test_extrair_tags_valida_corpo_obrigatorio(app_teste: FastAPI) -> None:
    """A rota devolve HTTP 422 quando o campo caminho não é informado."""
    resposta: httpx.Response = asyncio.run(
        main=enviar_requisicao(
            app=app_teste, metodo="POST", url="/extrair_tags_do_arquivo", corpo={}
        )
    )

    assert resposta.status_code == 422


def test_buscar_e_extrair_tags_retorna_resultados(app_teste: FastAPI) -> None:
    """A rota composta associa cada arquivo aos bookmarks extraídos."""
    resposta: httpx.Response = asyncio.run(
        main=enviar_requisicao(
            app=app_teste, metodo="GET", url="/buscar_e_extrair_tags"
        )
    )

    assert resposta.status_code == 200
    assert resposta.json()["total_arquivos"] == 1
    assert resposta.json()["resultados"][0]["tags_extraidas"][0]["titulo"] == "Exemplo"


def test_openapi_expoe_contratos_de_requisicao_e_resposta(app_teste: FastAPI) -> None:
    """O OpenAPI referencia os modelos explícitos usados pela documentação."""
    contrato = asyncio.run(
        main=enviar_requisicao(app=app_teste, metodo="GET", url="/openapi.json")
    ).json()

    schema_listagem = contrato["paths"]["/listar_arquivos"]["get"]["responses"]["200"]
    schema_extracao = contrato["paths"]["/extrair_tags_do_arquivo"]["post"]
    assert schema_listagem["content"]["application/json"]["schema"]["$ref"].endswith(
        "ListarArquivosResposta"
    )
    assert schema_extracao["requestBody"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("ExtrairTagsRequisicao")
