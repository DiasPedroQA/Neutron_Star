# Atoms/frontend/cli/main.py

"""Ponto de entrada CLI para o Neutron Star."""

from __future__ import annotations
import sys
import logging
from pathlib import Path

from frontend.cli.cli_display import cli_exibir_sistema_operacional, menu_exportar
from frontend.cli.cli_display import cli_exibir_favoritos as exibir_favoritos
from frontend.cli.cli_display import cli_exibir_estatisticas as exibir_estatisticas
from backend.infrastructure.controllers.so_identifier import DetectarSistemaOperacional
from backend.infrastructure.controllers.parser import AnalisadorTags
from backend.infrastructure.controllers.file_scanners import VarredorSistemaArquivos
from backend.core.services import FavoritoProcessingService
from backend.core.entidades.entidade_sistema_operacional import (
    ModeloSistemaOperacional,
)
from backend.core.entidades.entidade_processamento import ResultadoProcessamento
from backend.core.entidades.entidade_bookmark import Favorito
from backend.debug_config import (
    DebugConfig,
    load_debug_config,
    setup_logging as setup_debug_logging,
)


# Garantia de que a raiz do projeto (Atoms/) está no PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


def criar_servico() -> FavoritoProcessingService:
    """Fabrica o serviço de processamento com as implementações concretas."""
    varredor = VarredorSistemaArquivos()
    buscador = AnalisadorTags()
    return FavoritoProcessingService(
        vassoura=varredor,
        analisador=buscador,
        exportador=None,
    )


def exibir_resultados(
    links_favoritos: list[Favorito], stats_bookmark: dict[str, int]
) -> None:
    """Exibe estatísticas e os favoritos encontrados."""
    exibir_estatisticas(estatisticas=stats_bookmark)
    if links_favoritos:
        exibir_favoritos(favoritos=links_favoritos)
    else:
        print("Nenhum favorito encontrado.")


def main() -> None:
    """Função principal do CLI."""

    # ---------- Configuração de debug via JSON ----------
    config_path: Path = (
        Path(__file__).resolve().parent.parent.parent / "outputs/debug_config.json"
    )
    config: DebugConfig = load_debug_config(config_path=str(config_path))
    setup_debug_logging(config=config)

    logger: logging.Logger = logging.getLogger(name=__name__)

    identificador = DetectarSistemaOperacional()
    so_identificado: ModeloSistemaOperacional = (
        identificador.detectar_sistema_operacional()
    )
    cli_exibir_sistema_operacional(so=so_identificado)

    servico: FavoritoProcessingService = criar_servico()

    logger.info(
        msg=f"Iniciando processamento do diretório: {so_identificado.pasta_usuario}"
    )
    processamento_dados: ResultadoProcessamento = servico.processar_diretorio(
        caminho_raiz=so_identificado.pasta_usuario
    )

    favoritos_extraidos: list[Favorito] = processamento_dados.favoritos_processados
    estatisticas: dict[str, int] = (
        processamento_dados.estatisticas_processadas.para_dict()
    )

    exibir_resultados(links_favoritos=favoritos_extraidos, stats_bookmark=estatisticas)
    menu_exportar(favoritos=favoritos_extraidos)


if __name__ == "__main__":
    main()
