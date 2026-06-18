# Atoms/frontend/cli/main.py

"""Ponto de entrada CLI para o Neutron Star."""

from __future__ import annotations
import sys
import logging
from pathlib import Path
from typing import Any

from frontend.cli.cli_display import cli_exibir_sistema_operacional
from frontend.cli.cli_display import cli_exibir_favoritos as exibir_favoritos
from frontend.cli.cli_display import cli_exibir_estatisticas as exibir_estatisticas
from backend.infrastructure.so_identifier import DetectarSistemaOperacional
from backend.infrastructure.parser import TagsFinder
from backend.infrastructure.file_scanners import FileSystemScanner
from backend.infrastructure.exporters.pdf_exporter import PDFExporter
from backend.infrastructure.exporters.json_exporter import JSONExporter
from backend.infrastructure.exporters.csv_exporter import CSVExporter
from backend.core.services import BookmarkProcessingService
from backend.core.entidades.entidade_sistema_operacional import (
    ModeloSistemaOperacional,
)
from backend.core.entidades.entidade_processamento import ResultadoProcessamento
from backend.core.entidades.entidade_bookmark import Favorito
from backend.debug_config import load_debug_config, setup_logging as setup_debug_logging


# Garantia de que a raiz do projeto (Atoms/) está no PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


def criar_servico() -> BookmarkProcessingService:
    """Fabrica o serviço de processamento com as implementações concretas."""
    varredor = FileSystemScanner()
    buscador = TagsFinder()
    return BookmarkProcessingService(
        vassoura=varredor,
        analisador=buscador,
        exportador=None,
    )


def exibir_resultados(
    links_favoritos: list[Favorito], stats_bookmark: dict[str, int]
) -> None:
    """Exibe estatísticas e os primeiros favoritos encontrados."""
    exibir_estatisticas(estatisticas=stats_bookmark)
    if links_favoritos:
        exibir_favoritos(favoritos=links_favoritos[:5])
    else:
        print("Nenhum favorito encontrado.")


def menu_exportar(favoritos: list[Favorito]) -> None:
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
        nome_arquivo: str = f"bookmarks.{exportador.obter_formatos_suportados()}"
        pasta_saida_conversoes = Path("Atoms/outputs/", nome_arquivo)
        exportador.exportar(lista_favoritos=favoritos, saida=pasta_saida_conversoes)
        print(f"✅ Exportado para {pasta_saida_conversoes.resolve()}")
    elif opcao == "4":
        print("Exportação cancelada. Loop encerrado.")
    else:
        print("Opção inválida.")


def main() -> None:
    """Função principal do CLI."""

    # ---------- Configuração de debug via JSON ----------
    config_path: Path = (
        Path(__file__).resolve().parent.parent.parent / "debug_config.json"
    )
    config: dict[str, Any] = load_debug_config(config_path=str(config_path))
    setup_debug_logging(config)

    logger: logging.Logger = logging.getLogger(__name__)

    identificador = DetectarSistemaOperacional()
    so_identificado: ModeloSistemaOperacional = (
        identificador.detectar_sistema_operacional()
    )
    cli_exibir_sistema_operacional(so=so_identificado)

    servico: BookmarkProcessingService = criar_servico()

    logger.info(
        msg=f"Iniciando processamento do diretório: {so_identificado.pasta_usuario}"
    )
    resultado: ResultadoProcessamento = servico.processar_diretorio(
        caminho_raiz=so_identificado.pasta_usuario
    )

    favoritos_extraidos: list[Favorito] = resultado.favoritos_processados
    estatisticas: dict[str, int] = resultado.estatisticas_processadas.para_dict()

    exibir_resultados(links_favoritos=favoritos_extraidos, stats_bookmark=estatisticas)
    menu_exportar(favoritos=favoritos_extraidos)


if __name__ == "__main__":
    main()
