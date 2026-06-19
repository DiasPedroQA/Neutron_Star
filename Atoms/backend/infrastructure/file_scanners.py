"""Varredor de sistema de arquivos que implementa FileScanner."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_diretorio import ModeloPasta
from backend.core.interfaces.file_scanner import FileScanner

logger: logging.Logger = logging.getLogger(__name__)

# Padrão compilado uma única vez (performance)
_PADRAO_NOME_ARQUIVO: re.Pattern[str] = re.compile(
    pattern=r"^(bookmarks?|favoritos?)_(\d{2})_(\d{2})_(\d{4})\.html?$",
    flags=re.IGNORECASE,
)


class VarredorSistemaArquivos(FileScanner):
    """Varre diretórios e constrói a árvore de ModeloPasta/ModeloArquivo."""

    def varrer_diretorio(self, pasta_raiz: ModeloPasta) -> None:
        """Preenche recursivamente a estrutura a partir de pasta_raiz."""
        if not pasta_raiz.caminho_absoluto.exists():
            logger.warning(
                msg=f"Diretório raiz não existe: {pasta_raiz.caminho_absoluto}"
            )
            return
        self._varrer_recursivamente(pasta=pasta_raiz)
        logger.info(msg="Varredura concluída para {pasta_raiz.caminho_absoluto}")

    def localizar_arquivos_html(self, pasta: ModeloPasta) -> list[ModeloArquivo]:
        """Retorna todos os arquivos HTML da árvore."""
        arquivos_html: list[ModeloArquivo] = []
        self._coletar_arquivos_html(pasta=pasta, coletor=arquivos_html)
        logger.info(msg=f"Total de arquivos HTML encontrados: {len(arquivos_html)}")
        return arquivos_html

    # ── métodos privados ──────────────────────────────────────────

    def _varrer_recursivamente(self, pasta: ModeloPasta) -> None:
        """Percorre o diretório e adiciona subpastas e arquivos ao modelo."""
        try:
            for item in pasta.caminho_absoluto.iterdir():
                if item.is_dir() and not self._deve_ignorar_diretorio(diretorio=item):
                    logger.info(msg=f"Sub pasta encontrada: {item.name}")
                    sub_pasta = ModeloPasta(
                        nome_pasta=item.name,
                        caminho_absoluto=item,
                        pasta_pai=pasta,
                    )
                    pasta.adicionar_subpasta(nova_sub_pasta=sub_pasta)
                    self._varrer_recursivamente(pasta=sub_pasta)
                elif item.is_file() and self._deve_processar_arquivo(arquivo=item):
                    logger.info(msg=f"Sub arquivo encontrado: {item.name}")
                    arquivo = ModeloArquivo(
                        nome_arquivo=item.name,
                        caminho_arquivo=item,
                        tamanho_arquivo_bytes=item.stat().st_size,
                        eh_html=True,
                    )
                    pasta.adicionar_arquivo(sub_arquivo=arquivo)
        except PermissionError:
            logger.warning(msg=f"Sem permissão para acessar: {pasta.caminho_absoluto}")

    def _coletar_arquivos_html(
        self, pasta: ModeloPasta, coletor: list[ModeloArquivo]
    ) -> None:
        """Recolhe recursivamente os ModeloArquivo HTML da árvore."""
        coletor.extend(arquivo for arquivo in pasta.subarquivos if arquivo.eh_html)
        for sub in pasta.subpastas:
            self._coletar_arquivos_html(pasta=sub, coletor=coletor)

    @staticmethod
    def _deve_ignorar_diretorio(diretorio: Path) -> bool:
        """Pastas ocultas ou de sistema devem ser ignoradas."""
        return diretorio.name.startswith(".") or diretorio.name.lower() in {
            "system volume information",
            "$recycle.bin",
            "recycler",
            "lost+found",
        }

    @staticmethod
    def _deve_processar_arquivo(arquivo: Path) -> bool:
        """Valida se o arquivo segue o padrão de exportação HTML de favoritos.

        Formato esperado (case‑insensitive):
            <palavra>_<dd>_<mm>_<aaaa>.html
        onde <palavra> pode ser:
            bookmark, bookmarks, favorito, favoritos.

        Exemplos válidos:
            bookmarks_25_12_2023.html
            favorito_01_01_2024.html
            bookmark_25_12_2025.html
            favoritos_01_01_2026.html
        """
        # Verifica primeiro a extensão (mais barato)
        if arquivo.suffix.lower() not in (".html", ".htm"):
            return False

        # Aplica a regex sobre o nome completo (stem + extensão)
        return bool(_PADRAO_NOME_ARQUIVO.fullmatch(arquivo.name))

    # ── aliases de compatibilidade ────────────────────────────────

    def _scan_recursive(self, pasta_atual: ModeloPasta) -> None:
        """Alias para _varrer_recursivamente."""
        self._varrer_recursivamente(pasta=pasta_atual)

    def _collect_html_files(
        self, pasta: ModeloPasta, coletor: list[ModeloArquivo]
    ) -> None:
        """Alias para _coletar_arquivos_html."""
        self._coletar_arquivos_html(pasta=pasta, coletor=coletor)
