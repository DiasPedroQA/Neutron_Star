# Atoms/backend/infrastructure/scanners.py

"""Implementação concreta do scanner de arquivos."""

from pathlib import Path
from typing import Any, Optional

from Atoms.backend.core.entities import ModeloArquivo, ModeloPasta
from Atoms.backend.infrastructure.parser import NetscapeBookmarkParser


class FileSystemScanner:
    """Scanner de sistema de arquivos que também extrai bookmarks de HTML."""

    def __init__(self, parser: Optional[NetscapeBookmarkParser] = None) -> None:
        self.parser: NetscapeBookmarkParser = parser or NetscapeBookmarkParser()

    def scan_and_process(self, root_path: Path) -> list[dict[str, Any]]:
        """
        Escaneia o diretório, monta a árvore de pastas e extrai bookmarks.

        Retorna:
            - Lista de dicionários de bookmarks encontrados.
            - ModeloPasta raiz da estrutura escaneada.
        """
        root_pasta = ModeloPasta(
            nome_pasta=root_path.name,
            caminho_pasta=root_path,
            pasta_pai=None,
        )
        bookmarks: list[dict[str, Any]] = []
        self._scan_recursive(pasta=root_pasta, bookmarks=bookmarks)
        return bookmarks

    def _scan_recursive(self, pasta: ModeloPasta, bookmarks: list[dict[str, Any]]) -> None:
        """Preenche a árvore e extrai bookmarks de arquivos HTML encontrados."""
        if not pasta.caminho_pasta.exists():
            return

        for item in pasta.caminho_pasta.iterdir():
            if item.is_dir():
                # Ignora pastas ocultas e de sistema
                if item.name.startswith(".") or item.name in {
                    "System Volume Information",
                    "$Recycle.Bin",
                }:
                    continue

                sub = ModeloPasta(
                    nome_pasta=item.name,
                    caminho_pasta=item,
                    pasta_pai=pasta,
                )
                pasta.adicionar_subpasta(sub_pasta=sub)
                self._scan_recursive(pasta=sub, bookmarks=bookmarks)

            elif item.is_file() and item.suffix.lower() in (".html", ".htm"):
                arquivo = ModeloArquivo(
                    nome_arquivo=item.name,
                    caminho_arquivo=item,
                    tamanho_arquivo_bytes=item.stat().st_size,
                    file_is_html=True,
                )
                pasta.adicionar_arquivo(sub_arquivo=arquivo)

                # Processa imediatamente o arquivo encontrado
                try:
                    parsed: list[dict[str, Any]] = self.parser.parse_file(arquivo=arquivo)
                    bookmarks.extend(parsed)
                except Exception:
                    # Opcional: logar erro, continuar com os próximos
                    continue
