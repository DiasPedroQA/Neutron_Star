"""Testes do caso de uso de busca de arquivos (busca_arquivos.py)."""

from pathlib import Path

from aplicacao.casos_de_uso.busca_arquivos import aplicar_filtros, buscar_arquivos


class TestAplicarFiltros:
    """Composição de filtros aplicados em sequência sobre uma lista de caminhos."""

    def test_sem_filtros_retorna_lista_original(self) -> None:
        """Nenhum filtro informado deve devolver a lista intacta."""
        arquivos: list[Path] = [Path("a.html"), Path("b.html")]

        assert aplicar_filtros(arquivos=arquivos, filtros=[]) == arquivos

    def test_aplica_filtros_em_sequencia_como_and_logico(self) -> None:
        """Só devem sobrar itens que passam em TODOS os filtros (AND lógico)."""
        arquivos: list[Path] = [Path("a.html"), Path("ab.html"), Path("b.html")]

        resultado: list[Path] = aplicar_filtros(
            arquivos=arquivos,
            filtros=[lambda p: "a" in p.name, lambda p: "b" in p.name],
        )

        assert resultado == [Path("ab.html")]


class TestBuscarArquivos:
    """Busca recursiva de arquivos por extensão, chaves e data no nome."""

    def test_encontra_apenas_arquivos_com_a_extensao_pedida(self, tmp_path: Path) -> None:
        """Arquivos com outra extensão não devem entrar no resultado."""
        (tmp_path / "favoritos.html").write_text(data="x")
        (tmp_path / "notas.txt").write_text(data="x")

        resultado: list[Path] = buscar_arquivos(pasta=tmp_path)

        assert resultado == [tmp_path / "favoritos.html"]

    def test_filtra_por_chave_no_nome(self, tmp_path: Path) -> None:
        """Apenas arquivos cujo nome contém uma das chaves devem ser retornados."""
        (tmp_path / "bookmarks_trabalho.html").write_text(data="x")
        (tmp_path / "bookmarks_pessoal.html").write_text(data="x")

        resultado: list[Path] = buscar_arquivos(pasta=tmp_path)

        assert resultado == [tmp_path / "bookmarks_trabalho.html"]

    def test_ignora_arquivos_em_pastas_ocultas(self, tmp_path: Path) -> None:
        """Arquivos dentro de uma pasta cujo nome começa com '.' não devem aparecer."""
        pasta_oculta: Path = tmp_path / ".config"
        pasta_oculta.mkdir()
        (pasta_oculta / "favoritos.html").write_text(data="x")

        resultado: list[Path] = buscar_arquivos(pasta=tmp_path)

        assert not resultado

    def test_busca_recursiva_em_subpastas(self, tmp_path: Path) -> None:
        """Arquivos em subpastas (não ocultas) também devem ser encontrados."""
        subpasta: Path = tmp_path / "sub"
        subpasta.mkdir()
        (subpasta / "favoritos.html").write_text(data="x")

        resultado: list[Path] = buscar_arquivos(pasta=tmp_path)

        assert resultado == [subpasta / "favoritos.html"]
