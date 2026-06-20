# Atoms/tests/back/unit/core/test_entidade_arquivo.py

"""Testes para a entidade ModeloArquivo."""

import pytest
from pathlib import Path
from backend.core.entidades.entidade_arquivo import ModeloArquivo


class TestModeloArquivo:
    def test_criacao_valida(self) -> None:
        """Criação com atributos corretos."""
        arq = ModeloArquivo(
            nome_arquivo="teste.html",
            caminho_arquivo=Path("/absoluto/teste.html"),
            tamanho_arquivo_bytes=1024,
            eh_html=True,
        )
        assert arq.nome_arquivo == "teste.html"
        assert arq.caminho_arquivo == Path("/absoluto/teste.html")
        assert arq.tamanho_arquivo_bytes == 1024
        assert arq.eh_html is True

    def test_criacao_com_flag_html_falsa_mas_extensao_html(self) -> None:
        """Se a extensão for .html, eh_html é forçado para True."""
        arq = ModeloArquivo(
            nome_arquivo="favoritos.html",
            caminho_arquivo=Path("/tmp/favoritos.html"),
            eh_html=False,
        )
        assert arq.eh_html is True

    def test_criacao_com_htm(self) -> None:
        """Extensão .htm também força eh_html=True."""
        arq = ModeloArquivo(
            nome_arquivo="favoritos.htm",
            caminho_arquivo=Path("/tmp/favoritos.htm"),
            eh_html=False,
        )
        assert arq.eh_html is True

    def test_nome_vazio_levanta_valueerror(self) -> None:
        with pytest.raises(
            expected_exception=ValueError,
            match="nome_arquivo deve ser uma string não vazia",
        ):
            ModeloArquivo(nome_arquivo="", caminho_arquivo=Path("/tmp/teste.txt"))

    def test_caminho_nao_absoluto_levanta_valueerror(self) -> None:
        with pytest.raises(
            expected_exception=ValueError, match="Caminho deve ser absoluto"
        ):
            ModeloArquivo(nome_arquivo="teste.txt", caminho_arquivo=Path("teste.txt"))

    def test_tamanho_negativo_levanta_valueerror(self) -> None:
        with pytest.raises(
            expected_exception=ValueError, match="não pode ser negativo"
        ):
            ModeloArquivo(
                nome_arquivo="teste.txt",
                caminho_arquivo=Path("/tmp/teste.txt"),
                tamanho_arquivo_bytes=-1,
            )

    def test_nome_diferente_do_caminho_levanta_valueerror(self) -> None:
        with pytest.raises(
            expected_exception=ValueError,
            match="nome_arquivo deve ser igual ao nome final",
        ):
            ModeloArquivo(
                nome_arquivo="diferente.txt",
                caminho_arquivo=Path("/tmp/teste.txt"),
            )

    def test_alias_file_is_html(self) -> None:
        arq = ModeloArquivo(
            nome_arquivo="x.txt",
            caminho_arquivo=Path("/tmp/x.txt"),
        )
        assert arq.file_is_html == arq.eh_html
        arq.file_is_html = True
        assert arq.eh_html is True
