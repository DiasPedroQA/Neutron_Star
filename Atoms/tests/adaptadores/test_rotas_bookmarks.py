# pylint: disable=too-few-public-methods

"""Testes HTTP ponta a ponta para as rotas públicas da API."""


import os
from pathlib import Path

import pytest
from adaptadores.api import router
from aplicacao.portas import Diretorio, LeitorArquivo
from dominio.entidades import ArquivoTemp, TagExtraida
from fastapi import FastAPI

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
    return app
