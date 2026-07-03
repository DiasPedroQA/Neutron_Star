"""Testes para o modelo concreto ItemDiretorio.

Verifica a criação, propriedades, serialização e gerenciamento
de filhos específicos de diretórios.
"""

from pathlib import Path
from typing import Any

import pytest

from src.models.arquivo_info import ItemArquivo
from src.models.diretorio_info import ItemDiretorio


class TestItemDiretorio:
    """Suite de testes para a classe ItemDiretorio."""

    def test_criacao_com_filhos(self) -> None:
        """Verifica a criação de um diretório com uma lista de filhos."""
        filho1 = ItemArquivo(caminho=Path("/tmp/pasta/a.txt"))
        filho2 = ItemDiretorio(caminho=Path("/tmp/pasta/sub"))
        diretorio = ItemDiretorio(
            caminho=Path("/tmp/pasta"),
            qtd_itens=2,
            filhos=(filho1, filho2),
            executavel=True,
        )
        assert diretorio.caminho == Path("/tmp/pasta")
        assert diretorio.eh_diretorio is True
        assert diretorio.qtd_itens == 2
        assert len(diretorio.filhos) == 2
        assert diretorio.filhos[0] is filho1
        assert diretorio.filhos[1] is filho2

    def test_propriedade_listavel(self) -> None:
        """Verifica que listavel é um alias para executavel em diretórios."""
        diretorio_nao_listavel = ItemDiretorio(caminho=Path("/tmp/pasta"), executavel=False)
        assert diretorio_nao_listavel.listavel is False

        diretorio_listavel = ItemDiretorio(caminho=Path("/tmp/pasta"), executavel=True)
        assert diretorio_listavel.listavel is True

    def test_para_dict_com_campos_extras(self) -> None:
        """Verifica que para_dict() inclui 'qtd_itens' e serializa 'filhos'."""
        filho = ItemArquivo(caminho=Path("/tmp/root/a.txt"), tamanho=100)
        diretorio = ItemDiretorio(
            caminho=Path("/tmp/root"),
            qtd_itens=1,
            filhos=(filho,),
            legivel=True,
        )
        dados: dict[str, Any] = diretorio.para_dict()  # ← sem anotação

        assert dados["qtd_itens"] == 1
        assert isinstance(dados["filhos"], list)
        assert len(dados["filhos"]) == 1
        assert dados["filhos"][0]["caminho"] == "/tmp/root/a.txt"
        assert dados["filhos"][0]["tamanho"] == 100
        assert dados["legivel"] is True

    def test_imutabilidade(self) -> None:
        """Garante que a classe frozen não permite alteração de atributos."""
        diretorio = ItemDiretorio(caminho=Path("/tmp/pasta"))
        with pytest.raises(expected_exception=AttributeError):
            diretorio.qtd_itens = 10  # type: ignore
