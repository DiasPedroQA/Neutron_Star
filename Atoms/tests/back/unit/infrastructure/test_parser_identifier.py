# pylint: disable=redefined-outer-name

"""Testes de infraestrutura, serviços e apresentação do Neutron Star."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from Atoms.backend.core.entidades.entidade_arquivo import ModeloArquivo
from Atoms.backend.core.entidades.entidade_bookmark import Favorito
from Atoms.backend.core.entidades.entidade_sistema_operacional import ModeloSistemaOperacional
from Atoms.backend.infrastructure import so_identifier as identifier_module
from Atoms.backend.infrastructure.analisador import TagsFinder
from Atoms.backend.infrastructure.so_identifier import DetectarSistemaOperacional


class TestTagsFinder:
    """Testes para o analisador de favoritos baseado em tags HTML.

    Esta classe valida o suporte a arquivos, o parsing correto de HTML e o tratamento de casos inválidos.
    """

    def test_obter_nome_e_versao_normalizados(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verifica se o nome e a versão do sistema são normalizados corretamente.

        Este teste garante que o detector retorna o nome em minúsculas e a versão conforme fornecida pela plataforma.

        Args:
            monkeypatch: Fixture do pytest usada para simular as respostas de platform.system e platform.release.
        """

        monkeypatch.setattr(identifier_module.platform, "system", lambda: "Linux")
        monkeypatch.setattr(identifier_module.platform, "release", lambda: "5.15.0")

        detector = DetectarSistemaOperacional()

        assert detector.obter_nome_sistema() == "linux"
        assert detector.obter_versao_sistema() == "5.15.0"

    def test_detectar_sistema_operacional_uses_home(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Garante que a detecção do sistema operacional utiliza o diretório home esperado.

        Este teste verifica se o modelo de sistema operacional resultante contém o caminho home fornecido pelo teste.

        Args:
            monkeypatch: Fixture do pytest usada para sobrescrever funções do módulo platform e Path.home.
            tmp_path: Diretório temporário usado como home simulado do usuário.
        """

        monkeypatch.setattr(identifier_module.platform, "system", lambda: "Linux")
        monkeypatch.setattr(identifier_module.platform, "release", lambda: "5.15.0")
        monkeypatch.setattr(identifier_module.Path, "home", lambda: tmp_path)

        detector = DetectarSistemaOperacional()
        modelo: ModeloSistemaOperacional = detector.detectar_sistema_operacional()

        assert modelo.pasta_usuario == tmp_path
        assert modelo.nome_sistema == "linux"

    def test_suporta_html_por_marcacao_e_extensao(self, tmp_path: Path) -> None:
        """Verifica se o analisador suporta arquivos HTML tanto pela marcação quanto pela extensão.

        Este teste garante que arquivos marcados como HTML ou com extensão .html sejam considerados válidos para parsing.

        Args:
            tmp_path: Diretório temporário usado para criar os arquivos de teste.
        """
        arquivo_html = ModeloArquivo(
            nome_arquivo="favoritos.html",
            caminho_arquivo=tmp_path / "favoritos.html",
            tamanho_arquivo_bytes=0,
            eh_html=True,
        )
        arquivo_txt = ModeloArquivo(
            nome_arquivo="favoritos.html",
            caminho_arquivo=tmp_path / "favoritos.html",
            tamanho_arquivo_bytes=0,
            eh_html=False,
        )

        analisador = TagsFinder()

        assert analisador.suporta_arquivo(arquivo=arquivo_html)
        assert analisador.suporta_arquivo(arquivo=arquivo_txt)

    def test_analisar_arquivo_retorna_favoritos_para_html_valido(self, tmp_path: Path) -> None:
        """Verifica se o analisador retorna favoritos válidos a partir de um HTML bem formado.

        Este teste garante que apenas links suportados são convertidos em favoritos e que seus campos principais são preenchidos corretamente.

        Args:
            tmp_path: Diretório temporário usado para criar o arquivo HTML de teste.
        """
        caminho: Path = tmp_path / "favoritos.html"
        caminho.write_text(
            data="""
            <html><body>
            <a href=\"https://example.com\" add_date=\"1672531200\">Example</a>
            <a href=\"ftp://example.com\">Bad</a>
            </body></html>
            """,
            encoding="utf-8",
        )

        arquivo = ModeloArquivo(
            nome_arquivo="favoritos.html",
            caminho_arquivo=caminho,
            tamanho_arquivo_bytes=0,
            eh_html=True,
        )
        analisador = TagsFinder()

        favoritos: list[Favorito] = analisador.analisar_arquivo(arquivo=arquivo)

        assert len(favoritos) == 1
        assert favoritos[0].titulo == "Example"
        assert favoritos[0].url == "https://example.com"
        assert favoritos[0].data_adicao == datetime(year=2023, month=1, day=1, tzinfo=timezone.utc)

    def test_analisar_arquivo_retorna_vazio_para_arquivo_ausente(self, tmp_path: Path) -> None:
        """Verifica se o analisador retorna uma lista vazia quando o arquivo não existe.

        Este teste garante que a ausência do arquivo é tratada de forma silenciosa, sem lançar exceções e sem retornar favoritos.

        Args:
            tmp_path: Diretório temporário usado para construir o caminho de um arquivo inexistente.
        """
        arquivo = ModeloArquivo(
            nome_arquivo="missing.html",
            caminho_arquivo=tmp_path / "missing.html",
            tamanho_arquivo_bytes=0,
            eh_html=True,
        )
        analisador = TagsFinder()

        assert not analisador.analisar_arquivo(arquivo=arquivo)

    def test_analisar_arquivo_retorna_vazio_em_erro_de_leitura(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Verifica se o analisador retorna lista vazia quando ocorre erro de leitura.

        Este teste garante que falhas de I/O ao carregar o HTML resultam em fallback silencioso sem favoritos retornados.

        Args:
            monkeypatch: Fixture do pytest usada para simular uma exceção ao ler o arquivo.
            tmp_path: Diretório temporário usado para criar o arquivo HTML que falhará na leitura.
        """
        caminho: Path = tmp_path / "favoritos.html"
        caminho.write_text("<html></html>", encoding="utf-8")

        def levantar_erro_leitura(self: Path, **kwargs: object) -> str:
            raise OSError("boom")

        monkeypatch.setattr(
            Path,
            "read_text",
            levantar_erro_leitura,
        )

        arquivo = ModeloArquivo(
            nome_arquivo="favoritos.html",
            caminho_arquivo=caminho,
            tamanho_arquivo_bytes=0,
            eh_html=True,
        )
        analisador = TagsFinder()

        assert not analisador.analisar_arquivo(arquivo=arquivo)

    def test_convert_timestamp_returns_epoch_when_invalid(self) -> None:
        """Verifica se timestamps inválidos são convertidos para a época padrão.

        Este teste garante que entradas não numéricas resultem em uma data de fallback consistente em vez de erro.

        """
        analisador = TagsFinder()

        timestamp: datetime = analisador._convert_timestamp(timestamp_str="nota-numero")

        assert timestamp == datetime(year=1970, month=1, day=1, tzinfo=timezone.utc)
