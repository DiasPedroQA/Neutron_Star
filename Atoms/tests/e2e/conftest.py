# pylint: disable=redefined-outer-name

"""Fixtures de infraestrutura local para os testes ponta a ponta."""

from collections.abc import Iterator
from pathlib import Path
from threading import Thread

import pytest
from flask import Flask
from werkzeug.serving import BaseWSGIServer, make_server

from main import criar_aplicacao


@pytest.fixture
def home_e2e(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Cria uma Home isolada e faz o domínio usá-la durante o teste."""
    home: Path = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home)
    return home


@pytest.fixture
def servidor_local(tmp_path: Path, home_e2e: Path) -> Iterator[str]:
    """Sobe a aplicação Flask em porta efêmera, isolando os arquivos de log."""
    assert home_e2e.is_dir()
    aplicacao: Flask = criar_aplicacao(diretorio_logs=tmp_path / "logs")
    servidor: BaseWSGIServer = make_server(
        host="127.0.0.1",
        port=0,
        app=aplicacao,
        threaded=True,
    )
    thread_servidor: Thread = Thread(target=servidor.serve_forever, daemon=True)
    thread_servidor.start()

    try:
        yield f"http://127.0.0.1:{servidor.server_port}"
    finally:
        servidor.shutdown()
        thread_servidor.join(timeout=5)
