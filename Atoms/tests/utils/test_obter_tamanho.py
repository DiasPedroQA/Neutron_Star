"""Testes para a função _obter_tamanho_seguro (obtenção de tamanho de arquivo com fallback para stat)."""

# =============================================================================
# _obter_tamanho_seguro
# =============================================================================
from pathlib import Path

from pytest_mock import MockerFixture

from src.utils.system_tools import _obter_tamanho_seguro


def _criar_arquivo_fake(caminho: Path, conteudo: bytes = b"") -> Path:
    caminho.write_bytes(conteudo)
    return caminho


class TestObterTamanhoSeguro:
    """Testes para _obter_tamanho_seguro."""

    def test_tamanho_nos_dados_e_retornado_direto(self, tmp_path: Path) -> None:
        """Tamanho presente nos dados é retornado imediatamente."""
        arquivo: Path = _criar_arquivo_fake(caminho=tmp_path / "arquivo.txt")
        resultado: int | None = _obter_tamanho_seguro(dados={"tamanho": 100}, caminho=arquivo)
        assert resultado == 100

    def test_fallback_via_stat_quando_tamanho_ausente(self, tmp_path: Path) -> None:
        """Usa stat como fallback se tamanho não estiver nos dados."""
        arquivo: Path = _criar_arquivo_fake(caminho=tmp_path / "arquivo.txt", conteudo=b"hello world")
        resultado: int | None = _obter_tamanho_seguro(dados={"tamanho": None}, caminho=arquivo)
        assert resultado == 11

    def test_retorna_none_quando_stat_falha(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Retorna None se tanto os dados quanto o stat falham."""
        arquivo: Path = _criar_arquivo_fake(caminho=tmp_path / "arquivo.txt")
        mocker.patch.object(Path, "stat", side_effect=OSError)
        resultado: int | None = _obter_tamanho_seguro({"tamanho": None}, arquivo)
        assert resultado is None
