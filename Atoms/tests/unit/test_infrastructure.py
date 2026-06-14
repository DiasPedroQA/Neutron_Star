# pylint: disable=redefined-outer-name

"""Testes de infraestrutura, serviços e apresentação do Neutron Star."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from _pytest.capture import CaptureResult

import Atoms.backend.infrastructure.identifier as identifier_module
from Atoms.backend.core.entidades.entidade_arquivo import ModeloArquivo
from Atoms.backend.core.entidades.entidade_bookmark import Bookmark
from Atoms.backend.core.entidades.entidade_diretorio import ModeloPasta
from Atoms.backend.core.entidades.entidade_sistema_operacional import ModeloSistemaOperacional
from Atoms.backend.core.entidades.resultado_processamento import ResultadoProcessamento
from Atoms.backend.core.interfaces.bookmark_exporter import BookmarkExporter
from Atoms.backend.core.interfaces.bookmark_parser import BookmarkParser
from Atoms.backend.core.interfaces.bookmark_repository import BookmarkRepository
from Atoms.backend.core.interfaces.file_scanner import FileScanner
from Atoms.backend.core.services import BookmarkProcessingService
from Atoms.backend.infrastructure.exporters import CSVExporter, JSONExporter, PDFExporter
from Atoms.backend.infrastructure.identifier import DetectarSistemaOperacional
from Atoms.backend.infrastructure.parser import TagsFinder
from Atoms.backend.infrastructure.scanners import FileSystemScanner
from Atoms.frontend.display import cli_exibir_arquivo, cli_exibir_bookmarks, cli_exibir_estatisticas, cli_exibir_pasta, cli_exibir_sistema_operacional


class TestFileSystemScanner:
    def test_scan_directory_builds_tree_and_finds_html(self, tmp_path: Path) -> None:
        """Verifica se o scanner constrói a árvore de diretórios e encontra arquivos HTML.

        Este teste garante que arquivos HTML na pasta raiz e em subdiretórios são detectados e retornados corretamente na lista de resultados.

        Args:
            tmp_path: Diretório temporário usado como raiz para simular a estrutura de diretórios.
        """
        root: Path = tmp_path / "home"
        root.mkdir()
        (root / "bookmarks.html").write_text("<html></html>", encoding="utf-8")
        sub: Path = root / "Downloads"
        sub.mkdir()
        (sub / "favorites.bookmarks.html").write_text("<html></html>", encoding="utf-8")
        html_files: list[ModeloArquivo] = self._prepare_and_scan_tree(
            files=[
                ("bookmarks.html", "<html></html>"),
                ("Downloads/favorites.bookmarks.html", "<html></html>"),
            ],
            root=root,
        )
        assert len(html_files) == 2
        assert {f.nome_arquivo for f in html_files} == {
            "bookmarks.html",
            "favorites.bookmarks.html",
        }

    def test_ignora_diretorios_ocultos(self, tmp_path: Path) -> None:
        """Verifica se o scanner ignora diretórios ocultos durante a varredura.

        Este teste garante que arquivos HTML dentro de pastas iniciadas com ponto não são considerados nos resultados da busca.

        Args:
            tmp_path: Diretório temporário usado como raiz para criar a estrutura com diretório oculto.
        """
        root: Path = tmp_path / "home"
        root.mkdir()
        oculto: Path = root / ".secret"
        oculto.mkdir()
        html_files: list[ModeloArquivo] = self._prepare_and_scan_tree(files=[(".secret/bookmarks.html", "<html></html>")], root=root)
        assert not html_files

    def test_should_ignore_non_bookmark_html_and_non_html_files(self, tmp_path: Path) -> None:
        root: Path = tmp_path / "home"
        root.mkdir()
        html_files: list[ModeloArquivo] = self._prepare_and_scan_tree(
            files=[
                ("about.html", "<html></html>"),
                ("favorites.html", "<html></html>"),
                ("bookmark_list.htm", "<html></html>"),
                ("notes.txt", "ignore"),
                ("favorito.html", "<html></html>"),
            ],
            root=root,
        )

        assert {f.nome_arquivo for f in html_files} == {
            "bookmark_list.htm",
            "favorito.html",
        }

    def test_scan_directory_returns_empty_when_root_missing(self, tmp_path: Path) -> None:
        root: Path = tmp_path / "home"
        pasta = ModeloPasta(nome_pasta="home", caminho_absoluto=root)
        scanner = FileSystemScanner()

        scanner.scan_directory(pasta_home=pasta)

        assert scanner.find_html_files(pasta=pasta) == []

    def test_internal_filters_handle_hidden_directories_and_html_names(self) -> None:
        assert FileSystemScanner._deve_ignorar_diretorio(Path("/tmp/.secret"))
        assert FileSystemScanner._deve_ignorar_diretorio(Path("/tmp/System Volume Information"))
        assert not FileSystemScanner._deve_ignorar_diretorio(Path("/tmp/bookmarks"))
        assert FileSystemScanner._deve_processar_arquivo(Path("/tmp/bookmarks.html"))
        assert FileSystemScanner._deve_processar_arquivo(Path("/tmp/favorito.htm"))
        assert not FileSystemScanner._deve_processar_arquivo(Path("/tmp/readme.txt"))
        assert not FileSystemScanner._deve_processar_arquivo(Path("/tmp/notes.html"))

    def _prepare_and_scan_tree(self, files: list[tuple[str, str]], root: Path) -> list[ModeloArquivo]:
        for relative_path, content in files:
            file_path = root / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")

        pasta = ModeloPasta(nome_pasta="home", caminho_absoluto=root)
        scanner = FileSystemScanner()
        scanner.scan_directory(pasta_home=pasta)
        return scanner.find_html_files(pasta=pasta)


class TestExporters:
    """Testes para os exportadores de bookmarks em diferentes formatos.

    Esta classe verifica se os exportadores geram arquivos válidos e lidam corretamente com casos especiais como listas vazias.
    """

    def test_json_exporter_writes_json(self, tmp_path: Path) -> None:
        """Verifica se o exportador JSON grava um arquivo JSON válido.

        Este teste garante que os dados persistidos podem ser carregados como JSON e preservam os campos principais do bookmark.

        Args:
            tmp_path: Diretório temporário usado como destino para o arquivo JSON exportado.
        """
        bookmarks: list[Bookmark] = [
            Bookmark(
                title="Example",
                url="https://example.com",
                add_date=datetime(year=2023, month=1, day=1, tzinfo=timezone.utc),
            )
        ]
        saida: Path = tmp_path / "out.json"

        JSONExporter().export(bookmarks=bookmarks, saida=saida)

        assert saida.exists()
        data = json.loads(saida.read_text(encoding="utf-8"))
        assert data[0]["url"] == "https://example.com"

    def test_csv_exporter_writes_csv(self, tmp_path: Path) -> None:
        """Verifica se o exportador CSV grava um arquivo CSV válido.

        Este teste garante que o arquivo gerado contém as colunas esperadas e preserva os dados dos bookmarks.

        Args:
            tmp_path: Diretório temporário usado como destino para o arquivo CSV exportado.
        """
        bookmarks: list[Bookmark] = [
            Bookmark(
                title="Example",
                url="https://example.com",
                add_date=datetime(year=2023, month=1, day=1, tzinfo=timezone.utc),
            )
        ]
        saida: Path = tmp_path / "out.csv"

        CSVExporter().export(bookmarks=bookmarks, saida=saida)

        assert saida.exists()
        with saida.open(encoding="utf-8", newline="") as f:
            reader: csv.DictReader[str] = csv.DictReader(f)
            rows = list(reader)

        assert rows[0]["title"] == "Example"

    def test_csv_exporter_ignora_lista_vazia(self, tmp_path: Path) -> None:
        """Verifica se o exportador CSV não cria arquivos quando a lista está vazia.

        Este teste garante que nenhuma saída é gerada em disco quando não há bookmarks para exportar.

        Args:
            tmp_path: Diretório temporário usado como destino potencial para o arquivo CSV.
        """
        saida: Path = tmp_path / "out.csv"

        CSVExporter().export(bookmarks=[], saida=saida)

        assert not saida.exists()

    def test_json_exporter_writes_empty_array(self, tmp_path: Path) -> None:
        saida: Path = tmp_path / "out.json"

        JSONExporter().export(bookmarks=[], saida=saida)

        assert saida.exists()
        assert json.loads(saida.read_text(encoding="utf-8")) == []

    def test_pdf_exporter_builds_file(self, tmp_path: Path) -> None:
        """Verifica se o exportador PDF gera um arquivo PDF não vazio.

        Este teste garante que, dado ao menos um bookmark, o arquivo PDF é criado no disco com algum conteúdo gravado.

        Args:
            tmp_path: Diretório temporário usado como destino para o arquivo PDF exportado.
        """
        pytest.importorskip("reportlab")

        bookmarks: list[Bookmark] = [
            Bookmark(
                title="Example",
                url="https://example.com",
                add_date=datetime(year=2023, month=1, day=1, tzinfo=timezone.utc),
            )
        ]
        saida: Path = tmp_path / "out.pdf"

        PDFExporter().export(bookmarks=bookmarks, saida=saida)

        assert saida.exists()
        assert saida.stat().st_size > 0


class TestBookmarkProcessingService:
    class DummyScanner(FileScanner):
        """Mock de FileScanner para os testes de serviço."""

        def scan_directory(self, pasta_home: ModeloPasta) -> None:
            self.scanned: ModeloPasta = pasta_home

        def find_html_files(self, pasta: ModeloPasta) -> list[ModeloArquivo]:
            return [
                ModeloArquivo(
                    nome_arquivo="bookmarks.html",
                    caminho_arquivo=pasta.caminho_absoluto / "bookmarks.html",
                    tamanho_arquivo_bytes=0,
                    file_is_html=True,
                )
            ]

    class DummyParser(BookmarkParser):
        """Mock de BookmarkParser para os testes de serviço."""

        def supports_file(self, arquivo: ModeloArquivo) -> bool:
            return True

        def parse_file(self, arquivo: ModeloArquivo) -> list[Bookmark]:
            return [
                Bookmark(
                    title="Example",
                    url="https://example.com",
                    add_date=datetime(year=2023, month=1, day=1, tzinfo=timezone.utc),
                )
            ]

    class DummyParserWithoutResults(BookmarkParser):
        """Mock de BookmarkParser que falha ao parsear bookmarks."""

        def supports_file(self, arquivo: ModeloArquivo) -> bool:
            return True

        def parse_file(self, arquivo: ModeloArquivo) -> list[Bookmark]:
            return []

    class DummyParserUnsupported(BookmarkParser):
        """Mock de BookmarkParser que não suporta o arquivo."""

        def supports_file(self, arquivo: ModeloArquivo) -> bool:
            return False

        def parse_file(self, arquivo: ModeloArquivo) -> list[Bookmark]:
            return []

    class DummyExporter(BookmarkExporter):
        """Mock de BookmarkExporter para os testes de serviço."""

        def get_supported_formats(self) -> list[str]:
            return ["json"]

        def export(self, bookmarks: list[Bookmark], saida: Path) -> None:
            saida.write_text("ok", encoding="utf-8")

    class DummyRepository(BookmarkRepository):
        """Mock de BookmarkRepository para os testes de serviço."""

        def __init__(self) -> None:
            self.saved: tuple[list[Bookmark], str] | None = None

        def save(self, bookmarks: list[Bookmark], identifier: str) -> None:
            self.saved = (bookmarks, identifier)

        def load(self, identifier: str) -> list[Bookmark]:
            return []

    def test_process_directory_collects_bookmarks_and_stats(self, tmp_path: Path) -> None:
        """Verifica se o serviço processa o diretório e coleta estatísticas de bookmarks.

        Este teste garante que arquivos HTML são encontrados, processados e que as estatísticas retornadas refletem o resultado do processamento.

        Args:
            tmp_path: Diretório temporário usado como raiz para simular o diretório home.
        """
        root: Path = tmp_path / "home"
        root.mkdir()
        service = BookmarkProcessingService(
            scanner=self.DummyScanner(),
            parser=self.DummyParser(),
            exporter=None,
            repository=None,
        )

        result: ResultadoProcessamento = service.process_directory(root_path=root)

        assert result.statistics.total_files == 1
        assert result.statistics.processed_files == 1
        assert result.statistics.failed_files == 0
        assert result.statistics.total_bookmarks == 1
        assert result.root_path == str(root)

    def test_process_directory_skips_files_with_no_bookmarks(self, tmp_path: Path) -> None:
        root: Path = tmp_path / "home"
        root.mkdir()
        service = BookmarkProcessingService(
            scanner=self.DummyScanner(),
            parser=self.DummyParserWithoutResults(),
            exporter=None,
            repository=None,
        )

        result: ResultadoProcessamento = service.process_directory(root_path=root)

        assert result.statistics.total_files == 1
        assert result.statistics.processed_files == 0
        assert result.statistics.failed_files == 1
        assert result.statistics.total_bookmarks == 0

    def test_process_directory_skips_unsupported_files(self, tmp_path: Path) -> None:
        root: Path = tmp_path / "home"
        root.mkdir()
        service = BookmarkProcessingService(
            scanner=self.DummyScanner(),
            parser=self.DummyParserUnsupported(),
            exporter=None,
            repository=None,
        )

        result: ResultadoProcessamento = service.process_directory(root_path=root)

        assert result.statistics.total_files == 1
        assert result.statistics.processed_files == 0
        assert result.statistics.failed_files == 1
        assert result.statistics.total_bookmarks == 0

    def test_save_to_repository_ignores_missing_repository(self) -> None:
        service = BookmarkProcessingService(
            scanner=self.DummyScanner(),
            parser=self.DummyParser(),
        )
        bookmarks: list[Bookmark] = [
            Bookmark(
                title="Example",
                url="https://example.com",
                add_date=datetime(year=2023, month=1, day=1, tzinfo=timezone.utc),
            )
        ]

        service.save_to_repository(bookmarks=bookmarks, session_id="test-id")

    def test_export_bookmarks_adds_suffix_and_uses_exporter(self, tmp_path: Path) -> None:
        """Verifica se a exportação adiciona o sufixo correto ao caminho de saída.

        Este teste garante que o serviço usa o exporter configurado e grava o arquivo no formato esperado.

        Args:
            tmp_path: Diretório temporário usado como base para o arquivo de saída.
        """
        exporter = self.DummyExporter()
        service = BookmarkProcessingService(
            scanner=self.DummyScanner(),
            parser=self.DummyParser(),
            exporter=exporter,
        )
        bookmarks: list[Bookmark] = [
            Bookmark(
                title="Example",
                url="https://example.com",
                add_date=datetime(year=2023, month=1, day=1, tzinfo=timezone.utc),
            )
        ]
        saida: Path = tmp_path / "out"

        service.export_bookmarks(bookmarks=bookmarks, output_path=saida, formato="json")

        assert saida.with_suffix(suffix=".json").exists()

    def test_export_bookmarks_raises_without_exporter(self) -> None:
        """Garante que o serviço exige um exporter configurado para exportar bookmarks.

        Este teste verifica se uma exceção é lançada quando se tenta exportar sem fornecer um exporter ao serviço.

        """
        service = BookmarkProcessingService(
            scanner=self.DummyScanner(),
            parser=self.DummyParser(),
        )

        with pytest.raises(ValueError, match="Nenhum exporter"):
            service.export_bookmarks(bookmarks=[], output_path=Path("out.json"), formato="json")

    def test_export_bookmarks_raises_invalid_format(self, tmp_path: Path) -> None:
        """Garante que o serviço rejeita formatos de exportação não suportados.

        Este teste verifica se uma exceção apropriada é lançada ao solicitar exportação em um formato inválido.

        Args:
            tmp_path: Diretório temporário usado como destino de saída para o arquivo de teste.
        """
        exporter = self.DummyExporter()
        service = BookmarkProcessingService(
            scanner=self.DummyScanner(),
            parser=self.DummyParser(),
            exporter=exporter,
        )

        with pytest.raises(ValueError, match="não suportado"):
            service.export_bookmarks(bookmarks=[], output_path=tmp_path / "out.txt", formato="csv")

    def test_save_to_repository_calls_repo(self) -> None:
        """Verifica se o serviço delega corretamente a persistência ao repositório.

        Este teste garante que os bookmarks e o identificador de sessão são encaminhados ao repositório sem alterações.

        """
        repo = self.DummyRepository()
        service = BookmarkProcessingService(
            scanner=self.DummyScanner(),
            parser=self.DummyParser(),
            repository=repo,
        )
        bookmarks: list[Bookmark] = [
            Bookmark(
                title="Example",
                url="https://example.com",
                add_date=datetime(year=2023, month=1, day=1, tzinfo=timezone.utc),
            )
        ]

        service.save_to_repository(bookmarks=bookmarks, session_id="test-id")

        assert repo.saved is not None
        assert repo.saved[1] == "test-id"


class TestTagsFinder:
    """Testes para o parser de bookmarks baseado em tags HTML.

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

        assert modelo.user_home == tmp_path
        assert modelo.nome_sistema == "linux"

    def test_supports_html_by_flag_and_extension(self, tmp_path: Path) -> None:
        """Verifica se o parser suporta arquivos HTML tanto pela flag quanto pela extensão.

        Este teste garante que arquivos marcados como HTML ou com extensão .html sejam considerados válidos para parsing.

        Args:
            tmp_path: Diretório temporário usado para criar os arquivos de teste.
        """
        arquivo_html = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=tmp_path / "bookmarks.html",
            tamanho_arquivo_bytes=0,
            file_is_html=True,
        )
        arquivo_txt = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=tmp_path / "bookmarks.html",
            tamanho_arquivo_bytes=0,
            file_is_html=False,
        )

        parser = TagsFinder()

        assert parser.supports_file(arquivo=arquivo_html)
        assert parser.supports_file(arquivo=arquivo_txt)

    def test_parse_file_returns_bookmarks_for_valid_html(self, tmp_path: Path) -> None:
        """Verifica se o parser retorna bookmarks válidos a partir de um HTML bem formado.

        Este teste garante que apenas links suportados são convertidos em bookmarks e que seus campos principais são preenchidos corretamente.

        Args:
            tmp_path: Diretório temporário usado para criar o arquivo HTML de teste.
        """
        caminho: Path = tmp_path / "bookmarks.html"
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
            nome_arquivo="bookmarks.html",
            caminho_arquivo=caminho,
            tamanho_arquivo_bytes=0,
            file_is_html=True,
        )
        parser = TagsFinder()

        bookmarks: list[Bookmark] = parser.parse_file(arquivo=arquivo)

        assert len(bookmarks) == 1
        assert bookmarks[0].title == "Example"
        assert bookmarks[0].url == "https://example.com"
        assert bookmarks[0].add_date == datetime(year=2023, month=1, day=1, tzinfo=timezone.utc)

    def test_parse_file_returns_empty_for_missing_file(self, tmp_path: Path) -> None:
        """Verifica se o parser retorna uma lista vazia quando o arquivo não existe.

        Este teste garante que a ausência do arquivo é tratada de forma silenciosa, sem lançar exceções e sem retornar bookmarks.

        Args:
            tmp_path: Diretório temporário usado para construir o caminho de um arquivo inexistente.
        """
        arquivo = ModeloArquivo(
            nome_arquivo="missing.html",
            caminho_arquivo=tmp_path / "missing.html",
            tamanho_arquivo_bytes=0,
            file_is_html=True,
        )
        parser = TagsFinder()

        assert parser.parse_file(arquivo=arquivo) == []

    def test_parse_file_returns_empty_on_read_error(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        caminho: Path = tmp_path / "bookmarks.html"
        caminho.write_text("<html></html>", encoding="utf-8")

        monkeypatch.setattr(
            Path,
            "read_text",
            lambda self, **kwargs: (_ for _ in ()).throw(OSError("boom")),
        )

        arquivo = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=caminho,
            tamanho_arquivo_bytes=0,
            file_is_html=True,
        )
        parser = TagsFinder()

        assert parser.parse_file(arquivo=arquivo) == []

    def test_convert_timestamp_returns_epoch_when_invalid(self) -> None:
        """Verifica se timestamps inválidos são convertidos para a época padrão.

        Este teste garante que entradas não numéricas resultem em uma data de fallback consistente em vez de erro.

        """
        parser = TagsFinder()

        timestamp: datetime = parser._convert_timestamp(timestamp_str="nota-numero")

        assert timestamp == datetime(year=1970, month=1, day=1, tzinfo=timezone.utc)


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
        so = ModeloSistemaOperacional(
            nome_sistema="linux",
            versao_sistema="5.15.0",
            user_home=tmp_path,
        )
        cli_exibir_sistema_operacional(so=so)
        cli_exibir_estatisticas(stats={"bookmarks": 2})
        cli_exibir_bookmarks(
            bookmarks=[
                Bookmark(
                    title="A",
                    url="https://a",
                    add_date=datetime(year=1970, month=1, day=1, tzinfo=timezone.utc),
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
            nome_arquivo="bookmarks.html",
            caminho_arquivo=str(tmp_path / "bookmarks.html"),
            tamanho_arquivo=123,
            is_html=True,
        )

        captured: CaptureResult[str] = capsys.readouterr()

        assert "Sistema:" in captured.out
        assert "bookmarks: 2" in captured.out
        assert "https://a" in captured.out
        assert "Pasta" in captured.out
        assert "bookmarks.html" in captured.out

    def test_cli_exibir_bookmarks_prints_message_when_no_bookmarks(self, capsys: pytest.CaptureFixture[str]) -> None:
        cli_exibir_bookmarks(bookmarks=[])
        captured: CaptureResult[str] = capsys.readouterr()

        assert "Nenhum bookmark encontrado." in captured.out

    def test_cli_exibir_pasta_respects_custom_title(self, capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
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
