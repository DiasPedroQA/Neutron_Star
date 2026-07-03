"""Testes para a função _dados_comuns que extrai metadados comuns de arquivos/diretórios.

Verifica a extração de caminho, data de modificação, tamanho, permissões e oculto,
além do tratamento de erros (OSError, permissões).
"""

import os
from datetime import datetime
from pathlib import Path
from typing import NoReturn

import pytest
from pytest_mock import MockerFixture

from src.utils.system_tools import _dados_comuns


# -----------------------------------------------------------------------------
# Funções auxiliares (definidas localmente, sem importar de conftest)
# -----------------------------------------------------------------------------
def _criar_arquivo(caminho: Path, conteudo: bytes = b"hello world") -> Path:
    """Cria um arquivo com conteúdo e retorna o caminho."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(data=conteudo)
    return caminho


def _criar_pasta(caminho: Path) -> Path:
    """Cria um diretório e retorna o caminho."""
    caminho.mkdir(parents=True, exist_ok=True)
    return caminho


def _lancar_oserror(*args, **kwargs) -> NoReturn:
    """Função auxiliar que sempre levanta OSError, usada em mocks."""
    raise OSError("Erro simulado")


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------
@pytest.fixture
def arquivo_txt(tmp_path: Path) -> Path:
    """Fixture que retorna um arquivo de texto com conteúdo."""
    return _criar_arquivo(caminho=tmp_path / "arquivo.txt", conteudo=b"hello world")


@pytest.fixture
def pasta(tmp_path: Path) -> Path:
    """Fixture que retorna um diretório."""
    return _criar_pasta(caminho=tmp_path / "subdir")


# -----------------------------------------------------------------------------
# Testes
# -----------------------------------------------------------------------------
class TestDadosComuns:
    """Suite de testes para a função _dados_comuns."""

    def test_arquivo_retorna_metadados_completos(self, arquivo_txt: Path) -> None:
        """Verifica que um arquivo existente retorna todos os metadados esperados."""
        dados: dict[str, str | Path | datetime | int | bool | None] = _dados_comuns(caminho=arquivo_txt)

        assert dados["caminho"] == arquivo_txt.absolute()
        assert isinstance(dados["modificado"], datetime)
        assert dados["tamanho"] == 11
        assert dados["legivel"] is True
        assert dados["gravavel"] is True
        assert dados["executavel"] is False  # Por padrão não é executável
        assert dados["oculto"] is False

    def test_diretorio_tem_tamanho_none(self, pasta: Path) -> None:
        """Verifica que diretórios têm tamanho None."""
        dados: dict[str, str | Path | datetime | int | bool | None] = _dados_comuns(caminho=pasta)
        assert dados["tamanho"] is None

    def test_falha_no_stat_resulta_em_none(self, arquivo_txt: Path, mocker: MockerFixture) -> None:
        """Simula falha em stat; modificado e tamanho devem ser None."""
        mocker.patch.object(Path, "stat", side_effect=OSError)
        dados: dict[str, str | Path | datetime | int | bool | None] = _dados_comuns(caminho=arquivo_txt)
        assert dados["modificado"] is None
        assert dados["tamanho"] is None
        # As permissões ainda podem ser obtidas via os.access, então continuam True
        assert dados["legivel"] is True

    def test_oserror_no_access_resulta_em_permissoes_false(self, arquivo_txt: Path, monkeypatch) -> None:
        """Simula erro em os.access; permissões devem ser False."""
        monkeypatch.setattr(os, "access", _lancar_oserror)
        dados: dict[str, str | Path | datetime | int | bool | None] = _dados_comuns(caminho=arquivo_txt)
        assert dados["legivel"] is False
        assert dados["gravavel"] is False
        assert dados["executavel"] is False

    def test_nome_com_ponto_marca_oculto(self, tmp_path: Path) -> None:
        """Arquivo com nome iniciado por '.' deve ser considerado oculto."""
        oculto: Path = _criar_arquivo(caminho=tmp_path / ".oculto.txt", conteudo=b"hello world")
        dados: dict[str, str | Path | datetime | int | bool | None] = _dados_comuns(caminho=oculto)
        assert dados["oculto"] is True

    def test_arquivo_sem_ponto_nao_e_oculto(self, tmp_path: Path) -> None:
        """Arquivo sem ponto no início não é oculto."""
        normal: Path = _criar_arquivo(caminho=tmp_path / "normal.txt", conteudo=b"hello world")
        dados: dict[str, str | Path | datetime | int | bool | None] = _dados_comuns(caminho=normal)
        assert dados["oculto"] is False
