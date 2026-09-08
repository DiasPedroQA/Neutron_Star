# Atoms/tests/aplicacao/test_portas.py

"""Testes unitários para os contratos abstratos (portas) da aplicação."""

from pathlib import Path

import pytest

from src.aplicacao.portas import (
    BuscadorPort,
    EscritorPort,
    GerenciadorSistemaPort,
    LeitorHTMLPort,
    ParserPort,
)


def test_gerenciador_sistema_port_nao_pode_ser_instanciada_diretamente() -> None:
    """Garante que a ABC não pode ser usada sem uma implementação concreta."""
    with pytest.raises(TypeError):
        GerenciadorSistemaPort()  # pylint: disable=abstract-class-instantiated


def test_gerenciador_sistema_port_aceita_implementacao_concreta() -> None:
    """Garante que uma subclasse que implementa o contrato pode ser instanciada e usada."""

    class GerenciadorFalso(GerenciadorSistemaPort):
        """Implementação fake mínima usada apenas neste teste."""

        def obter_informacoes_so(self) -> dict:
            return {"so": "Linux"}

    gerenciador = GerenciadorFalso()

    assert gerenciador.obter_informacoes_so() == {"so": "Linux"}


def test_buscador_port_nao_pode_ser_instanciada_diretamente() -> None:
    """Garante que a ABC não pode ser usada sem uma implementação concreta."""
    with pytest.raises(TypeError):
        BuscadorPort()  # pylint: disable=abstract-class-instantiated


def test_buscador_port_exige_ambos_os_metodos_abstratos() -> None:
    """Garante que implementar só um dos dois métodos abstratos ainda impede a instanciação."""

    class BuscadorIncompleto(BuscadorPort):
        """Implementação deliberadamente parcial, faltando o método escanear."""

        def validar_pasta(self, caminho: Path) -> bool:
            return True

    with pytest.raises(TypeError):
        BuscadorIncompleto()  # pylint: disable=abstract-class-instantiated


def test_buscador_port_aceita_implementacao_concreta_completa() -> None:
    """Garante que implementar os dois métodos abstratos permite a instanciação e o uso."""

    class BuscadorFalso(BuscadorPort):
        """Implementação fake mínima usada apenas neste teste."""

        def validar_pasta(self, caminho: Path) -> bool:
            return caminho.exists()

        def escanear(self, caminho: Path) -> dict:
            return {"total_arquivos": 0}

    buscador = BuscadorFalso()

    assert buscador.validar_pasta(caminho=Path("/tmp")) is True
    assert buscador.escanear(caminho=Path("/tmp")) == {"total_arquivos": 0}


def test_leitor_html_port_nao_pode_ser_instanciada_diretamente() -> None:
    """Garante que a ABC não pode ser usada sem uma implementação concreta."""
    with pytest.raises(TypeError):
        LeitorHTMLPort()  # pylint: disable=abstract-class-instantiated


def test_leitor_html_port_aceita_implementacao_concreta() -> None:
    """Garante que uma subclasse que implementa o contrato pode ser instanciada e usada."""

    class LeitorFalso(LeitorHTMLPort):
        """Implementação fake mínima usada apenas neste teste."""

        def ler_arquivo(self, caminho: Path) -> str:
            return "<html></html>"

    leitor = LeitorFalso()

    assert leitor.ler_arquivo(caminho=Path("bookmarks.html")) == "<html></html>"


def test_escritor_port_nao_pode_ser_instanciada_diretamente() -> None:
    """Garante que a ABC não pode ser usada sem uma implementação concreta."""
    with pytest.raises(TypeError):
        EscritorPort()  # pylint: disable=abstract-class-instantiated


def test_escritor_port_aceita_implementacao_concreta() -> None:
    """Garante que uma subclasse que implementa o contrato pode ser instanciada e usada."""

    class EscritorFalso(EscritorPort):
        """Implementação fake mínima usada apenas neste teste."""

        def salvar_lote(
            self,
            caminho_original: Path,
            dados: list[dict],
            extensao: str,
            sufixo: str = "_processado",
        ) -> str:
            nome_final = f"{caminho_original.stem}{sufixo}.{extensao}"
            return str(caminho_original.with_name(nome_final))

    escritor = EscritorFalso()

    resultado = escritor.salvar_lote(
        caminho_original=Path("favoritos.html"),
        dados=[{"Titulo": "GitHub"}],
        extensao="json",
    )

    assert resultado == "favoritos_processado.json"


def test_parser_port_nao_pode_ser_instanciada_diretamente() -> None:
    """Garante que a ABC não pode ser usada sem uma implementação concreta."""
    with pytest.raises(TypeError):
        ParserPort()  # pylint: disable=abstract-class-instantiated


def test_parser_port_aceita_implementacao_concreta() -> None:
    """Garante que uma subclasse que implementa o contrato pode ser instanciada e usada."""

    class ParserFalso(ParserPort):
        """Implementação fake mínima usada apenas neste teste."""

        def extrair_favoritos(self, html_conteudo: str) -> list:
            return [{"titulo": "GitHub"}] if html_conteudo else []

    parser = ParserFalso()

    assert not parser.extrair_favoritos(html_conteudo="")
    assert parser.extrair_favoritos(html_conteudo="<html></html>") == [{"titulo": "GitHub"}]
