"""
Fixtures e funções auxiliares para os testes do módulo tools.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


# ---------------------------------------------------------------------------
# Funções auxiliares de criação
# ---------------------------------------------------------------------------


def criar_arquivo_fake(caminho_arquivo: Path, conteudo: bytes = b"") -> Path:
    """Cria um arquivo fake com conteúdo binário e retorna o caminho."""
    caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)
    caminho_arquivo.write_bytes(data=conteudo)
    return caminho_arquivo


def criar_pasta_fake(caminho_pasta: Path) -> Path:
    """Cria uma pasta fake e retorna o caminho."""
    caminho_pasta.mkdir(parents=True, exist_ok=True)
    return caminho_pasta


def _lancar_oserror(*_args: object, **_kwargs: object) -> None:
    """Substituta de os.access que levanta OSError para simular falha."""
    raise OSError("acesso negado simulado")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def estrutura_base(fs: FakeFilesystem) -> Path:
    """Cria uma estrutura de diretórios comum para testes.

    Estrutura:
        /raiz/
        ├── arquivo.txt          (conteúdo: "hello world")
        ├── .oculto.txt          (arquivo oculto)
        ├── subdir/              (diretório vazio)
        │   └── .oculto_sub/     (subdiretório oculto)
        ├── sem_permissao/       (diretório sem permissão de listagem)
        └── link_symbolic -> arquivo.txt  (symlink)
    """
    fs.create_dir(directory_path="/raiz")
    fs.create_file(file_path="/raiz/arquivo.txt", contents="hello world")
    fs.create_file(file_path="/raiz/.oculto.txt", contents="secreto")
    fs.create_dir(directory_path="/raiz/subdir")
    fs.create_dir(directory_path="/raiz/subdir/.oculto_sub")
    fs.create_dir(directory_path="/raiz/sem_permissao")
    fs.chmod(path="/raiz/sem_permissao", mode=0o000)
    fs.create_symlink(file_path="/raiz/link_symbolic", link_target="/raiz/arquivo.txt")
    return Path("/raiz")


@pytest.fixture
def mock_windows(mocker: MockerFixture) -> MagicMock:
    """Simula ambiente Windows e mocka GetFileAttributesW.

    Retorna o mock da função para configuração de retorno/side_effect.
    """
    mocker.patch("sys.platform", "win32")
    mock_kernel32 = MagicMock()
    mock_get_attrs = MagicMock(return_value=0)
    mock_kernel32.GetFileAttributesW = mock_get_attrs
    mocker.patch("ctypes.windll", create=True, new=mock_kernel32)
    return mock_get_attrs


@pytest.fixture
def arquivo_hash(fs: FakeFilesystem) -> Path:
    """Cria um arquivo com conteúdo conhecido para testar cálculo de hash."""
    caminho = "/tmp/hash_teste.bin"
    fs.create_file(file_path=caminho, contents=b"conteudo para hash")
    return Path(caminho)


@pytest.fixture
def arquivo_simples(tmp_path: Path) -> Path:
    """Arquivo vazio em tmp_path para testes de permissões e info."""
    return criar_arquivo_fake(caminho_arquivo=tmp_path / "arquivo.txt", conteudo=b"")
