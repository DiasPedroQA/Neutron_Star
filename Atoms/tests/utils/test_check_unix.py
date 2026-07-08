"""Testes para a função _verificar_oculto em sistemas Unix (Linux/macOS).

Verifica a detecção de arquivos/diretórios ocultos baseada no nome
(iniciado por '.') ou em componentes ocultos no caminho relativo à raiz.
"""

from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from src.utils.system_tools import _verificar_oculto


class TestVerificarOcultoUnix:
    """Testes para _verificar_oculto em sistemas Unix (Linux/macOS)."""

    def test_nome_com_ponto_inicial_e_oculto(self, fs: FakeFilesystem) -> None:
        """Nome iniciado por '.' é considerado oculto."""
        fs.create_file(file_path="/tmp/.oculto")
        assert _verificar_oculto(caminho=Path("/tmp/.oculto")) is True

    def test_nome_sem_ponto_nao_e_oculto(self, fs: FakeFilesystem) -> None:
        """Nome sem '.' inicial não é oculto."""
        fs.create_file(file_path="/tmp/visivel")
        assert _verificar_oculto(caminho=Path("/tmp/visivel")) is False

    def test_caminho_fora_da_raiz_usa_nome_base(self, estrutura_base: Path) -> None:
        """Se o caminho está fora da raiz, usa apenas o nome base."""
        assert _verificar_oculto(caminho=Path("/outro/.oculto"), raiz_busca=estrutura_base) is True

    def test_raiz_none_usa_apenas_nome(self, fs: FakeFilesystem) -> None:
        """Se raiz_busca é None, apenas o nome é verificado."""
        fs.create_file(file_path="/tmp/.oculto")
        assert _verificar_oculto(caminho=Path("/tmp/.oculto"), raiz_busca=None) is True

    @pytest.mark.parametrize(
        argnames="caminho_relativo, esperado",
        argvalues=[
            ("subdir/.oculto_sub", True),
            ("subdir", False),
        ],
        ids=["com_componente_oculto", "sem_componente_oculto"],
    )
    def test_verifica_componentes_ocultos_no_caminho_relativo(
        self, estrutura_base: Path, caminho_relativo: str, esperado: bool
    ) -> None:
        """Verifica se o caminho relativo contém componentes ocultos."""
        caminho: Path = estrutura_base / caminho_relativo
        assert _verificar_oculto(caminho=caminho, raiz_busca=estrutura_base) is esperado
