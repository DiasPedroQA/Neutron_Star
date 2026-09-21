# Atoms/tests/conftest.py
# pylint: disable=redefined-outer-name

"""Fixtures compartilhadas e setup do servidor de testes do Neutron Star."""

import logging
import socket
import threading
import time
from collections.abc import Generator, Iterator
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.serving import BaseWSGIServer, make_server

import main
from src.infra.conteiner import conteiner


def _encontrar_porta_livre() -> int:
    """Obtém uma porta TCP livre do sistema operacional."""
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def live_server_url() -> Generator[str, None, None]:
    """Sobe o servidor Flask real em uma thread dedicada para os testes E2E."""
    app_instancia: Flask = main.criar_aplicacao()
    app_instancia.config["TESTING"] = True

    porta: int = _encontrar_porta_livre()
    servidor: BaseWSGIServer = make_server(host="127.0.0.1", port=porta, app=app_instancia)
    thread = threading.Thread(target=servidor.serve_forever, daemon=True)
    thread.start()

    time.sleep(0.5)  # Breve warmup do socket

    yield f"http://127.0.0.1:{porta}"
    servidor.shutdown()
    thread.join()


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[Flask]:
    """App Flask de teste com o log de auditoria redirecionado para ``tmp_path``."""
    arquivo_log: Path = tmp_path / "erros_servidor.txt"

    def _handler_temporario(**_kwargs: object) -> logging.Handler:
        return logging.FileHandler(filename=arquivo_log, encoding="utf-8")

    monkeypatch.setattr(target=main, name="RotatingFileHandler", value=_handler_temporario)
    aplicacao: Flask = main.criar_aplicacao()
    aplicacao.config["TESTING"] = True

    yield aplicacao

    # Evita acúmulo de handlers no logger global entre testes.
    for handler in list(aplicacao.logger.handlers):
        if isinstance(handler, logging.FileHandler):
            aplicacao.logger.removeHandler(hdlr=handler)
            handler.close()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Cliente HTTP de teste do Flask."""
    return app.test_client()


@pytest.fixture
def caso_uso_info(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Substitui ``obter_info_sistema_use_case`` do contêiner por um mock."""
    falso = MagicMock(name="ObterInfoSistemaUseCase")
    monkeypatch.setattr(target=conteiner, name="obter_info_sistema_use_case", value=falso)
    return falso


@pytest.fixture
def caso_uso_escanear(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Substitui ``escanear_diretorio_use_case`` do contêiner por um mock."""
    falso = MagicMock(name="EscanearDiretorioUseCase")
    monkeypatch.setattr(target=conteiner, name="escanear_diretorio_use_case", value=falso)
    return falso


@pytest.fixture
def caso_uso_converter(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Substitui ``converter_favoritos_use_case`` do contêiner por um mock."""
    falso = MagicMock(name="ConverterFavoritosLoteUseCase")
    monkeypatch.setattr(target=conteiner, name="converter_favoritos_use_case", value=falso)
    return falso
