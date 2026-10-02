# Atoms/tests/conftest.py

"""Fixtures globais e configuração de ambiente de testes do Neutron Star.

Convenção de import: todo o código da aplicação é importado como ``src.*``
(o ``pythonpath = ["."]`` do pyproject.toml aponta para ``Atoms/``).
"""

import logging
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from flask import Flask
from flask.testing import FlaskClient

from main import criar_aplicacao
from src.controllers import api_controller


@pytest.fixture(autouse=True)
def isolar_logging_raiz() -> Iterator[None]:
    """Restaura handlers e nível do logger raiz após cada teste (sem vazamento entre testes)."""
    raiz: logging.Logger = logging.getLogger()
    handlers_originais: list[logging.Handler] = list(raiz.handlers)
    nivel_original: int = raiz.level
    yield
    for handler in list(raiz.handlers):
        if handler not in handlers_originais:
            handler.close()
    raiz.handlers[:] = handlers_originais
    raiz.setLevel(nivel_original)


@pytest.fixture(name="app")
def fixture_app(tmp_path: Path) -> Flask:
    """Instancia a aplicação Flask em modo de teste, com logs isolados em ``tmp_path``."""
    aplicacao: Flask = criar_aplicacao(diretorio_logs=tmp_path / "logs")
    aplicacao.config.update({"TESTING": True})
    return aplicacao


@pytest.fixture(name="client")
def fixture_client(app: Flask) -> FlaskClient:
    """Retorna um cliente de testes HTTP do Flask."""
    return app.test_client()


@pytest.fixture(name="mock_servico")
def fixture_mock_servico(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock do ConversorService injetado no api_controller."""
    mock: MagicMock = MagicMock()
    monkeypatch.setattr(api_controller, "servico", mock)
    return mock


@pytest.fixture(name="caminho_teste_temp", scope="session")
def fixture_caminho_teste_temp(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Fornece um diretório temporário isolado para escrita de arquivos de teste."""
    return tmp_path_factory.mktemp(basename="neutron_star_tests")


@pytest.fixture(name="html_netscape_exemplo")
def fixture_html_netscape_exemplo() -> str:
    """Exemplo canônico de HTML no formato Netscape Bookmark File."""
    return """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3 ADD_DATE="1710000000">Tecnologia</H3>
    <DL><p>
        <DT><A HREF="https://python.org" ADD_DATE="1710001000">Python Official</A>
        <DT><A HREF="https://flask.palletsprojects.com" ADD_DATE="1710002000">Flask Web</A>
    </DL><p>
    <DT><A HREF="https://globo.com" ADD_DATE="1710003000">Portal Globo</A>
</DL><p>"""
