"""Testes do adaptador de API (adaptadores/api/app.py).

Verificam que a API é uma casca fina sobre o mesmo núcleo usado pela CLI:
os mesmos cenários (busca, exportação, falha) devem se comportar igual.
"""

import socket
import subprocess
import sys
import time
from collections.abc import Callable, Generator
from pathlib import Path

import httpx
import pytest
from adaptadores.api.app import app, executar
from adaptadores.api.app import main as api_main
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

_HTML_VALIDO = """
<DL><p>
    <DT><A HREF="https://a.com">Site A</A>
</DL><p>
"""

cliente = TestClient(app)


class TestHealth:
    """Endpoint de verificação de disponibilidade."""

    def test_verificar_saude(self) -> None:
        """GET /health deve responder 200 com status 'ok'."""
        resposta = cliente.get(url="/health")

        assert resposta.status_code == 200
        assert resposta.json() == {"status": "ok"}


class TestBuscar:
    """POST /bookmarks/buscar — mesmo comportamento de aplicacao.etapas.etapa_buscar."""

    def test_encontra_arquivos_que_atendem_aos_filtros(self, tmp_path: Path) -> None:
        """Arquivo que bate com extensão e chave deve aparecer na resposta."""
        (tmp_path / "bookmarks_trabalho.html").write_text(data=_HTML_VALIDO, encoding="utf-8")

        resposta = cliente.post(
            url="/bookmarks/buscar",
            json={"diretorio": str(tmp_path), "chaves": ["trabalho"]},
        )

        assert resposta.status_code == 200
        encontrados: str = resposta.json()["arquivos_encontrados"]
        assert str(tmp_path / "bookmarks_trabalho.html") in encontrados

    def test_diretorio_invalido_retorna_erro_422(self, tmp_path: Path) -> None:
        """Diretório inexistente deve virar HTTP 422, não um 500 genérico."""
        resposta = cliente.post(
            url="/bookmarks/buscar",
            json={"diretorio": str(tmp_path / "nao_existe")},
        )

        assert resposta.status_code == 422


class TestProcessarLote:
    """POST /bookmarks/lote — mesmo comportamento do modo --lote da CLI."""

    def test_processa_arquivos_e_retorna_resumo(self, tmp_path: Path) -> None:
        """Arquivos válidos devem ser exportados e contabilizados como sucesso."""
        arquivo: Path = tmp_path / "bookmarks.html"
        arquivo.write_text(data=_HTML_VALIDO, encoding="utf-8")
        saida: Path = tmp_path / "saida"

        resposta = cliente.post(
            url="/bookmarks/lote",
            json={
                "arquivos": [str(arquivo)],
                "formatos": [".json"],
                "diretorio_saida": str(saida),
            },
        )

        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo == {"total": 1, "sucesso": 1, "falhas": {}}
        assert (saida / "bookmarks.json").exists()

    def test_arquivo_invalido_aparece_em_falhas_sem_quebrar_a_requisicao(self, tmp_path: Path) -> None:
        """Um arquivo inválido deve aparecer em 'falhas', com resposta 200 (não 500)."""
        invalido: Path = tmp_path / "invalido.html"
        invalido.write_text(data="<html>sem bookmarks</html>", encoding="utf-8")

        resposta = cliente.post(
            url="/bookmarks/lote",
            json={"arquivos": [str(invalido)], "formatos": [".json"]},
        )

        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo["sucesso"] == 0
        assert str(invalido) in corpo["falhas"]


class TestExecutarProgramatico:
    """Forma alternativa de subir a API: python -m adaptadores.api.app / executar()."""

    def test_executar_delega_para_uvicorn_run(
        self, mocker: Callable[..., Generator[MockerFixture, None, None]]
    ) -> None:
        """executar() deve chamar uvicorn.run com os parâmetros recebidos, sem lógica própria."""
        uvicorn_run = mocker.patch("uvicorn.run")

        executar(host="0.0.0.0", port=9001, reload=True)

        uvicorn_run.assert_called_once_with("adaptadores.api.app:app", host="0.0.0.0", port=9001, reload=True)

    def test_main_le_argumentos_e_chama_executar(
        self, mocker: Callable[..., Generator[MockerFixture, None, None]]
    ) -> None:
        """O console script (neutron-api) deve repassar host/porta/reload pros argumentos certos."""
        executar_mock = mocker.patch("adaptadores.api.app.executar")

        api_main(argv=["--host", "0.0.0.0", "--port", "9002", "--reload"])

        executar_mock.assert_called_once_with(host="0.0.0.0", port=9002, reload=True)


@pytest.mark.integration
class TestEntryPointInstalado:
    """Integração real: sobe 'neutron-api' como processo e bate na porta de verdade.

    Complementa o TestClient acima (que simula requisições em memória): aqui é
    o servidor HTTP real, subindo na porta real — pega problemas de instalação
    do entry point que o TestClient nunca pegaria.
    """

    def test_health_via_servidor_real(self) -> None:
        """GET /health num servidor uvicorn real, iniciado via subprocess, deve responder 200."""
        porta: int = _porta_livre()
        processo: subprocess.Popen[str] = subprocess.Popen(
            args=[sys.executable, "-m", "adaptadores.api.app", "--port", str(porta)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            _aguardar_servidor(porta=porta, tentativas=30)
            resposta: httpx.Response = httpx.get(f"http://127.0.0.1:{porta}/health", timeout=2)
            assert resposta.status_code == 200
            assert resposta.json() == {"status": "ok"}
        finally:
            processo.terminate()
            processo.wait(timeout=5)


def _porta_livre() -> int:
    """Pede ao sistema operacional uma porta TCP livre, evitando conflitos entre execuções."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _aguardar_servidor(porta: int, tentativas: int) -> None:
    """Espera o servidor responder, tentando algumas vezes antes de desistir."""
    for _ in range(tentativas):
        try:
            httpx.get(url=f"http://127.0.0.1:{porta}/health", timeout=0.5)
            return
        except httpx.ConnectError:
            time.sleep(0.2)
    pytest.fail(f"Servidor não respondeu na porta {porta} a tempo.")
