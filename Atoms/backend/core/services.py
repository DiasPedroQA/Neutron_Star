# Atoms/backend/core/services.py

"""Serviço principal que orquestra o processamento de favoritos."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TypeVar

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_bookmark import Favorito
from backend.core.entidades.entidade_diretorio import ModeloPasta
from backend.core.entidades.entidade_processamento import (
    EstatisticasProcessamento,
    ResultadoProcessamento,
)
from backend.core.interfaces.bookmark_exporter import FavoritoExporter
from backend.core.interfaces.bookmark_parser import FavoritoParser
from backend.core.interfaces.bookmark_repository import FavoritoRepository
from backend.core.interfaces.file_scanner import FileScanner

logger: logging.Logger = logging.getLogger(name=__name__)

T = TypeVar("T")


class FavoritoProcessingService:
    """Contém a lógica de negócio para processar favoritos."""

    def __init__(
        self,
        vassoura: FileScanner | None = None,
        analisador: FavoritoParser | None = None,
        exportador: FavoritoExporter | None = None,
        repositorio: FavoritoRepository | None = None,
        *,
        scanner: FileScanner | None = None,
        parser: FavoritoParser | None = None,
        exporter: FavoritoExporter | None = None,
        repository: FavoritoRepository | None = None,
    ) -> None:
        """Injeta dependências de infraestrutura via abstrações."""
        self.vassoura, self.analisador, self.exportador, self.repositorio = (
            self._resolver_dependencias(
                vassoura=vassoura,
                analisador=analisador,
                exportador=exportador,
                repositorio=repositorio,
                scanner=scanner,
                parser=parser,
                exporter=exporter,
                repository=repository,
            )
        )
        self._log_inicializacao()

    def _resolver_dependencias(
        self,
        vassoura: FileScanner | None,
        analisador: FavoritoParser | None,
        exportador: FavoritoExporter | None,
        repositorio: FavoritoRepository | None,
        scanner: FileScanner | None,
        parser: FavoritoParser | None,
        exporter: FavoritoExporter | None,
        repository: FavoritoRepository | None,
    ) -> tuple[
        FileScanner,
        FavoritoParser,
        FavoritoExporter | None,
        FavoritoRepository | None,
    ]:
        """Resolve as dependências, usando fallback para parâmetros legados."""
        # Registro de uso de parâmetros legados
        if vassoura is None and scanner is not None:
            logger.info("Usando parâmetro 'scanner' em vez de 'vassoura'")
        if analisador is None and parser is not None:
            logger.info("Usando parâmetro 'parser' em vez de 'analisador'")
        if exportador is None and exporter is not None:
            logger.info("Usando parâmetro 'exporter' em vez de 'exportador'")
        if repositorio is None and repository is not None:
            logger.info("Usando parâmetro 'repository' em vez de 'repositorio'")

        varredor_final: FileScanner | None = vassoura or scanner
        analisador_final: FavoritoParser | None = analisador or parser

        if varredor_final is None or analisador_final is None:
            logger.error(
                "Dependências obrigatórias ausentes: scanner=%s, parser=%s",
                varredor_final,
                analisador_final,
            )
            raise ValueError("vassoura e analisador são obrigatórios")

        return (
            varredor_final,
            analisador_final,
            exportador or exporter,
            repositorio or repository,
        )

    def _log_inicializacao(self) -> None:
        """Registra resumo das dependências injetadas."""
        logger.debug(
            "Serviço inicializado: scanner=%s, parser=%s, exporter=%s, repository=%s",
            type(self.vassoura).__name__,
            type(self.analisador).__name__,
            type(self.exportador).__name__ if self.exportador else None,
            type(self.repositorio).__name__ if self.repositorio else None,
        )

    # ── Métodos de processamento e exportação ──────────────────────

    def processar_diretorio(self, caminho_raiz: Path) -> ResultadoProcessamento:
        """Processa um diretório e retorna favoritos encontrados e estatísticas."""
        logger.info("Iniciando processamento do diretório: %s", caminho_raiz)

        pasta_raiz_usuario = ModeloPasta(
            nome_pasta=caminho_raiz.name, caminho_absoluto=caminho_raiz
        )
        logger.debug("Pasta raiz criada: %s", pasta_raiz_usuario.caminho_absoluto)

        self.vassoura.varrer_diretorio(pasta_raiz=pasta_raiz_usuario)
        arquivos_html: list[ModeloArquivo] = self.vassoura.localizar_arquivos_html(
            pasta=pasta_raiz_usuario
        )

        total_encontrados = len(arquivos_html)
        logger.info("Arquivos HTML encontrados: %d", total_encontrados)
        if total_encontrados == 0:
            logger.warning("Nenhum arquivo HTML encontrado em %s", caminho_raiz)

        favoritos: list[Favorito] = []
        estatisticas = EstatisticasProcessamento(
            total_arquivos=total_encontrados,
            arquivos_processados=0,
            arquivos_com_falha=0,
            total_favoritos=0,
        )

        for arquivo_html in arquivos_html:
            logger.debug("Analisando arquivo: %s", arquivo_html.caminho_arquivo)

            if not self.analisador.suporta_arquivo(arquivo=arquivo_html):
                logger.warning(
                    "Arquivo não suportado pelo parser: %s",
                    arquivo_html.caminho_arquivo,
                )
                estatisticas.arquivos_com_falha += 1
                continue

            if favoritos_extraidos := self.analisador.analisar_arquivo(
                arquivo=arquivo_html
            ):
                favoritos.extend(favoritos_extraidos)
                estatisticas.arquivos_processados += 1
                estatisticas.total_favoritos += len(favoritos_extraidos)
                logger.debug(
                    "Extraídos %d favoritos de %s",
                    len(favoritos_extraidos),
                    arquivo_html.caminho_arquivo,
                )
            else:
                logger.info(
                    "Nenhum favorito extraído de %s", arquivo_html.caminho_arquivo
                )
                estatisticas.arquivos_com_falha += 1

        logger.info(
            "Processamento concluído: total_arquivos=%d, processados=%d, falhas=%d, favoritos=%d",
            estatisticas.total_arquivos,
            estatisticas.arquivos_processados,
            estatisticas.arquivos_com_falha,
            estatisticas.total_favoritos,
        )

        return ResultadoProcessamento(
            favoritos_processados=favoritos,
            estatisticas_processadas=estatisticas,
            caminho_raiz=str(caminho_raiz),
        )

    def exportar_favoritos(
        self,
        links_favoritos: list[Favorito],
        caminho_saida: Path,
        formato_saida: str = "json",
    ) -> None:
        """Exporta favoritos usando o exportador configurado.

        Raises:
            ValueError: Quando nenhum exportador está configurado ou o formato não é suportado.
        """
        exportador = self.exportador
        if not exportador:
            logger.error("Tentativa de exportar sem exportador configurado")
            raise ValueError("Nenhum exportador configurado")

        formatos_validos: str = exportador.obter_formatos_suportados()
        if formato_saida not in formatos_validos:
            logger.error(
                "Formato inválido '%s'. Formatos suportados: %s",
                formato_saida,
                formatos_validos,
            )
            raise ValueError(
                f"Formato '{formato_saida}' não suportado. Use: {formatos_validos}"
            )

        if not caminho_saida.suffix:
            novo_caminho = caminho_saida.with_suffix(f".{formato_saida}")
            logger.debug(
                "Ajustando extensão do arquivo: %s -> %s", caminho_saida, novo_caminho
            )
            caminho_saida = novo_caminho

        logger.info(
            "Exportando %d favoritos para %s (formato %s)",
            len(links_favoritos),
            caminho_saida,
            formato_saida,
        )
        exportador.exportar(lista_favoritos=links_favoritos, saida=caminho_saida)
        logger.debug("Exportação concluída")

    def salvar_no_repositorio(
        self,
        favoritos: list[Favorito] | None = None,
        id_sessao: str = "",
        *,
        bookmarks: list[Favorito] | None = None,
    ) -> None:
        """Salva favoritos no repositório, quando presente."""
        favoritos_finais: list[Favorito] = (
            favoritos if favoritos is not None else (bookmarks or [])
        )

        if bookmarks is not None and favoritos is None:
            logger.info("Usando parâmetro 'bookmarks' em vez de 'favoritos'")

        repositorio = self.repositorio
        if not repositorio:
            logger.debug("Repositório não configurado – nada será salvo")
            return

        logger.info(
            msg=f"Salvando {len(favoritos_finais)} favoritos no repositório (id_sessao={id_sessao})"
        )
        repositorio.salvar(favoritos=favoritos_finais, identificador=id_sessao)
        logger.debug("Favoritos salvos com sucesso")

    # ── Aliases de compatibilidade ─────────────────────────────────

    def exportar_bookmarks(
        self, bookmarks: list[Favorito], output_dir: Path, formato: str = "json"
    ) -> None:
        """Alias de compatibilidade para `exportar_favoritos`."""
        logger.debug("Usando alias 'exportar_bookmarks'")
        self.exportar_favoritos(
            links_favoritos=bookmarks, caminho_saida=output_dir, formato_saida=formato
        )

    def process_directory(self, root_path: Path) -> ResultadoProcessamento:
        """Alias de compatibilidade para `processar_diretorio`."""
        logger.debug("Usando alias 'process_directory' para %s", root_path)
        return self.processar_diretorio(caminho_raiz=root_path)

    def export_bookmarks(
        self, bookmarks: list[Favorito], output_path: Path, formato: str = "json"
    ) -> None:
        """Alias de compatibilidade para `exportar_favoritos`."""
        logger.debug("Usando alias 'export_bookmarks'")
        self.exportar_favoritos(
            links_favoritos=bookmarks, caminho_saida=output_path, formato_saida=formato
        )

    def save_to_repository(self, bookmarks: list[Favorito], session_id: str) -> None:
        """Alias de compatibilidade para `salvar_no_repositorio`."""
        logger.debug("Usando alias 'save_to_repository'")
        self.salvar_no_repositorio(favoritos=bookmarks, id_sessao=session_id)
