# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments

"""Funções de apresentação de dados para o Neutron Star.

Fornece visualizações em linha de comando para as entidades do domínio:
- Sistema operacional
- Pastas e arquivos
- Favoritos extraídos
- Estatísticas do processamento
"""

from pathlib import Path

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_bookmark import Favorito
from backend.core.entidades.entidade_diretorio import ModeloPasta
from backend.core.entidades.entidade_sistema_operacional import (
    ModeloSistemaOperacional,
)


def cli_exibir_sistema_operacional(so: ModeloSistemaOperacional) -> None:
    """Exibe informações do sistema operacional usando o modelo de domínio."""
    a: str = str(so.nome_sistema)
    b: str = str(so.versao_sistema)
    c: str = str(so.pasta_usuario)
    print(f"🖥️  Sistema: {a} | " + f"Versão: {b} | " + f"Home: {c}")


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
    pai_nome: str = pasta_pai.nome_pasta if pasta_pai else "(raiz)"
    print(f"   Pasta pai: {pai_nome}")
    print(f"   Subpastas: {len(subpastas)} | Arquivos: {len(subarquivos)}")


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
    arquivo: str = f"Arquivo: {nome_arquivo}"
    caminho: str = f"Caminho: {caminho_arquivo}"
    tamanho: str = f"Tamanho: {tamanho_arquivo} bytes"
    print(f"📄 {arquivo} | {caminho} | {tamanho} | HTML: {html}")


def cli_exibir_estatisticas(
    estatisticas: dict[str, int] | None = None, *, stats: dict[str, int] | None = None
) -> None:
    """Exibe estatísticas do processamento de favoritos."""
    dados_estatisticas: dict[str, int] = estatisticas or stats or {}
    print("\n📊 Estatísticas do processamento:")
    for chave, valor in dados_estatisticas.items():
        print(f"   {chave}: {valor}")


def cli_exibir_favoritos(favoritos: list[Favorito], limite: int = 5) -> None:
    """Exibe os primeiros favoritos encontrados.

    Args:
        favoritos: Lista de favoritos.
        limite: Quantos favoritos exibir.
    """
    if not favoritos:
        print("Nenhum favorito encontrado.")
        return

    print(f"\n🔖 Exibindo os primeiros {min(limite, len(favoritos))} favoritos:")
    for indice, favorito in enumerate(favoritos[:limite], start=1):
        print(f"   {indice}. {favorito.titulo}")
        print(f"      URL: {favorito.url}")
        if favorito.data_adicao:
            print(
                f"      Adicionado em: {favorito.data_adicao.strftime(format='%Y-%m-%d %H:%M:%S')}"
            )
        print()


def cli_exibir_bookmarks(bookmarks: list[Favorito], limite: int = 5) -> None:
    """Alias de compatibilidade para `cli_exibir_favoritos`."""
    cli_exibir_favoritos(favoritos=bookmarks, limite=limite)
