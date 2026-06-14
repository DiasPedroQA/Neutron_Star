# Atoms/frontend/display.py
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Funções de apresentação de dados para o Neutron Star/Atoms.

Fornece visualizações em linha de comando para as entidades do domínio:
- Sistema operacional
- Pastas e arquivos
- Bookmarks extraídos
- Estatísticas do processamento
"""

from pathlib import Path

from Atoms.backend.core.entidades.entidade_arquivo import ModeloArquivo
from Atoms.backend.core.entidades.entidade_bookmark import Bookmark
from Atoms.backend.core.entidades.entidade_diretorio import ModeloPasta
from Atoms.backend.core.entidades.entidade_sistema_operacional import ModeloSistemaOperacional


def cli_exibir_sistema_operacional(so: ModeloSistemaOperacional) -> None:
    """Exibe informações do sistema operacional usando o modelo de domínio."""
    print(f"🖥️  Sistema: {so.nome_sistema} | " f"Versão: {so.versao_sistema} | " f"Home: {so.user_home}")


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
    print(f"\n📁 {cabecalho}: {nome_pasta}")
    print(f"   Caminho: {caminho_absoluto}")
    pai_nome = pasta_pai.nome_pasta if pasta_pai else "(raiz)"
    print(f"   Pasta pai: {pai_nome}")
    print(f"   Subpastas: {len(subpastas)} | Arquivos: {len(subarquivos)}")


def cli_exibir_arquivo(nome_arquivo: str, caminho_arquivo: str, tamanho_arquivo: int, is_html: bool) -> None:
    """Exibe informações de um arquivo."""
    print(f"📄 Arquivo: {nome_arquivo} | " f"Caminho: {caminho_arquivo} | " f"Tamanho: {tamanho_arquivo} bytes | " f"HTML: {is_html}")


def cli_exibir_estatisticas(stats: dict[str, int]) -> None:
    """Exibe estatísticas do processamento de bookmarks."""
    print("\n📊 Estatísticas do processamento:")
    for chave, valor in stats.items():
        print(f"   {chave}: {valor}")


def cli_exibir_bookmarks(bookmarks: list[Bookmark], limite: int = 5) -> None:
    """Exibe os primeiros bookmarks encontrados.

    Args:
        bookmarks: lista de bookmarks.
        limite: quantos bookmarks exibir (padrão: 5).
    """
    if not bookmarks:
        print("Nenhum bookmark encontrado.")
        return

    print(f"\n🔖 Exibindo os primeiros {min(limite, len(bookmarks))} bookmarks:")
    for i, bm in enumerate(bookmarks[:limite], start=1):
        print(f"   {i}. {bm.title}")
        print(f"      URL: {bm.url}")
        if bm.add_date:
            print(f"      Adicionado em: {bm.add_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
