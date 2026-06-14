# Atoms/backend/core/services.py

"""Serviço principal que orquestra todo o processo de bookmark."""

from __future__ import annotations

from pathlib import Path

from Atoms.backend.core.entidades.entidade_arquivo import ModeloArquivo
from Atoms.backend.core.entidades.entidade_bookmark import Bookmark
from Atoms.backend.core.entidades.entidade_diretorio import ModeloPasta
from Atoms.backend.core.entidades.resultado_processamento import EstatisticasProcessamento, ResultadoProcessamento
from Atoms.backend.core.interfaces.bookmark_exporter import BookmarkExporter
from Atoms.backend.core.interfaces.bookmark_parser import BookmarkParser
from Atoms.backend.core.interfaces.bookmark_repository import BookmarkRepository
from Atoms.backend.core.interfaces.file_scanner import FileScanner


class BookmarkProcessingService:
    """SERVICE: Contém a lógica de negócio para processar bookmarks."""

    def __init__(
        self,
        scanner: FileScanner,
        parser: BookmarkParser,
        exporter: BookmarkExporter | None = None,
        repository: BookmarkRepository | None = None,
    ) -> None:
        """Injeta dependências de infraestrutura via abstrações.

        Args:
            scanner: Implementação de FileScanner.
            parser: Implementação de BookmarkParser.
            exporter: Implementação de BookmarkExporter (opcional).
            repository: Implementação de BookmarkRepository (opcional).
        """
        self.scanner: FileScanner = scanner
        self.parser: BookmarkParser = parser
        self.exporter: BookmarkExporter | None = exporter
        self.repository: BookmarkRepository | None = repository

    def process_directory(self, root_path: Path) -> ResultadoProcessamento:
        """Processa um diretório e retorna bookmarks encontrados e estatísticas.

        :param root_path: Caminho absoluto do diretório a ser processado.
        :return: Objeto de resultado de processamento com bookmarks e estatísticas.
        """
        root_pasta = ModeloPasta(nome_pasta=root_path.name, caminho_absoluto=root_path)

        self.scanner.scan_directory(pasta_home=root_pasta)
        html_files: list[ModeloArquivo] = self.scanner.find_html_files(pasta=root_pasta)

        all_bookmarks: list[Bookmark] = []
        stats = EstatisticasProcessamento(
            total_files=len(html_files),
            processed_files=0,
            failed_files=0,
            total_bookmarks=0,
        )

        for html_file in html_files:
            if not self.parser.supports_file(arquivo=html_file):
                stats.failed_files += 1
                continue
            if bookmarks := self.parser.parse_file(arquivo=html_file):
                all_bookmarks.extend(bookmarks)
                stats.processed_files += 1
                stats.total_bookmarks += len(bookmarks)
            else:
                stats.failed_files += 1

        return ResultadoProcessamento(
            bookmarks=all_bookmarks,
            statistics=stats,
            root_path=str(root_path),
        )

    def export_bookmarks(self, bookmarks: list[Bookmark], output_path: Path, formato: str = "json") -> None:
        """Exporta bookmarks usando o exporter configurado.

        Args:
            bookmarks: Lista de bookmarks a exportar.
            output_path: Caminho do arquivo de saída.
            formato: Extensão de saída do arquivo.

        Raises:
            ValueError: Quando nenhum exporter está configurado ou o formato não é suportado.
        """
        if not self.exporter:
            raise ValueError("Nenhum exporter configurado")

        formatos_validos: list[str] = self.exporter.get_supported_formats()
        if formato not in formatos_validos:
            raise ValueError(f"Formato '{formato}' não suportado. Use: {formatos_validos}")

        if not output_path.suffix:
            output_path = output_path.with_suffix(f".{formato}")

        self.exporter.export(bookmarks=bookmarks, saida=output_path)

    def save_to_repository(self, bookmarks: list[Bookmark], session_id: str) -> None:
        """Salva bookmarks no repositório, quando presente.

        Args:
            bookmarks: Lista de bookmarks a persistir.
            session_id: Identificador da sessão usada como chave.
        """
        if self.repository:
            self.repository.save(bookmarks=bookmarks, identifier=session_id)
