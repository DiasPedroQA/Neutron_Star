# pylint: disable=abstract-class-instantiated

"""Testes para a classe base abstrata ItemBase.

Como ItemBase é abstrata, os testes utilizam as classes concretas
ItemArquivo e ItemDiretorio para verificar o comportamento herdado.
"""

from datetime import datetime
from pathlib import Path

import pytest

from src.models.arquivo_info import ItemArquivo
from src.models.diretorio_info import ItemDiretorio
from src.models.item_neutro import ItemBase


class TestItemBase:
    """Suite de testes para os atributos e métodos comuns de ItemBase."""

    def test_criacao_via_subclasses(self) -> None:
        """Verifica que ItemBase não pode ser instanciada diretamente,
        mas suas subclasses funcionam corretamente.
        """
        with pytest.raises(expected_exception=TypeError):
            ItemBase(caminho=Path("/tmp/x"))  # type: ignore

        arquivo = ItemArquivo(caminho=Path("/tmp/a.txt"))
        diretorio = ItemDiretorio(caminho=Path("/tmp/pasta"))
        assert isinstance(arquivo, ItemBase)
        assert isinstance(diretorio, ItemBase)

    def test_propriedades_nome_e_sufixo(self, tmp_path: Path) -> None:
        """Verifica o cálculo correto de 'nome' e 'sufixo'."""
        arquivo_path: Path = tmp_path / "documento.pdf"
        arquivo_path.write_text(data="conteudo")  # cria um arquivo real
        arquivo = ItemArquivo(caminho=arquivo_path)
        self._validate_item_file(
            tipo_objeto=arquivo, nome_objeto="documento.pdf", sufixo_objeto=".pdf", eh_diretorio_objeto=False
        )

        diretorio_path: Path = tmp_path / "pasta"
        diretorio_path.mkdir()  # cria um diretório real
        diretorio = ItemDiretorio(caminho=diretorio_path)
        self._validate_item_file(tipo_objeto=diretorio, nome_objeto="pasta", sufixo_objeto="", eh_diretorio_objeto=True)

    def _validate_item_file(self, tipo_objeto, nome_objeto, sufixo_objeto, eh_diretorio_objeto) -> None:
        """Valida os atributos nome, sufixo e eh_diretorio de um ItemBase."""
        assert isinstance(tipo_objeto, ItemBase)
        assert isinstance(nome_objeto, str)
        assert isinstance(sufixo_objeto, str)
        assert isinstance(eh_diretorio_objeto, bool)
        assert tipo_objeto.caminho == tipo_objeto.caminho  # Verifica que o caminho é consistente
        assert tipo_objeto.caminho.name == nome_objeto
        assert tipo_objeto.caminho.suffix == sufixo_objeto
        assert tipo_objeto.caminho.is_dir() is eh_diretorio_objeto
        assert tipo_objeto.caminho.is_file() is not eh_diretorio_objeto
        assert tipo_objeto.caminho.is_symlink() is False  # Não estamos testando links simbólicos aqui
        assert tipo_objeto.nome == nome_objeto
        assert tipo_objeto.sufixo == sufixo_objeto
        assert tipo_objeto.eh_diretorio is eh_diretorio_objeto

    def test_para_dict_base(self) -> None:
        """Verifica que o dicionário gerado por para_dict() contém
        os campos obrigatórios definidos na base.
        """
        modificado = datetime(year=2025, month=6, day=1, hour=10, minute=30, second=0)
        arquivo = ItemArquivo(
            caminho=Path("/tmp/foo.txt"),
            modificado=modificado,
            tamanho=512,
            legivel=True,
            gravavel=False,
            executavel=True,
            oculto=False,
        )
        dados: dict[str, str | int | bool | None] = arquivo.para_dict()

        # Campos obrigatórios da base
        assert dados["caminho"] == "/tmp/foo.txt"
        assert dados["nome"] == "foo.txt"
        assert dados["modificado"] == "2025-06-01T10:30:00"
        assert dados["tamanho"] == 512
        assert dados["eh_diretorio"] is False
        assert dados["legivel"] is True
        assert dados["gravavel"] is False
        assert dados["executavel"] is True
        assert dados["oculto"] is False
