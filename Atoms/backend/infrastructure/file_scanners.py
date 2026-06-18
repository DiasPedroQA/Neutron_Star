"""Varredor de sistema de arquivos que implementa FileScanner."""

from __future__ import annotations

import logging
from pathlib import Path

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_diretorio import ModeloPasta
from backend.core.interfaces.file_scanner import FileScanner

logger: logging.Logger = logging.getLogger(name=__name__)


class FileSystemScanner(FileScanner):
    """Varre diretórios e constrói a árvore de ModeloPasta/ModeloArquivo."""

    def varrer_diretorio(self, pasta_raiz: ModeloPasta) -> None:
        """
        Preenche recursivamente a estrutura de subpastas e arquivos a partir
        de pasta_raiz.
        """
        if not pasta_raiz.caminho_absoluto.exists():
            logger.warning("Diretório raiz não existe: %s", pasta_raiz.caminho_absoluto)
            return
        self._varrer_recursivamente(pasta_atual=pasta_raiz)
        logger.info("Varredura concluída para %s", pasta_raiz.caminho_absoluto)

    def localizar_arquivos_html(self, pasta: ModeloPasta) -> list[ModeloArquivo]:
        """
        Retorna todos os arquivos HTML (ModeloArquivo) encontrados na árvore
        a partir da pasta fornecida.
        """
        arquivos_html: list[ModeloArquivo] = []
        self._coletar_arquivos_html(pasta=pasta, coletor=arquivos_html)
        logger.info("Total de arquivos HTML encontrados: %d", len(arquivos_html))
        return arquivos_html

    def _varrer_recursivamente(self, pasta_atual: ModeloPasta) -> None:
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
                    self._varrer_recursivamente(pasta_atual=sub_pasta)
                elif item.is_file() and self._deve_processar_arquivo(item=item):
                    arquivo = ModeloArquivo(
                        nome_arquivo=item.name,
                        caminho_arquivo=item,
                        tamanho_arquivo_bytes=item.stat().st_size,
                        eh_html=True,
                    )
                    pasta_atual.adicionar_arquivo(sub_arquivo=arquivo)
        except PermissionError:
            logger.warning(
                "Sem permissão para acessar: %s", pasta_atual.caminho_absoluto
            )

    def _coletar_arquivos_html(
        self, pasta: ModeloPasta, coletor: list[ModeloArquivo]
    ) -> None:
        """Recolhe recursivamente todos os ModeloArquivo HTML da árvore."""
        for arquivo in pasta.subarquivos:
            if arquivo.eh_html or arquivo.caminho_arquivo.suffix.lower() in (
                ".html",
                ".htm",
            ):
                coletor.append(arquivo)
        for sub in pasta.subpastas:
            self._coletar_arquivos_html(pasta=sub, coletor=coletor)

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
        """Verifica se o arquivo parece uma exportação HTML de favoritos.

        Os nomes aceitos incluem termos em português e o termo `bookmark`,
        comum em exportações de navegadores.
        """
        if item.suffix.lower() not in (".html", ".htm"):
            return False
        nome_lower: str = item.name.lower()
        termos_exportacao = ("bookmark", "favorito", "bookmarks")
        return any(termo in nome_lower for termo in termos_exportacao)

    def _scan_recursive(self, pasta_atual: ModeloPasta) -> None:
        """Alias de compatibilidade para `_varrer_recursivamente`."""
        self._varrer_recursivamente(pasta_atual=pasta_atual)

    def _collect_html_files(
        self, pasta: ModeloPasta, coletor: list[ModeloArquivo]
    ) -> None:
        """Alias de compatibilidade para `_coletar_arquivos_html`."""
        self._coletar_arquivos_html(pasta=pasta, coletor=coletor)


VarredorSistemaArquivos = FileSystemScanner
