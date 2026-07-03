"""Testes para a função criar_item (criação de ItemArquivo ou ItemDiretorio a partir de um caminho).

Verifica a criação de itens a partir de caminhos existentes, incluindo a detecção
de tipo (arquivo/diretório), permissões, preenchimento de hash (quando solicitado)
e tratamento de erros.
"""

import hashlib
from pathlib import Path

from pytest_mock import MockerFixture

from src.models.arquivo_info import ItemArquivo
from src.models.diretorio_info import ItemDiretorio
from src.models.item_neutro import ItemBase
from src.utils.system_tools import criar_item


def _criar_arquivo_fake(caminho: Path, conteudo: bytes = b"") -> Path:
    """Cria um arquivo com conteúdo no sistema de arquivos temporário."""
    caminho.write_bytes(data=conteudo)
    return caminho


def _criar_pasta_fake(caminho: Path) -> Path:
    """Cria um diretório no sistema de arquivos temporário."""
    caminho.mkdir(parents=True, exist_ok=True)
    return caminho


class TestCriarItem:
    """Testes para criar_item."""

    def test_cria_item_arquivo(self, tmp_path: Path) -> None:
        """Cria ItemArquivo com metadados corretos."""
        arquivo: Path = _criar_arquivo_fake(caminho=tmp_path / "arquivo.txt", conteudo=b"hello world")
        item: ItemBase = self._criacao_de_item(caminho=arquivo, tipo_esperado=ItemArquivo, nome_esperado="arquivo.txt")
        assert item.caminho == arquivo
        assert item.tamanho == 11
        assert item.tipo_mime is not None  # type: ignore
        assert item.hash_checksum is None  # type: ignore

    def test_cria_arquivo_com_hash(self, tmp_path: Path) -> None:
        """Com calcular_hash=True, o checksum é preenchido."""
        conteudo = b"hello world"
        arquivo: Path = _criar_arquivo_fake(caminho=tmp_path / "arquivo.txt", conteudo=conteudo)
        item: ItemBase | None = criar_item(caminho=arquivo, calcular_hash=True)
        assert isinstance(item, ItemArquivo)
        assert item.hash_checksum == hashlib.sha256(conteudo).hexdigest()

    def test_cria_diretorio_listavel(self, tmp_path: Path) -> None:
        """Diretório listável tem qtd_itens preenchido."""
        pasta: Path = _criar_pasta_fake(caminho=tmp_path / "subdir")
        item: ItemBase = self._criacao_de_item(caminho=pasta, tipo_esperado=ItemDiretorio, nome_esperado="subdir")
        assert item.executavel is True
        assert item.qtd_itens == 0  # type: ignore

    def _criacao_de_item(self, caminho: Path, tipo_esperado: type[ItemBase], nome_esperado: str) -> ItemBase:
        """Helper para criar item e verificar tipo/nome.

        Retorna o item criado (não None) para uso nos testes.
        """
        result: ItemBase | None = criar_item(caminho=caminho)
        assert result is not None
        assert isinstance(result, tipo_esperado)
        assert result.nome == nome_esperado
        return result

    def test_cria_diretorio_sem_permissao_de_execucao(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Diretório sem execução tem qtd_itens=None."""
        pasta: Path = _criar_pasta_fake(caminho=tmp_path / "sem_permissao")
        mocker.patch("os.access", return_value=False)
        mocker.patch.object(Path, "iterdir", side_effect=PermissionError)

        item: ItemBase | None = criar_item(caminho=pasta)
        assert isinstance(item, ItemDiretorio)
        assert item.executavel is False
        assert item.qtd_itens is None

    def test_caminho_inexistente_retorna_none(self, tmp_path: Path) -> None:
        """Caminho inexistente retorna None."""
        assert criar_item(caminho=tmp_path / "inexistente") is None

    # def test_falha_ao_determinar_tipo_retorna_none(
    #     self, tmp_path: Path, mocker: MockerFixture
    # ) -> None:
    #     """Se is_file/is_dir falham, retorna None."""
    #     arquivo: Path = _criar_arquivo_fake(
    #         caminho=tmp_path / "arquivo.txt", conteudo=b"test"
    #     )
    #     mocker.patch.object(Path, "is_file", side_effect=OSError)
    #     mocker.patch.object(Path, "is_dir", side_effect=OSError)
    #     '''/home/diaspedro/Desktop/PyProject/Neutron_Star/Atoms/tests/utils/test_criar_item.py::TestCriarItem::test_falha_ao_determinar_tipo_retorna_none failed: /usr/lib/python3.12/unittest/mock.py:1567: in __enter__
    #         setattr(self.target, self.attribute, new_attr)
    #     E   AttributeError: 'PosixPath' object attribute 'is_file' is read-only

    #     During handling of the above exception, another exception occurred:
    #     Atoms/tests/utils/test_criar_item.py:105: in test_falha_ao_determinar_tipo_retorna_none
    #         mocker.patch.object(arquivo, "is_file", side_effect=OSError)
    #     .venv/lib/python3.12/site-packages/pytest_mock/plugin.py:297: in object
    #         return self._start_patch(
    #     .venv/lib/python3.12/site-packages/pytest_mock/plugin.py:266: in _start_patch
    #         mocked: MockType = p.start()
    #                         ^^^^^^^^^
    #     /usr/lib/python3.12/unittest/mock.py:1606: in start
    #         result = self.__enter__()
    #                 ^^^^^^^^^^^^^^^^
    #     /usr/lib/python3.12/unittest/mock.py:1580: in __enter__
    #         if not self.__exit__(*sys.exc_info()):
    #             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #     /usr/lib/python3.12/unittest/mock.py:1588: in __exit__
    #         delattr(self.target, self.attribute)
    #     E   AttributeError: 'PosixPath' object attribute 'is_file' is read-only
    #     '''
    #     assert criar_item(caminho=arquivo) is None
