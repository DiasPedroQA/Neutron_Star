# pylint: disable=redefined-outer-name

"""Testes de infraestrutura, serviços e apresentação do Neutron Star."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from _pytest.capture import CaptureResult

from Atoms.backend.core.entidades.entidade_bookmark import Favorito
from Atoms.backend.core.entidades.entidade_sistema_operacional import ModeloSistemaOperacional
from Atoms.frontend.cli_display import (
    cli_exibir_arquivo,
    cli_exibir_estatisticas,
    cli_exibir_favoritos,
    cli_exibir_pasta,
    cli_exibir_sistema_operacional,
)


class TestFrontendDisplay:
    """Testes de exibição no frontend para saída em linha de comando.

    Esta classe valida que as funções de exibição imprimem as informações esperadas.
    """

    def test_display_functions_print_expected_output(self, capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
        """Verifica se as funções de exibição imprimem as saídas esperadas.

        Este teste garante que as informações principais são renderizadas
        corretamente no terminal.

        Args:
            capsys: Fixture do pytest utilizada para capturar a saída padrão.
            tmp_path: Diretório temporário utilizado para simular paths no sistema de arquivos.
        """
        so: ModeloSistemaOperacional = ModeloSistemaOperacional(
            nome_sistema="linux",
            versao_sistema="5.15.0",
            pasta_usuario=tmp_path,
        )
        cli_exibir_sistema_operacional(so=so)
        cli_exibir_estatisticas(estatisticas={"favoritos": 2})
        cli_exibir_favoritos(
            favoritos=[
                Favorito(
                    titulo="A",
                    url="https://a",
                    data_adicao=datetime(year=1970, month=1, day=1, tzinfo=timezone.utc),
                )
            ]
        )
        cli_exibir_pasta(
            nome_pasta="home",
            caminho_absoluto=tmp_path,
            pasta_pai=None,
            subpastas=[],
            subarquivos=[],
        )
        cli_exibir_arquivo(
            nome_arquivo="favoritos.html",
            caminho_arquivo=str(tmp_path / "favoritos.html"),
            tamanho_arquivo=123,
            eh_html=True,
        )

        captured = capsys.readouterr()

        assert "Sistema:" in captured.out
        assert "favoritos: 2" in captured.out
        assert "https://a" in captured.out
        assert "Pasta" in captured.out
        assert "favoritos.html" in captured.out

    def test_cli_exibir_favoritos_prints_message_when_no_favoritos(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verifica se a função de exibição de favoritos mostra mensagem quando não há favoritos.

        Este teste garante que o usuário recebe um feedback textual apropriado ao tentar listar uma coleção vazia de favoritos.

        Args:
            capsys: Fixture do pytest utilizada para capturar a saída padrão.
        """
        cli_exibir_favoritos(favoritos=[])
        captured: CaptureResult[str] = capsys.readouterr()

        assert "Nenhum favorito encontrado." in captured.out

    def test_cli_exibir_pasta_respects_custom_title(self, capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
        """Verifica se a função de exibição de pasta respeita o título customizado.

        Este teste garante que o cabeçalho de saída usa o título fornecido e continua exibindo corretamente as estatísticas de subpastas e arquivos.

        Args:
            capsys: Fixture do pytest utilizada para capturar a saída padrão.
            tmp_path: Diretório temporário utilizado como caminho absoluto da pasta exibida.
        """
        cli_exibir_pasta(
            nome_pasta="home",
            caminho_absoluto=tmp_path,
            pasta_pai=None,
            subpastas=[],
            subarquivos=[],
            titulo="Raiz",
        )
        captured: CaptureResult[str] = capsys.readouterr()

        assert "Raiz:" in captured.out
        assert "Subpastas: 0 | Arquivos: 0" in captured.out
