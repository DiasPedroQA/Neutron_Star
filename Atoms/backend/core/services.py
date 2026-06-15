"""Serviço principal que orquestra o processamento de favoritos."""

from __future__ import annotations

from pathlib import Path

from Atoms.backend.core.entidades.entidade_arquivo import ModeloArquivo
from Atoms.backend.core.entidades.entidade_bookmark import Favorito
from Atoms.backend.core.entidades.entidade_diretorio import ModeloPasta
from Atoms.backend.core.entidades.entidade_processamento import EstatisticasProcessamento, ResultadoProcessamento
from Atoms.backend.core.interfaces.bookmark_exporter import BookmarkExporter
from Atoms.backend.core.interfaces.bookmark_parser import BookmarkParser
from Atoms.backend.core.interfaces.bookmark_repository import BookmarkRepository
from Atoms.backend.core.interfaces.file_scanner import FileScanner


class BookmarkProcessingService:
    """Contém a lógica de negócio para processar favoritos."""

    def __init__(
        self,
        varredor: FileScanner | None = None,
        analisador: BookmarkParser | None = None,
        exportador: BookmarkExporter | None = None,
        repositorio: BookmarkRepository | None = None,
        *,
        scanner: FileScanner | None = None,
        parser: BookmarkParser | None = None,
        exporter: BookmarkExporter | None = None,
        repository: BookmarkRepository | None = None,
    ) -> None:
        """Injeta dependências de infraestrutura via abstrações.

        Args:
            varredor: Implementação de FileScanner.
            analisador: Implementação de BookmarkParser.
            exportador: Implementação de BookmarkExporter (opcional).
            repositorio: Implementação de BookmarkRepository (opcional).
        """
        varredor_final = varredor or scanner
        analisador_final = analisador or parser
        if varredor_final is None or analisador_final is None:
            raise ValueError("varredor e analisador são obrigatórios")

        self.varredor: FileScanner = varredor_final
        self.analisador: BookmarkParser = analisador_final
        self.exportador: BookmarkExporter | None = exportador or exporter
        self.repositorio: BookmarkRepository | None = repositorio or repository

    def processar_diretorio(self, caminho_raiz: Path) -> ResultadoProcessamento:
        """Processa um diretório e retorna favoritos encontrados e estatísticas.

        :param caminho_raiz: Caminho absoluto do diretório a ser processado.
        :return: Objeto de resultado de processamento com favoritos e estatísticas.
        """
        pasta_raiz = ModeloPasta(nome_pasta=caminho_raiz.name, caminho_absoluto=caminho_raiz)

        self.varredor.varrer_diretorio(pasta_raiz=pasta_raiz)
        arquivos_html: list[ModeloArquivo] = self.varredor.localizar_arquivos_html(pasta=pasta_raiz)

        favoritos: list[Favorito] = []
        estatisticas = EstatisticasProcessamento(
            total_arquivos=len(arquivos_html),
            arquivos_processados=0,
            arquivos_com_falha=0,
            total_favoritos=0,
        )

        for arquivo_html in arquivos_html:
            if not self.analisador.suporta_arquivo(arquivo=arquivo_html):
                estatisticas.arquivos_com_falha += 1
                continue
            if favoritos_extraidos := self.analisador.analisar_arquivo(arquivo=arquivo_html):
                favoritos.extend(favoritos_extraidos)
                estatisticas.arquivos_processados += 1
                estatisticas.total_favoritos += len(favoritos_extraidos)
            else:
                estatisticas.arquivos_com_falha += 1

        return ResultadoProcessamento(
            favoritos=favoritos,
            estatisticas=estatisticas,
            caminho_raiz=str(caminho_raiz),
        )

    def exportar_favoritos(self, favoritos: list[Favorito], caminho_saida: Path, formato: str = "json") -> None:
        """Exporta favoritos usando o exportador configurado.

        Args:
            favoritos: Lista de favoritos a exportar.
            caminho_saida: Caminho do arquivo de saída.
            formato: Extensão de saída do arquivo.

        Raises:
            ValueError: Quando nenhum exportador está configurado ou o formato não é suportado.
        """
        if not self.exportador:
            raise ValueError("Nenhum exportador configurado")

        formatos_validos: list[str] = self.exportador.obter_formatos_suportados()
        if formato not in formatos_validos:
            raise ValueError(f"Formato '{formato}' não suportado. Use: {formatos_validos}")

        if not caminho_saida.suffix:
            caminho_saida = caminho_saida.with_suffix(f".{formato}")

        self.exportador.exportar(favoritos, caminho_saida)

    def salvar_no_repositorio(
        self,
        favoritos: list[Favorito] | None = None,
        id_sessao: str = "",
        *,
        bookmarks: list[Favorito] | None = None,
    ) -> None:
        """Salva favoritos no repositório, quando presente.

        Args:
            favoritos: Lista de favoritos a persistir.
            id_sessao: Identificador da sessão usada como chave.
        """
        favoritos_finais = favoritos if favoritos is not None else (bookmarks or [])
        if self.repositorio:
            self.repositorio.salvar(favoritos_finais, id_sessao)

    def exportar_bookmarks(self, bookmarks: list[Favorito], caminho_saida: Path, formato: str = "json") -> None:
        """Alias de compatibilidade para `exportar_favoritos`."""
        self.exportar_favoritos(favoritos=bookmarks, caminho_saida=caminho_saida, formato=formato)

    def process_directory(self, root_path: Path) -> ResultadoProcessamento:
        """Alias de compatibilidade para `processar_diretorio`."""
        return self.processar_diretorio(caminho_raiz=root_path)

    def export_bookmarks(self, bookmarks: list[Favorito], output_path: Path, formato: str = "json") -> None:
        """Alias de compatibilidade para `exportar_favoritos`."""
        self.exportar_favoritos(favoritos=bookmarks, caminho_saida=output_path, formato=formato)

    def save_to_repository(self, bookmarks: list[Favorito], session_id: str) -> None:
        """Alias de compatibilidade para `salvar_no_repositorio`."""
        self.salvar_no_repositorio(favoritos=bookmarks, id_sessao=session_id)


FavoritoProcessingService = BookmarkProcessingService
