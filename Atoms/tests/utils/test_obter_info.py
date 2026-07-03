"""Testes para a função obter_info_arquivo (criação de ItemArquivo a partir de um caminho)."""

# =============================================================================
# obter_info_arquivo
# =============================================================================
from pathlib import Path

import pytest

from src.models.arquivo_info import ItemArquivo
from src.utils.system_tools import obter_info_arquivo
from tests.conftest import criar_arquivo_fake, criar_pasta_fake


class TestObterInfoArquivo:
    """Testes para obter_info_arquivo."""

    def test_arquivo_existente_retorna_item(self, arquivo_simples: Path) -> None:
        """Arquivo existente retorna ItemArquivo."""
        assert isinstance(obter_info_arquivo(arquivo_simples), ItemArquivo)

    def test_diretorio_retorna_none(self, tmp_path: Path) -> None:
        """Diretório retorna None."""
        pasta = criar_pasta_fake(tmp_path / "subdir")
        assert obter_info_arquivo(pasta) is None

    def test_arquivo_inexistente_retorna_none(self, tmp_path: Path) -> None:
        """Arquivo inexistente retorna None."""
        assert obter_info_arquivo(tmp_path / "missing.txt") is None

    def test_arquivo_sem_leitura_retorna_legivel_false(self, tmp_path: Path) -> None:
        """Arquivo sem permissão de leitura tem legivel=False."""
        arquivo: Path = criar_arquivo_fake(caminho_arquivo=tmp_path / "secret.txt", conteudo=b"top secret")
        arquivo.chmod(0o200)  # apenas escrita
        item: ItemArquivo | None = obter_info_arquivo(caminho=arquivo)
        assert isinstance(item, ItemArquivo)
        assert item.legivel is False

    @pytest.mark.parametrize(
        ("conteudo", "calcular_hash"),
        [
            (b"hello world", False),
            (b"", False),
            (b"conteudo para hash", True),
        ],
        ids=["texto-sem-hash", "vazio-sem-hash", "com-hash"],
    )
    def test_happy_paths_parametrizados(self, tmp_path: Path, conteudo: bytes, calcular_hash: bool) -> None:
        """Caminhos felizes com e sem hash."""
        arquivo: Path = criar_arquivo_fake(caminho_arquivo=tmp_path / "arquivo.txt", conteudo=conteudo)
        item: ItemArquivo | None = obter_info_arquivo(caminho=arquivo, calcular_hash=calcular_hash)
        assert isinstance(item, ItemArquivo)
        assert item.caminho == arquivo
        assert (item.hash_checksum is not None) is calcular_hash
