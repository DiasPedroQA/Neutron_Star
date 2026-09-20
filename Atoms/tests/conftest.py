# Atoms/tests/conftest.py

"""Fixtures compartilhadas da suíte de testes do Neutron Star.

Princípios:
    * Hermeticidade: nenhum teste escreve em arquivos versionados (ex.: ``logs/``).
    * Isolamento: substituições no contêiner global usam ``monkeypatch`` e são
      revertidas automaticamente ao fim de cada teste.
"""

import logging
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from flask import Flask
from flask.testing import FlaskClient

import main
from src.infra.conteiner import conteiner


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[Flask]:
    """App Flask de teste com o log de auditoria redirecionado para ``tmp_path``."""
    arquivo_log: Path = tmp_path / "erros_servidor.txt"

    def _handler_temporario(**_kwargs: object) -> logging.Handler:
        return logging.FileHandler(filename=arquivo_log, encoding="utf-8")

    monkeypatch.setattr(main, "RotatingFileHandler", _handler_temporario)
    aplicacao: Flask = main.criar_aplicacao()
    aplicacao.config["TESTING"] = True

    yield aplicacao

    # Evita acúmulo de handlers no logger global entre testes.
    for handler in list(aplicacao.logger.handlers):
        if isinstance(handler, logging.FileHandler):
            aplicacao.logger.removeHandler(handler)
            handler.close()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Cliente HTTP de teste do Flask."""
    return app.test_client()


@pytest.fixture
def caso_uso_info(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Substitui ``obter_info_sistema_use_case`` do contêiner por um mock."""
    falso = MagicMock(name="ObterInfoSistemaUseCase")
    monkeypatch.setattr(conteiner, "obter_info_sistema_use_case", falso)
    return falso


@pytest.fixture
def caso_uso_escanear(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Substitui ``escanear_diretorio_use_case`` do contêiner por um mock."""
    falso = MagicMock(name="EscanearDiretorioUseCase")
    monkeypatch.setattr(conteiner, "escanear_diretorio_use_case", falso)
    return falso


@pytest.fixture
def caso_uso_converter(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Substitui ``converter_favoritos_use_case`` do contêiner por um mock."""
    falso = MagicMock(name="ConverterFavoritosLoteUseCase")
    monkeypatch.setattr(conteiner, "converter_favoritos_use_case", falso)
    return falso
