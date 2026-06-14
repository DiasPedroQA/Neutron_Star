# Atoms/frontend/cli/main.py

"""Ponto de entrada CLI para o Neutron Star."""

from __future__ import annotations

import logging
from pathlib import Path

from Atoms.backend.core.entidades.entidade_bookmark import Bookmark
from Atoms.backend.core.entidades.entidade_sistema_operacional import ModeloSistemaOperacional
from Atoms.backend.core.entidades.resultado_processamento import ResultadoProcessamento
from Atoms.backend.core.services import BookmarkProcessingService
from Atoms.backend.infrastructure.exporters import CSVExporter, JSONExporter, PDFExporter
from Atoms.backend.infrastructure.identifier import DetectarSistemaOperacional
from Atoms.backend.infrastructure.parser import TagsFinder
from Atoms.backend.infrastructure.scanners import FileSystemScanner
from Atoms.frontend.display import cli_exibir_bookmarks as exibir_bookmarks
from Atoms.frontend.display import cli_exibir_estatisticas as exibir_estatisticas
from Atoms.frontend.display import cli_exibir_sistema_operacional


def setup_logging() -> None:
    """Configura o logging básico para o CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def criar_servico() -> BookmarkProcessingService:
    """Fabrica o serviço de processamento com as implementações concretas."""
    scanner = FileSystemScanner()
    parser = TagsFinder()
    # O exporter é opcional; pode ser escolhido mais tarde
    return BookmarkProcessingService(scanner=scanner, parser=parser, exporter=None)


def exibir_resultados(bookmarks: list[Bookmark], stats: dict[str, int]) -> None:
    """Exibe estatísticas e os primeiros bookmarks encontrados."""
    exibir_estatisticas(stats=stats)
    if bookmarks:
        exibir_bookmarks(bookmarks=bookmarks[:5])  # mostra só os 5 primeiros
    else:
        print("Nenhum bookmark encontrado.")


def exportar(bookmarks: list[Bookmark]) -> None:
    """Oferece opções de exportação e executa o exportador escolhido."""
    if not bookmarks:
        return

    print("\n📤 Exportar bookmarks:")
    print("1. JSON")
    print("2. CSV")
    print("3. PDF")
    print("4. Não exportar")

    opcao: str = input("Escolha (1-4): ").strip()

    exportadores: dict[str, JSONExporter | CSVExporter | PDFExporter] = {
        "1": JSONExporter(),
        "2": CSVExporter(),
        "3": PDFExporter(),
    }

    if opcao in exportadores:
        exporter: JSONExporter | CSVExporter | PDFExporter = exportadores[opcao]
        # O nome do arquivo pode ser fixo ou perguntado ao usuário
        nome_arquivo: str = f"bookmarks.{exporter.get_supported_formats()[0]}"
        caminho = Path(nome_arquivo)
        exporter.export(bookmarks=bookmarks, saida=caminho)
        print(f"✅ Exportado para {caminho.resolve()}")
    elif opcao == "4":
        print("Exportação cancelada.")
    else:
        print("Opção inválida.")


def main() -> None:
    """Função principal do CLI."""
    setup_logging()
    logger: logging.Logger = logging.getLogger(name=__name__)

    # 1. Detectar sistema operacional
    identificador = DetectarSistemaOperacional()
    so: ModeloSistemaOperacional = identificador.detectar_sistema_operacional()
    cli_exibir_sistema_operacional(so=so)

    # 2. Criar serviço com as dependências concretas
    servico: BookmarkProcessingService = criar_servico()

    # 3. Processar o diretório home do usuário
    logger.info(msg=f"Iniciando processamento do diretório: {so.user_home}")
    resultado: ResultadoProcessamento = servico.process_directory(root_path=so.user_home)

    bookmarks: list[Bookmark] = resultado.bookmarks
    estatisticas: dict[str, int] = resultado.statistics.to_dict()

    # 5. Exibir resultados
    exibir_resultados(bookmarks=bookmarks, stats=estatisticas)

    # 6. Oferecer exportação
    exportar(bookmarks=bookmarks)


if __name__ == "__main__":
    main()
