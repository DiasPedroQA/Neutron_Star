"""Testes para as definições de tipos TypedDict.

.. module:: tests.utils.test_tipos
   :platform: Unix, Windows
   :synopsis: Validação de contratos de dados estruturados.
"""

from typing import cast

import pytest

from src.utils.tipos import (
    MetadadosArquivo,
    FavoritoDict,
    StatusConversao,
    InfoSistema,
    ResultadoEscaneamento,
    ArquivoConvertido,
    ErroConversao,
    AtalhoSugerido,
)


class TestMetadadosArquivo:
    """Testes para o tipo MetadadosArquivo."""

    def test_criar_metadados_arquivo_valido(self) -> None:
        """Valida criação de metadados com todos os campos."""
        arquivo: MetadadosArquivo = {
            "nome": "bookmarks.html",
            "caminho_completo": "/home/user/bookmarks.html",
            "tamanho_kb": 245.67,
            "modificado_em": "25/09/2026 14:30:00",
            "selecionado": True,
        }
        assert arquivo["nome"] == "bookmarks.html"
        assert arquivo["selecionado"] is True
        assert arquivo["tamanho_kb"] == 245.67


class TestFavoritoDict:
    """Testes para o tipo FavoritoDict."""

    def test_criar_favorito_valido(self) -> None:
        """Valida estrutura de um favorito/link."""
        favorito: FavoritoDict = {
            "Titulo": "Python Docs",
            "URL": "https://docs.python.org",
            "Pasta": "Favoritos / Desenvolvimento",
            "Data_Adicao": "15/08/2026 10:45:00",
        }
        assert favorito["Titulo"] == "Python Docs"
        assert "https://" in favorito["URL"]

    def test_favorito_sem_titulo_permitido(self) -> None:
        """Valida favorito com título vazio (Sem título)."""
        favorito: FavoritoDict = {
            "Titulo": "Sem título",
            "URL": "https://example.com",
            "Pasta": "Não categorizado",
            "Data_Adicao": "Sem data",
        }
        assert favorito["Titulo"] == "Sem título"


class TestStatusConversao:
    """Testes para o tipo StatusConversao."""

    def test_status_conversao_em_progresso(self) -> None:
        """Valida status durante processamento."""
        status: StatusConversao = {
            "progresso": 50,
            "arquivo_atual": "bookmarks2.html",
            "concluido": False,
            "sucesso": True,
            "arquivos_convertidos": [
                {
                    "origem": "bookmarks1.html",
                    "destino": "bookmarks1_processado.json",
                    "total_links": 30,
                }
            ],
            "erros": [],
        }
        assert status["progresso"] == 50
        assert status["concluido"] is False
        assert len(status["arquivos_convertidos"]) == 1

    def test_status_conversao_finalizado_com_erros(self) -> None:
        """Valida status ao término com falhas registradas."""
        status: StatusConversao = {
            "progresso": 100,
            "arquivo_atual": "",
            "concluido": True,
            "sucesso": True,
            "arquivos_convertidos": [{"origem": "ok.html", "destino": "ok.json", "total_links": 5}],
            "erros": [{"arquivo": "corrupted.html", "erro": "Arquivo inacessível"}],
        }
        assert status["concluido"] is True
        assert len(status["erros"]) == 1


class TestInfoSistema:
    """Testes para o tipo InfoSistema."""

    def test_info_sistema_completa(self) -> None:
        """Valida informações do sistema operacional."""
        info: InfoSistema = {
            "so": "Linux (5.10.0)",
            "usuario": "pedro",
            "pasta_home": "/home/pedro",
            "atalhos_sugeridos": [
                {"label": "Pasta Home (~/)", "caminho": "~/"},
                {"label": "Documentos (~Documents)", "caminho": "~/Documents"},
            ],
        }
        assert info["usuario"] == "pedro"
        assert len(info["atalhos_sugeridos"]) == 2


class TestResultadoEscaneamento:
    """Testes para o tipo ResultadoEscaneamento."""

    def test_resultado_escaneamento_com_multiplos_arquivos(self) -> None:
        """Valida resultado de varredura de diretório."""
        resultado: ResultadoEscaneamento = {
            "caminho_varrido": "/home/pedro/Documents",
            "total_arquivos": 3,
            "tamanho_total_mb": 2.45,
            "data_busca": "25/09/2026 14:30:00",
            "arquivos": [
                {
                    "nome": "bookmarks.html",
                    "caminho_completo": "/home/pedro/Documents/bookmarks.html",
                    "tamanho_kb": 1024.5,
                    "modificado_em": "20/09/2026 10:00:00",
                    "selecionado": True,
                },
                {
                    "nome": "favoritos.html",
                    "caminho_completo": "/home/pedro/Documents/favoritos.html",
                    "tamanho_kb": 512.3,
                    "modificado_em": "21/09/2026 11:00:00",
                    "selecionado": False,
                },
            ],
        }
        assert resultado["total_arquivos"] == 3
        assert len(resultado["arquivos"]) == 2
        assert resultado["arquivos"][0]["selecionado"] is True


class TestTiposIntegrados:
    """Testes de integração entre múltiplos tipos."""

    def test_fluxo_completo_conversao(self) -> None:
        """Valida fluxo completo: escanear → processar → resultado."""
        scan: ResultadoEscaneamento = {
            "caminho_varrido": "~/Downloads",
            "total_arquivos": 1,
            "tamanho_total_mb": 1.0,
            "data_busca": "25/09/2026 14:00:00",
            "arquivos": [
                {
                    "nome": "test.html",
                    "caminho_completo": "/home/user/Downloads/test.html",
                    "tamanho_kb": 1024.0,
                    "modificado_em": "25/09/2026 13:00:00",
                    "selecionado": True,
                }
            ],
        }

        status: StatusConversao = {
            "progresso": 100,
            "arquivo_atual": "test.html",
            "concluido": True,
            "sucesso": True,
            "arquivos_convertidos": [
                {
                    "origem": scan["arquivos"][0]["nome"],
                    "destino": "test_processado.json",
                    "total_links": 42,
                }
            ],
            "erros": [],
        }

        assert status["sucesso"] is True
        assert status["arquivos_convertidos"][0]["total_links"] == 42
