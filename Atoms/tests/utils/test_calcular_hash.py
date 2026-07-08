"""Testes para a função _calcular_hash (cálculo de SHA-256 de arquivos)."""

# =============================================================================
# _calcular_hash
# =============================================================================
import hashlib
from pathlib import Path

from pytest_mock import MockerFixture
from src.utils.system_tools import _calcular_hash


class TestCalcularHash:
    """Testes para _calcular_hash."""

    _CONTEUDO: bytes = b"conteudo para hash"
    _HASH_ESPERADO: str = hashlib.sha256(_CONTEUDO).hexdigest()

    def test_hash_coincide_com_esperado(self, arquivo_hash: Path) -> None:
        """Hash calculado bate com o esperado."""
        assert _calcular_hash(caminho=arquivo_hash) == self._HASH_ESPERADO

    def test_arquivo_inexistente_retorna_none(self, tmp_path: Path) -> None:
        """Arquivo inexistente retorna None."""
        assert _calcular_hash(caminho=tmp_path / "inexistente.txt") is None

    def test_erro_de_leitura_retorna_none(self, arquivo_hash: Path, mocker: MockerFixture) -> None:
        """Erro de IO durante leitura retorna None."""
        mocker.patch("builtins.open", side_effect=PermissionError)
        assert _calcular_hash(caminho=arquivo_hash) is None
