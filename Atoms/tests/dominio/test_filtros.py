"""Testes dos predicados de filtragem de caminhos (dominio/filtros.py)."""

from pathlib import Path

import pytest
from dominio.filtros import (
    caminho_nao_oculto,
    extrair_nome_do_caminho,
    no_nome_contem_chave,
)


class TestExtrairNomeDoCaminho:
    """Extração do nome do arquivo, sempre em minúsculas."""

    def test_retorna_nome_em_minusculas(self) -> None:
        """Nome deve vir em lowercase independente da caixa original."""
        assert extrair_nome_do_caminho(Path("/tmp/Bookmarks_ABC.HTML")) == "bookmarks_abc.html"


class TestCaminhoNaoOculto:
    """Detecção de partes ocultas (iniciadas por ponto) no caminho."""

    @pytest.mark.parametrize(
        argnames=("caminho", "esperado"),
        argvalues=[
            pytest.param(Path("/home/user/docs/arquivo.html"), True, id="sem_partes_ocultas"),
            pytest.param(Path("/home/user/.config/arquivo.html"), False, id="pasta_oculta"),
            pytest.param(Path("/home/user/.arquivo.html"), False, id="arquivo_oculto"),
        ],
    )
    def test_deteccao_de_ocultos(self, caminho: Path, esperado: bool) -> None:
        """Qualquer parte do caminho iniciada por '.' deve marcar como oculto."""
        assert caminho_nao_oculto(caminho=caminho) is esperado


class TestNoNomeContemChave:
    """Busca de palavras-chave no nome do arquivo, sem diferenciar caixa."""

    def test_encontra_chave_case_insensitive(self) -> None:
        """Chave em caixa diferente da usada no nome ainda deve ser encontrada."""
        assert no_nome_contem_chave(caminho=Path("Bookmarks_Trabalho.html"))

    def test_nao_encontra_quando_nenhuma_chave_bate(self) -> None:
        """Nenhuma das chaves presente no nome deve retornar False."""
        assert not no_nome_contem_chave(caminho=Path("favoritos.html"))

    def test_lista_de_chaves_vazia_nao_encontra_nada(self) -> None:
        """Sem chaves para buscar, o resultado é sempre False."""
        assert not no_nome_contem_chave(caminho=Path("qualquer.html"))
