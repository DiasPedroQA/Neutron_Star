# Atoms/backend/infrastructure/controllers/file_scanners.py

"""Varredor de sistema de arquivos que implementa FileScanner."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_diretorio import ModeloPasta
from backend.core.interfaces.file_scanner import FileScanner

logger: logging.Logger = logging.getLogger(name=__name__)

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
            logger.warning("Diretório raiz não existe: %s", pasta_raiz.caminho_absoluto)
            return
        logger.info("Iniciando varredura em %s", pasta_raiz.caminho_absoluto)
        self._varrer_recursivamente(pasta=pasta_raiz)
        logger.info("Varredura concluída para %s", pasta_raiz.caminho_absoluto)

    def localizar_arquivos_html(self, pasta: ModeloPasta) -> list[ModeloArquivo]:
        """Retorna todos os arquivos HTML da árvore."""
        arquivos_html: list[ModeloArquivo] = []
        self._coletar_arquivos_html(pasta=pasta, coletor=arquivos_html)
        logger.info("Total de arquivos HTML encontrados: %d", len(arquivos_html))
        return arquivos_html

    # ── métodos privados ──────────────────────────────────────────

    def _varrer_recursivamente(self, pasta: ModeloPasta) -> None:
        """Percorre o diretório e adiciona subpastas e arquivos ao modelo."""
        logger.debug("Vasculhando diretório: %s", pasta.caminho_absoluto)
        try:
            itens = list(pasta.caminho_absoluto.iterdir())
            logger.debug(
                "Encontrados %d itens em %s", len(itens), pasta.caminho_absoluto
            )
            for item in itens:
                if item.is_dir():
                    if self._deve_ignorar_diretorio(diretorio=item):
                        logger.debug("Diretório ignorado: %s", item)
                        continue
                    logger.debug("Processando subpasta: %s", item)
                    sub_pasta = ModeloPasta(
                        nome_pasta=item.name,
                        caminho_absoluto=item,
                        pasta_pai=pasta,
                    )
                    pasta.adicionar_subpasta(nova_sub_pasta=sub_pasta)
                    self._varrer_recursivamente(pasta=sub_pasta)
                elif item.is_file():
                    if self._deve_processar_arquivo(arquivo=item):
                        logger.debug("Arquivo HTML aceito: %s", item)
                        arquivo = ModeloArquivo(
                            nome_arquivo=item.name,
                            caminho_arquivo=item,
                            tamanho_arquivo_bytes=item.stat().st_size,
                            eh_html=True,
                        )
                        pasta.adicionar_arquivo(sub_arquivo=arquivo)
                    else:
                        logger.debug("Arquivo ignorado (não atende padrão): %s", item)
        except PermissionError:
            logger.warning("Sem permissão para acessar: %s", pasta.caminho_absoluto)

    def _coletar_arquivos_html(
        self, pasta: ModeloPasta, coletor: list[ModeloArquivo]
    ) -> None:
        """Recolhe recursivamente os ModeloArquivo HTML da árvore."""
        html_na_pasta = [arquivo for arquivo in pasta.subarquivos if arquivo.eh_html]
        logger.debug(
            "Coletando %d arquivos HTML de %s",
            len(html_na_pasta),
            pasta.caminho_absoluto,
        )
        coletor.extend(html_na_pasta)
        for sub in pasta.subpastas:
            self._coletar_arquivos_html(pasta=sub, coletor=coletor)

    @staticmethod
    def _deve_ignorar_diretorio(diretorio: Path) -> bool:
        """Pastas ocultas ou de sistema devem ser ignoradas."""
        ignorar = diretorio.name.startswith(".") or diretorio.name.lower() in {
            "system volume information",
            "$recycle.bin",
            "recycler",
            "lost+found",
        }
        if ignorar:
            logger.debug("Diretório será ignorado: %s", diretorio)
        return ignorar

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
            logger.debug("Extensão não HTML: %s", arquivo)
            return False

        # Aplica a regex sobre o nome completo (stem + extensão)
        valido = bool(_PADRAO_NOME_ARQUIVO.fullmatch(arquivo.name))
        if not valido:
            logger.debug("Nome não corresponde ao padrão: %s", arquivo.name)
        return valido

    # ── aliases de compatibilidade ────────────────────────────────

    def _scan_recursive(self, pasta_atual: ModeloPasta) -> None:
        """Alias para _varrer_recursivamente."""
        logger.debug("Usando alias '_scan_recursive'")
        self._varrer_recursivamente(pasta=pasta_atual)

    def _collect_html_files(
        self, pasta: ModeloPasta, coletor: list[ModeloArquivo]
    ) -> None:
        """Alias para _coletar_arquivos_html."""
        logger.debug("Usando alias '_collect_html_files'")
        self._coletar_arquivos_html(pasta=pasta, coletor=coletor)
