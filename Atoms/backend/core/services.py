# backend/core/services.py

"""Serviço principal que orquestra todo o processo de bookmark."""
from pathlib import Path
from typing import Any, Optional

from Atoms.backend.core.entities import ModeloArquivo, ModeloPasta
from Atoms.backend.core.interfaces import (
    BookmarkExporter,
    BookmarkParser,
    BookmarkRepository,
    FileScanner,
)


class BookmarkProcessingService:
    """SERVICE: Contém a LÓGICA de negócio do processamento de bookmarks."""

    def __init__(
        self,
        scanner: FileScanner,
        parser: BookmarkParser,
        exporter: Optional[BookmarkExporter] = None,
        repository: Optional[BookmarkRepository] = None,
    ) -> None:
        """
        Injeta as dependências (todas interfaces, não implementações).

        Args:
            scanner: Implementação de escaneamento
            parser: Implementação de parsing
            exporter: Implementação de exportação (opcional)
            repository: Implementação de repositório (opcional)
        """
        self.scanner: FileScanner = scanner
        self.parser: BookmarkParser = parser
        self.exporter: BookmarkExporter | None = exporter
        self.repository: BookmarkRepository | None = repository

    def process_directory(
        self, root_path: Path
    ) -> dict[str, list[dict[str, str]] | dict[str, int] | str]:
        """
        LÓGICA DE NEGÓCIO: processa um diretório inteiro.

        1. Escaneia estrutura de pastas
        2. Encontra arquivos HTML
        3. Extrai bookmarks de cada arquivo
        4. Retorna resultados agregados
        """
        # Cria estrutura de pasta raiz
        root_pasta = ModeloPasta(nome_pasta=root_path.name, caminho_pasta=root_path)

        # 1. Escaneia (usando o scanner injetado)
        self.scanner.scan_directory(pasta=root_pasta)

        # 2. Encontra arquivos HTML
        html_files: list[ModeloArquivo] = self.scanner.find_html_files(pasta=root_pasta)

        # 3. Processa cada arquivo
        all_bookmarks: list[dict[str, Any]] = []
        stats: dict[str, int] = {
            "total_files": len(html_files),
            "processed_files": 0,
            "failed_files": 0,
            "total_bookmarks": 0,
        }

        for html_file in html_files:
            if bookmarks := self.parser.parse_file(arquivo=html_file):
                all_bookmarks.extend(bookmarks)
                stats["processed_files"] += 1
                stats["total_bookmarks"] += len(bookmarks)
            else:
                stats["failed_files"] += 1

        return {
            "bookmarks": all_bookmarks,
            "statistics": stats,
            "root_path": str(root_path),
        }

    def export_bookmarks(
        self, bookmarks: list[dict[str, Any]], output_path: Path, format: str = "json"
    ) -> None:
        """
        REGRA DE NEGÓCIO: exporta bookmarks para o formato especificado.

        Args:
            bookmarks: Lista de bookmarks
            output_path: Caminho do arquivo de saída
            format: Formato de exportação ("json", "csv", "pdf")
        """
        if not self.exporter:
            raise ValueError("Nenhum exporter configurado")

        # REGRA: validar formato
        if format not in ["json", "csv", "pdf"]:
            raise ValueError(f"Formato não suportado: {format}")

        # Adiciona extensão se não tiver
        if not output_path.suffix:
            output_path = output_path.with_suffix(f".{format}")

        # Exporta
        self.exporter.export(bookmarks, output_path)

    def save_to_repository(self, bookmarks: list[dict[str, Any]], session_id: str) -> None:
        """Salva resultados no repositório (se configurado)."""
        if self.repository:
            self.repository.save(bookmarks=bookmarks, identifier=session_id)
