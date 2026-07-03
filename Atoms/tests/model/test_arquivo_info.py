"""Testes para o modelo concreto ItemArquivo.

Verifica a criação, propriedades, serialização e comparação
de metadados específicos de arquivos.
"""

from datetime import datetime
from pathlib import Path

import pytest

from src.models.arquivo_info import ItemArquivo


class TestItemArquivo:
    """Suite de testes para a classe ItemArquivo."""

    def test_criacao_completa(self) -> None:
        """Verifica a instanciação com todos os atributos preenchidos."""
        modificado = datetime(year=2025, month=1, day=1, hour=12, minute=0, second=0)
        arquivo = ItemArquivo(
            caminho=Path("/tmp/bar.txt"),
            modificado=modificado,
            tamanho=1024,
            legivel=True,
            gravavel=False,
            executavel=True,
            oculto=True,
            tipo_mime="text/plain",
            hash_checksum="abc123",
        )
        assert arquivo.caminho == Path("/tmp/bar.txt")
        assert arquivo.modificado == modificado
        assert arquivo.tamanho == 1024
        assert arquivo.legivel is True
        assert arquivo.gravavel is False
        assert arquivo.executavel is True
        assert arquivo.oculto is True
        assert arquivo.tipo_mime == "text/plain"
        assert arquivo.hash_checksum == "abc123"
        assert arquivo.eh_diretorio is False

    def test_metadados_coincidem(self) -> None:
        """Verifica o método de comparação de metadados entre arquivos."""
        dt = datetime(year=2025, month=1, day=1, hour=10, minute=0, second=0)

        a1 = ItemArquivo(
            caminho=Path("/tmp/a.txt"),
            tamanho=100,
            modificado=dt,
            legivel=True,
            gravavel=False,
            executavel=False,
        )
        a2 = ItemArquivo(
            caminho=Path("/tmp/b.txt"),
            tamanho=100,
            modificado=dt,
            legivel=True,
            gravavel=False,
            executavel=False,
        )
        a3 = ItemArquivo(
            caminho=Path("/tmp/c.txt"),
            tamanho=200,
            modificado=dt,
            legivel=True,
            gravavel=False,
            executavel=False,
        )

        # Mesmo caminho deve retornar True independente dos outros campos
        mesmo_caminho = ItemArquivo(caminho=Path("/tmp/a.txt"), tamanho=999)
        assert a1.metadados_coincidem(outro=mesmo_caminho) is True

        # Caminhos diferentes mas metadados iguais
        assert a1.metadados_coincidem(outro=a2) is True

        # Caminhos diferentes e metadados diferentes
        assert a1.metadados_coincidem(outro=a3) is False

    def test_para_dict_com_campos_extras(self) -> None:
        """Verifica que para_dict() inclui 'tipo_mime' e 'hash_checksum'."""
        arquivo = ItemArquivo(
            caminho=Path("/tmp/data.json"),
            tamanho=2048,
            tipo_mime="application/json",
            hash_checksum="sha256:xyz",
        )
        dados: dict[str, str | int | bool | None] = arquivo.para_dict()

        # Campos extras
        assert dados["tipo_mime"] == "application/json"
        assert dados["hash_checksum"] == "sha256:xyz"
        # Verifica que um campo da base ainda está lá
        assert dados["tamanho"] == 2048

    def test_imutabilidade(self) -> None:
        """Garante que a classe frozen não permite alteração de atributos."""
        arquivo = ItemArquivo(caminho=Path("/tmp/x.txt"))
        with pytest.raises(expected_exception=AttributeError):
            arquivo.tamanho = 999  # type: ignore
