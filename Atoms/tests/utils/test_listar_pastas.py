"""Testes para a função listar_diretorio (listagem de diretórios com filtros e tratamento de erros)."""

# =============================================================================
# listar_diretorio
# =============================================================================
import os
from pathlib import Path

from pytest_mock import MockerFixture

from src.models.item_neutro import ItemBase
from src.utils.system_tools import listar_diretorio


def _criar_arquivo_fake(caminho: Path, conteudo: bytes = b"") -> Path:
    """Cria um arquivo com conteúdo no sistema de arquivos temporário."""
    caminho.write_bytes(conteudo)
    return caminho


def _criar_pasta_fake(caminho: Path) -> Path:
    """Cria um diretório no sistema de arquivos temporário."""
    caminho.mkdir(parents=True, exist_ok=True)
    return caminho


class TestListarDiretorio:
    """Testes para listar_diretorio."""

    @staticmethod
    def _nomes(resultado: list[ItemBase]) -> set[str]:
        """Extrai os nomes dos itens de uma lista de resultados."""
        return {item.nome for item in resultado}

    @staticmethod
    def _estrutura_padrao(raiz: Path) -> None:
        """Cria estrutura de diretórios reutilizável nos testes de listagem."""
        _criar_arquivo_fake(caminho=raiz / "arquivo.txt")
        _criar_pasta_fake(caminho=raiz / "subdir")
        _criar_arquivo_fake(caminho=raiz / ".oculto.txt")

    def test_diretorio_vazio_retorna_lista_vazia(self, tmp_path: Path) -> None:
        """Diretório vazio retorna lista vazia."""
        pasta: Path = _criar_pasta_fake(caminho=tmp_path / "vazio")
        assert not listar_diretorio(caminho=pasta)

    def test_lista_arquivos_pastas_e_ocultos(self, tmp_path: Path) -> None:
        """Lista inclui arquivos, pastas e itens ocultos."""
        self._estrutura_padrao(raiz=tmp_path)
        nomes: set[str] = self._nomes(resultado=listar_diretorio(caminho=tmp_path))
        assert {"arquivo.txt", "subdir", ".oculto.txt"}.issubset(nomes)

    def test_filtro_glob_por_extensao(self, tmp_path: Path) -> None:
        """Padrão glob filtra corretamente."""
        self._estrutura_padrao(raiz=tmp_path)
        nomes: set[str] = self._nomes(resultado=listar_diretorio(caminho=tmp_path, padrao_glob="*.txt"))
        assert "arquivo.txt" in nomes
        assert ".oculto.txt" in nomes
        assert "subdir" not in nomes

    def test_segue_symlinks_quando_solicitado(self, tmp_path: Path) -> None:
        """Com seguir_symlinks=True, links são incluídos."""
        alvo: Path = _criar_arquivo_fake(caminho=tmp_path / "arquivo.txt")
        os.symlink(str(alvo), str(tmp_path / "link_symbolic"))
        nomes: set[str] = self._nomes(resultado=listar_diretorio(caminho=tmp_path, seguir_symlinks=True))
        assert "link_symbolic" in nomes

    def test_permission_error_retorna_lista_vazia(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """PermissionError ao listar retorna lista vazia."""
        mocker.patch.object(Path, "iterdir", side_effect=PermissionError)
        assert not listar_diretorio(caminho=tmp_path)

    def test_itens_que_falham_sao_ignorados(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Itens que falham ao serem criados são ignorados."""
        _criar_arquivo_fake(caminho=tmp_path / "arquivo.txt")
        mocker.patch("src.utils.system_tools.criar_item", return_value=None)
        assert not listar_diretorio(caminho=tmp_path)
