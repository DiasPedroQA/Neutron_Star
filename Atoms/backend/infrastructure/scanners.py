# Atoms/backend/infrastructure/scanners.py

"""Scanner de sistema de arquivos que implementa FileScanner."""

from __future__ import annotations

import logging
from pathlib import Path

from Atoms.backend.core.entidades.entidade_arquivo import ModeloArquivo
from Atoms.backend.core.entidades.entidade_diretorio import ModeloPasta
from Atoms.backend.core.interfaces.file_scanner import FileScanner

logger: logging.Logger = logging.getLogger(name=__name__)


class FileSystemScanner(FileScanner):
    """Varre diretórios e constrói a árvore de ModeloPasta/ModeloArquivo."""

    def __init__(self) -> None:
        """Inicializa o scanner de sistema de arquivos."""
        self._parser = None

    # --- Implementação da interface FileScanner ---

    def scan_directory(self, pasta_home: ModeloPasta) -> None:
        """
        Preenche recursivamente a estrutura de subpastas e arquivos a partir
        de pasta_home.
        """
        if not pasta_home.caminho_absoluto.exists():
            logger.warning("Diretório raiz não existe: %s", pasta_home.caminho_absoluto)
            return
        self._scan_recursive(pasta_atual=pasta_home)
        logger.info("Escaneamento concluído para %s", pasta_home.caminho_absoluto)

    def find_html_files(self, pasta: ModeloPasta) -> list[ModeloArquivo]:
        """
        Retorna todos os arquivos HTML (ModeloArquivo) encontrados na árvore
        a partir da pasta fornecida.
        """
        html_files: list[ModeloArquivo] = []
        self._collect_html_files(pasta=pasta, coletor=html_files)
        logger.info("Total de arquivos HTML encontrados: %d", len(html_files))
        return html_files

    # --- Métodos privados auxiliares ---

    def _scan_recursive(self, pasta_atual: ModeloPasta) -> None:
        """Percorre o diretório e adiciona subpastas e arquivos ao modelo."""
        try:
            for item in pasta_atual.caminho_absoluto.iterdir():
                if item.is_dir() and not self._deve_ignorar_diretorio(item=item):
                    sub_pasta = ModeloPasta(
                        nome_pasta=item.name,
                        caminho_absoluto=item,
                        pasta_pai=pasta_atual,
                    )
                    pasta_atual.adicionar_subpasta(sub_pasta=sub_pasta)
                    self._scan_recursive(pasta_atual=sub_pasta)
                elif item.is_file() and self._deve_processar_arquivo(item=item):
                    arquivo = ModeloArquivo(
                        nome_arquivo=item.name,
                        caminho_arquivo=item,
                        tamanho_arquivo_bytes=item.stat().st_size,
                        file_is_html=True,
                    )
                    pasta_atual.adicionar_arquivo(sub_arquivo=arquivo)
        except PermissionError:
            logger.warning("Sem permissão para acessar: %s", pasta_atual.caminho_absoluto)

    def _collect_html_files(self, pasta: ModeloPasta, coletor: list[ModeloArquivo]) -> None:
        """Recolhe recursivamente todos os ModeloArquivo HTML da árvore."""
        for arquivo in pasta.subarquivos:
            if arquivo.file_is_html or arquivo.caminho_arquivo.suffix.lower() in (
                ".html",
                ".htm",
            ):
                coletor.append(arquivo)
        for sub in pasta.subpastas:
            self._collect_html_files(pasta=sub, coletor=coletor)

    # --- Filtros (mesmos de antes) ---

    @staticmethod
    def _deve_ignorar_diretorio(item: Path) -> bool:
        """Pastas ocultas ou de sistema devem ser ignoradas."""
        return item.name.startswith(".") or item.name.lower() in {
            "system volume information",
            "$recycle.bin",
            "recycler",
            "lost+found",
        }

    @staticmethod
    def _deve_processar_arquivo(item: Path) -> bool:
        """Verifica se é HTML e se o nome contém 'bookmark' ou 'favorito'."""
        if item.suffix.lower() not in (".html", ".htm"):
            return False
        nome_lower: str = item.name.lower()
        return "bookmark" in nome_lower or "favorito" in nome_lower
