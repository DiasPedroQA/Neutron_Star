"""Testes do ponto de entrada da CLI (main.py)."""

from argparse import Namespace
from pathlib import Path

from aplicacao.tipos import ParametrosBusca
from main import construir_parser, main, montar_contexto
from pytest import CaptureFixture

_HTML_VALIDO = """
<DL><p>
    <DT><A HREF="https://a.com">Site A</A>
</DL><p>
"""


class TestConstruirParser:
    """Configuração e valores padrão do parser de linha de comando."""

    def test_valores_padrao_quando_nenhum_argumento_informado(self) -> None:
        """Sem argumentos, os padrões documentados devem ser aplicados."""
        args: Namespace = construir_parser().parse_args(args=[])

        assert args.extensao == ".html"
        assert args.chaves == ["favoritos", "bookmarks"]
        assert args.formatos == [".json", ".csv"]
        assert args.lote is False

    def test_lote_pode_ser_ativado_por_flag(self) -> None:
        """A flag --lote deve ativar o modo de processamento em lote."""
        args: Namespace = construir_parser().parse_args(["--lote"])

        assert args.lote is True


class TestMontarContexto:
    """Conversão dos argumentos da CLI em ParametrosBusca."""

    def test_contexto_reflete_os_argumentos_informados(self, tmp_path: Path) -> None:
        """Cada argumento informado deve aparecer com o mesmo valor no contexto."""
        args: Namespace = construir_parser().parse_args(
            args=["--diretorio", str(tmp_path), "--chaves", "trabalho", "--formatos", ".md"]
        )

        contexto: ParametrosBusca = montar_contexto(args=args)

        assert contexto.get("diretorio") == tmp_path
        assert contexto.get("chaves") == ["trabalho"]
        assert contexto.get("formatos_exportacao") == [".md"]


class TestMainModoPadrao:
    """Execução do pipeline completo (buscar -> selecionar -> extrair -> exportar)."""

    def test_processa_arquivo_unico_encontrado(self, tmp_path: Path) -> None:
        """Com um arquivo válido no diretório, o pipeline deve gerar a exportação."""
        (tmp_path / "bookmarks_favoritos.html").write_text(data=_HTML_VALIDO, encoding="utf-8")
        saida: Path = tmp_path / "saida"

        main(
            argv=[
                "--diretorio",
                str(tmp_path),
                "--chaves",
                "favoritos",
                "--formatos",
                ".json",
                "--saida",
                str(saida),
            ]
        )

        assert (saida / "bookmarks.json").exists()


class TestMainModoLote:
    """Execução do modo --lote (processa todos os arquivos encontrados)."""

    def test_processa_todos_os_arquivos_encontrados(self, tmp_path: Path) -> None:
        """Múltiplos arquivos encontrados devem virar múltiplas exportações no lote."""
        (tmp_path / "bookmarks_a.html").write_text(data=_HTML_VALIDO, encoding="utf-8")
        (tmp_path / "bookmarks_b.html").write_text(data=_HTML_VALIDO, encoding="utf-8")
        saida: Path = tmp_path / "saida"

        main(
            argv=[
                "--diretorio",
                str(tmp_path),
                "--chaves",
                "bookmarks",
                "--formatos",
                ".json",
                "--saida",
                str(saida),
                "--lote",
            ]
        )

        assert (saida / "bookmarks_a.json").exists()
        assert (saida / "bookmarks_b.json").exists()

    def test_nenhum_arquivo_encontrado_nao_quebra(self, tmp_path: Path, capsys: CaptureFixture[str]) -> None:
        """Sem arquivos encontrados, deve avisar e retornar, sem lançar exceção."""
        main(argv=["--diretorio", str(tmp_path), "--chaves", "inexistente", "--lote"])

        assert "Nenhum arquivo encontrado" in capsys.readouterr().out
