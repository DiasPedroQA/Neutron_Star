# Atoms/tests/aplicacao/test_portas.py
# pylint: disable=abstract-class-instantiated, too-few-public-methods, missing-class-docstring

"""Testes unitários para validação dos contratos abstratos (portas) da aplicação."""

from pathlib import Path
from typing import cast

import pytest

from src.aplicacao.portas import (
    BuscadorPort,
    EscritorPort,
    GerenciadorSistemaPort,
    LeitorHTMLPort,
    ParserPort,
)
from src.dominio.entidades import FavoritoDict, InfoSistema, ResultadoEscaneamento

# ============================================================================
# GerenciadorSistemaPort
# ============================================================================


def test_gerenciador_sistema_port_nao_pode_ser_instanciada_diretamente() -> None:
    """Garante que GerenciadorSistemaPort não pode ser instanciada diretamente."""
    with pytest.raises(expected_exception=TypeError):
        GerenciadorSistemaPort()  # type: ignore[abstract]


def test_gerenciador_sistema_port_aceita_implementacao_concreta() -> None:
    """Garante que uma implementação concreta válida de GerenciadorSistemaPort é aceita."""

    class GerenciadorFalso(GerenciadorSistemaPort):
        """Implementação fake para teste de GerenciadorSistemaPort."""

        def obter_informacoes_so(self) -> InfoSistema:
            """Retorna dicionário estruturado mockado do sistema operacional."""
            return cast(InfoSistema, {"so": "Linux"})

    gerenciador = GerenciadorFalso()
    assert gerenciador.obter_informacoes_so() == {"so": "Linux"}


# ============================================================================
# BuscadorPort
# ============================================================================


def test_buscador_port_nao_pode_ser_instanciada_diretamente() -> None:
    """Garante que BuscadorPort não pode ser instanciada diretamente."""
    with pytest.raises(expected_exception=TypeError):
        BuscadorPort()  # type: ignore[abstract]


def test_buscador_port_exige_ambos_os_metodos_abstratos() -> None:
    """Garante que implementar apenas um método abstrato impede a instanciação."""

    class BuscadorIncompleto(BuscadorPort):
        """Implementação propositalmente incompleta sem o método escanear."""

        def validar_pasta(self, caminho: Path) -> bool:
            """Valida se a pasta existe."""
            return True

    with pytest.raises(expected_exception=TypeError):
        BuscadorIncompleto()  # type: ignore[abstract]


def test_buscador_port_aceita_implementacao_concreta_completa() -> None:
    """Garante que implementar todos os métodos abstratos permite o uso do BuscadorPort."""

    class BuscadorFalso(BuscadorPort):
        """Implementação fake completa para teste de BuscadorPort."""

        def validar_pasta(self, caminho: Path) -> bool:
            """Valida a existência do caminho informado."""
            return caminho.exists()

        def escanear(
            self,
            caminho: Path,
            extensao: str = ".html",
            profundidade: int = 5,
        ) -> ResultadoEscaneamento:
            """Simula a varredura do disco devolvendo estrutura tipada."""
            return cast(ResultadoEscaneamento, {"total_arquivos": 0})

    buscador = BuscadorFalso()
    assert buscador.validar_pasta(caminho=Path("/tmp")) is True
    assert buscador.escanear(caminho=Path("/tmp")) == {"total_arquivos": 0}


# ============================================================================
# LeitorHTMLPort
# ============================================================================


def test_leitor_html_port_nao_pode_ser_instanciada_diretamente() -> None:
    """Garante que LeitorHTMLPort não pode ser instanciada diretamente."""
    with pytest.raises(expected_exception=TypeError):
        LeitorHTMLPort()  # type: ignore[abstract]


def test_leitor_html_port_aceita_implementacao_concreta() -> None:
    """Garante que uma implementação concreta válida de LeitorHTMLPort é aceita."""

    class LeitorFalso(LeitorHTMLPort):
        """Implementação fake para teste de LeitorHTMLPort."""

        def ler_arquivo(self, caminho: Path) -> str:
            """Simula a leitura física de conteúdo HTML."""
            return "<html></html>"

    leitor = LeitorFalso()
    assert leitor.ler_arquivo(caminho=Path("bookmarks.html")) == "<html></html>"


# ============================================================================
# EscritorPort
# ============================================================================


def test_escritor_port_nao_pode_ser_instanciada_diretamente() -> None:
    """Garante que EscritorPort não pode ser instanciada diretamente."""
    with pytest.raises(expected_exception=TypeError):
        EscritorPort()  # type: ignore[abstract]


def test_escritor_port_aceita_implementacao_concreta() -> None:
    """Garante que uma implementação concreta válida de EscritorPort é aceita."""

    class EscritorFalso(EscritorPort):
        """Implementação fake para teste de EscritorPort."""

        def salvar_lote(
            self,
            caminho_original: Path,
            dados: list[FavoritoDict] | list[dict[str, str]],
            extensao: str,
            sufixo: str = "_processado",
            pasta_saida: Path | None = None,
        ) -> str:
            """Simula o salvamento de arquivos em disco calculando o caminho."""
            nome_final: str = f"{caminho_original.stem}{sufixo}.{extensao}"
            base: Path = pasta_saida if pasta_saida is not None else caminho_original.parent
            return str(base / nome_final)

    escritor = EscritorFalso()
    resultado: str = escritor.salvar_lote(
        caminho_original=Path("favoritos.html"),
        dados=[{"Titulo": "GitHub"}],  # type: ignore[list-item]
        extensao="json",
    )
    assert resultado == "favoritos_processado.json"


# ============================================================================
# ParserPort
# ============================================================================


def test_parser_port_nao_pode_ser_instanciada_diretamente() -> None:
    """Garante que ParserPort não pode ser instanciada diretamente."""
    with pytest.raises(expected_exception=TypeError):
        ParserPort()  # type: ignore[abstract]


def test_parser_port_aceita_implementacao_concreta() -> None:
    """Garante que uma implementação concreta válida de ParserPort é aceita."""

    class ParserFalso(ParserPort):
        """Implementação fake para teste de ParserPort."""

        def extrair_favoritos(self, html_conteudo: str) -> list:
            """Simula a extração de favoritos de uma string HTML."""
            return [{"titulo": "GitHub"}] if html_conteudo else []

    parser = ParserFalso()
    assert not parser.extrair_favoritos(html_conteudo="")
    assert parser.extrair_favoritos(html_conteudo="<html></html>") == [{"titulo": "GitHub"}]
