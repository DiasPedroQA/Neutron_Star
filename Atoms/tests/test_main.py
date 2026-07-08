"""Testes de integração ponta a ponta usando o ponto de entrada em src.main.

Cobre o fluxo real do CLI: Buscador(prefixo=..., data=...).buscar_arquivos(),
com Path.home() apontada para um diretório temporário via monkeypatch.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from src.main import Arquivo, Buscador, main


@pytest.fixture
def estrutura_temporaria(tmp_path: Path) -> Path:
    """Cria uma estrutura de diretórios para os testes de integração."""
    (tmp_path / "bookmarks_1_1_25.html").touch()
    (tmp_path / "bookmarks_01_01_25.html").touch()
    (tmp_path / "bookmarks_1_2_25.html").touch()
    (tmp_path / "relatorio_1_1_25.html").touch()  # prefixo diferente
    (tmp_path / ".oculto_bookmarks_1_1_25.html").touch()  # arquivo oculto

    sub: Path = tmp_path / "subpasta"
    sub.mkdir()
    (sub / "bookmarks_1_1_25.html").touch()
    return tmp_path


def test_buscador_com_prefixo_sem_data(estrutura_temporaria: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Busca arquivos com prefixo 'bookmarks', sem data específica."""
    monkeypatch.setattr("src.controllers.buscador.Path.home", lambda: estrutura_temporaria)
    buscador = Buscador(prefixo="bookmarks")
    buscador.raiz = estrutura_temporaria
    resultados: list[Arquivo] = buscador.buscar_arquivos()

    nomes: set[str] = {a.caminho.name for a in resultados}
    # 3 na raiz + 1 na subpasta
    assert len(resultados) == 4
    assert "bookmarks_1_1_25.html" in nomes
    assert "bookmarks_1_1_25.html" in nomes
    assert "bookmarks_1_2_25.html" in nomes
    assert "relatorio_1_1_25.html" not in nomes


def test_buscador_com_prefixo_e_data_exata(estrutura_temporaria: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Busca arquivos com prefixo 'bookmarks' e data '1_1_25'."""
    monkeypatch.setattr("src.controllers.buscador.Path.home", lambda: estrutura_temporaria)
    buscador = Buscador(prefixo="bookmarks", data="1_1_25")
    buscador.raiz = estrutura_temporaria
    resultados: list[Arquivo] = buscador.buscar_arquivos()

    nomes: set[str] = {a.caminho.name for a in resultados}
    # raiz + sufixo + subpasta, todos com a mesma data
    assert len(resultados) == 3
    assert "bookmarks_1_1_25.html" in nomes
    assert "bookmarks_1_1_25.html" in nomes
    assert "bookmarks_1_2_25.html" not in nomes


def test_buscador_ignora_ocultos(estrutura_temporaria: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Arquivos em pastas ocultas ou com nome começando com '.' são sempre ignorados."""
    monkeypatch.setattr("src.controllers.buscador.Path.home", lambda: estrutura_temporaria)
    buscador = Buscador(prefixo="bookmarks")
    buscador.raiz = estrutura_temporaria
    resultados: list[Arquivo] = buscador.buscar_arquivos()

    assert all(not a.caminho.name.startswith(".") for a in resultados)
    assert all(a.caminho.name != ".oculto_bookmarks_1_1_25.html" for a in resultados)


class TestCliMain:
    """Testes do ponto de entrada main() (argparse + normalizar_data)."""

    def test_main_aceita_data_em_formato_livre(
        self, estrutura_temporaria: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Data digitada em formato diferente do canônico ainda encontra o arquivo."""
        monkeypatch.setattr("src.controllers.buscador.Path.home", lambda: estrutura_temporaria)
        codigo_saida: int = main(["--prefixo", "bookmarks", "--data", "2025_01_01"])
        saida: str = capsys.readouterr().out

        assert codigo_saida == 0
        assert "bookmarks_1_1_25.html" in saida
        assert "bookmarks_1_1_25.html" in saida
        assert "bookmarks_1_2_25.html" not in saida

    def test_main_aceita_multiplos_prefixos(
        self, estrutura_temporaria: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--prefixo repetido busca todos os aliases na mesma execução."""
        monkeypatch.setattr("src.controllers.buscador.Path.home", lambda: estrutura_temporaria)
        codigo_saida: int = main(["--prefixo", "bookmarks", "--prefixo", "relatorio"])
        saida: str = capsys.readouterr().out

        assert codigo_saida == 0
        assert "bookmarks_1_1_25.html" in saida
        assert "relatorio_1_1_25.html" in saida

    def test_main_com_data_invalida_retorna_erro_sem_quebrar(
        self, estrutura_temporaria: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Data não reconhecível deve gerar mensagem clara e código de saída != 0, sem traceback."""
        monkeypatch.setattr("src.controllers.buscador.Path.home", lambda: estrutura_temporaria)
        codigo_saida: int = main(["--prefixo", "bookmarks", "--data", "isso-nao-e-uma-data"])
        erro: str = capsys.readouterr().err

        assert codigo_saida == 1
        assert "Data inválida" in erro
