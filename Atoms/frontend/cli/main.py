# Atoms/frontend/cli/main.py

"""Ponto de entrada CLI para o Neutron Star."""

from __future__ import annotations

import logging
from pathlib import Path

from Atoms.backend.core.entidades.entidade_bookmark import Favorito
from Atoms.backend.core.entidades.entidade_processamento import ResultadoProcessamento
from Atoms.backend.core.entidades.entidade_sistema_operacional import (
    ModeloSistemaOperacional,
)
from Atoms.backend.core.services import BookmarkProcessingService
from Atoms.backend.infrastructure.exporters.csv_exporter import CSVExporter
from Atoms.backend.infrastructure.exporters.json_exporter import JSONExporter
from Atoms.backend.infrastructure.exporters.pdf_exporter import PDFExporter
from Atoms.backend.infrastructure.file_scanners import FileSystemScanner
from Atoms.backend.infrastructure.parser import TagsFinder
from Atoms.backend.infrastructure.so_identifier import DetectarSistemaOperacional
from Atoms.frontend.cli_display import cli_exibir_estatisticas as exibir_estatisticas
from Atoms.frontend.cli_display import cli_exibir_favoritos as exibir_favoritos
from Atoms.frontend.cli_display import cli_exibir_sistema_operacional


def setup_logging() -> None:
    """Configura o logging básico para o CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def criar_servico() -> BookmarkProcessingService:
    """Fabrica o serviço de processamento com as implementações concretas."""
    varredor = FileSystemScanner()
    analisador = TagsFinder()
    return BookmarkProcessingService(
        varredor=varredor,
        analisador=analisador,
        exportador=None,
    )


def exibir_resultados(favoritos: list[Favorito], estatisticas: dict[str, int]) -> None:
    """Exibe estatísticas e os primeiros favoritos encontrados."""
    exibir_estatisticas(estatisticas=estatisticas)
    if favoritos:
        exibir_favoritos(favoritos=favoritos[:5])
    else:
        print("Nenhum favorito encontrado.")


def exportar(favoritos: list[Favorito]) -> None:
    """Oferece opções de exportação e executa o exportador escolhido."""
    if not favoritos:
        return

    print("\n📤 Exportar favoritos:")
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
        exportador: JSONExporter | CSVExporter | PDFExporter = exportadores[opcao]
        nome_arquivo: str = f"bookmarks.{exportador.obter_formatos_suportados()[0]}"
        caminho = Path(nome_arquivo)
        exportador.exportar(favoritos=favoritos, saida=caminho)
        print(f"✅ Exportado para {caminho.resolve()}")
    elif opcao == "4":
        print("Exportação cancelada.")
    else:
        print("Opção inválida.")


def main() -> None:
    """Função principal do CLI."""
    setup_logging()
    logger: logging.Logger = logging.getLogger(name=__name__)

    identificador = DetectarSistemaOperacional()
    so: ModeloSistemaOperacional = identificador.detectar_sistema_operacional()
    cli_exibir_sistema_operacional(so=so)

    servico: BookmarkProcessingService = criar_servico()

    logger.info(msg=f"Iniciando processamento do diretório: {so.pasta_usuario}")
    resultado: ResultadoProcessamento = servico.processar_diretorio(
        caminho_raiz=so.pasta_usuario
    )

    favoritos: list[Favorito] = resultado.favoritos
    estatisticas: dict[str, int] = resultado.estatisticas.para_dict()

    exibir_resultados(favoritos=favoritos, estatisticas=estatisticas)

    exportar(favoritos=favoritos)


if __name__ == "__main__":
    main()
