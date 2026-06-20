# Atoms/frontend/cli/cli_display.py
# pylint: disable=too-many-arguments,too-many-positional-arguments

"""Funções de apresentação de dados para o Neutron Star.

Fornece visualizações em linha de comando para as entidades do domínio:
- Sistema operacional
- Pastas e arquivos
- Favoritos extraídos
- Estatísticas do processamento
"""

import logging
from pathlib import Path

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_bookmark import Favorito
from backend.core.entidades.entidade_diretorio import ModeloPasta
from backend.core.entidades.entidade_sistema_operacional import (
    ModeloSistemaOperacional,
)
from backend.infrastructure.exporters.csv_exporter import CSVExporter
from backend.infrastructure.exporters.json_exporter import JSONExporter
from backend.infrastructure.exporters.pdf_exporter import PDFExporter

logger: logging.Logger = logging.getLogger(name=__name__)


def cli_exibir_sistema_operacional(so: ModeloSistemaOperacional) -> None:
    """Exibe informações do sistema operacional usando o modelo de domínio."""
    a: str = str(so.nome_sistema)
    b: str = str(so.versao_sistema)
    c: str = str(so.pasta_usuario)
    logger.info("🖥️  Sistema: %s | Versão: %s | Home: %s", a, b, c)


def cli_exibir_pasta(
    nome_pasta: str,
    caminho_absoluto: Path,
    pasta_pai: ModeloPasta | None,
    subpastas: list[ModeloPasta],
    subarquivos: list[ModeloArquivo],
    titulo: str | None = None,
) -> None:
    """Exibe informações de uma pasta."""
    cabecalho: str = titulo or "Pasta"
    pai_nome: str = pasta_pai.nome_pasta if pasta_pai else "(raiz)"
    logger.info("📁 %s: %s", cabecalho, nome_pasta)
    logger.info("   Caminho: %s", caminho_absoluto)
    logger.info("   Pasta pai: %s", pai_nome)
    logger.info("   Subpastas: %d | Arquivos: %d", len(subpastas), len(subarquivos))


def cli_exibir_arquivo(
    nome_arquivo: str,
    caminho_arquivo: str,
    tamanho_arquivo: int,
    eh_html: bool | None = None,
    *,
    is_html: bool | None = None,
) -> None:
    """Exibe informações de um arquivo."""
    html: bool = eh_html if eh_html is not None else bool(is_html)
    logger.info(
        "📄 Arquivo: %s | Caminho: %s | Tamanho: %d bytes | HTML: %s",
        nome_arquivo,
        caminho_arquivo,
        tamanho_arquivo,
        html,
    )


def cli_exibir_estatisticas(
    estatisticas: dict[str, int] | None = None, *, stats: dict[str, int] | None = None
) -> None:
    """Exibe estatísticas do processamento de favoritos."""
    dados_estatisticas: dict[str, int] = estatisticas or stats or {}
    logger.info("📊 Estatísticas do processamento:")
    for chave, valor in dados_estatisticas.items():
        logger.info("   %s: %s", chave, valor)


def cli_exibir_favoritos(favoritos: list[Favorito], limite: int = 5) -> None:
    """Exibe os primeiros favoritos encontrados.

    Args:
        favoritos: Lista de favoritos.
        limite: Quantos favoritos exibir.
    """
    if not favoritos:
        logger.info("Nenhum favorito encontrado.")
        return

    logger.info("🔖 Exibindo os primeiros %d favoritos:", min(limite, len(favoritos)))
    for indice, favorito in enumerate(favoritos[:limite], start=1):
        logger.info("   %d. %s", indice, favorito.titulo)
        logger.info("      URL: %s", favorito.url)
        if favorito.data_adicao:
            logger.info(
                "      Adicionado em: %s",
                favorito.data_adicao.strftime("%Y-%m-%d %H:%M:%S"),
            )


def cli_exibir_bookmarks(bookmarks: list[Favorito], limite: int = 5) -> None:
    """Alias de compatibilidade para `cli_exibir_favoritos`."""
    logger.debug("Usando alias 'cli_exibir_bookmarks'")
    cli_exibir_favoritos(favoritos=bookmarks, limite=limite)


def menu_exportar(favoritos: list[Favorito]) -> None:
    """Oferece opções de exportação e executa o exportador escolhido."""
    if not favoritos:
        logger.debug("Menu de exportação chamado sem favoritos – ignorado.")
        return

    print("\n📤 Exportar favoritos:")  # mantido como print para interação imediata
    print("1. JSON")
    print("2. CSV")
    print("3. PDF")
    print("4. Não exportar")

    opcao: str = input("Escolha (1-4): ").strip()
    logger.debug("Opção de exportação escolhida: %s", opcao)

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
        logger.info("✅ Exportado para %s", pasta_saida_conversoes.resolve())
    elif opcao == "4":
        logger.info("Exportação cancelada pelo usuário.")
    else:
        logger.warning("Opção de exportação inválida: %s", opcao)
