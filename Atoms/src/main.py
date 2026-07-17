"""
Módulo de busca de arquivos e extração de bookmarks (HTML).

Oferece funções puras de filtragem, pipeline de busca, parser de
arquivos Netscape Bookmark e exportadores para JSON, CSV, TXT e PDF.

Uso como biblioteca:
    from atoms import buscar_arquivos, parse_bookmarks_html, exportar_bookmarks
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from aplicacao.casos_de_uso.busca_arquivos import buscar_arquivos
from aplicacao.casos_de_uso.exportar_bookmarks import EXPORTADORES, exportar_bookmarks
from aplicacao.casos_de_uso.parse_bookmarks import parse_bookmarks_html
from dominio.entidades import BookmarkFolder
from dominio.excecoes import ErroBookmarks, NenhumDiretorioValidoError
from infraestrutura.sistema_arquivos import confirmar_dados_entrada, ler_arquivo_html

# =============================================================================
# DEMONSTRAÇÕES (opções de inicialização para o main())
# =============================================================================


def demo_busca_simples() -> None:
    """Opção 1: busca por extensão + palavras-chave, sem exigir data no nome."""
    print("=== [1] Busca simples ===")
    diretorios: list[Path] = confirmar_dados_entrada(caminhos=["~"])
    for pasta in diretorios:
        resultados: list[Path] = buscar_arquivos(pasta=pasta, extensao=".html", chaves=["bookmarks"])
        print(f"Encontrados {len(resultados)} arquivo(s) em {pasta}")
        for arquivo in resultados:
            print(f"Arquivo: {arquivo}")


def demo_busca_com_data() -> None:
    """Opção 2: busca exigindo data no nome do arquivo (padrão US ou BR)."""
    print("=== [2] Busca exigindo data no nome ===")
    diretorios: list[Path] = confirmar_dados_entrada(caminhos=["~"])
    for pasta in diretorios:
        resultados: list[Path] = buscar_arquivos(pasta=pasta, extensao=".html", chaves=["bookmarks"], exigir_data=True)
        print(f"Encontrados {len(resultados)} arquivo(s) com data em {pasta}")
        for arquivo in resultados:
            print(f"Arquivo: {arquivo}")


def demo_extracao_bookmarks(arquivo: Path = Path("bookmarks.html")) -> None:
    """Opção 3: extrai bookmarks de um arquivo HTML fixo e mostra prévia em JSON."""
    print("=== [3] Extração de bookmarks ===")
    if not arquivo.exists():
        print(f"Arquivo '{arquivo}' não encontrado, pulando.")
        return
    try:
        conteudo: str = ler_arquivo_html(caminho=arquivo)
        raiz: BookmarkFolder = parse_bookmarks_html(conteudo_html=conteudo)
        if json_str := exportar_bookmarks(raiz=raiz, formato=".json"):
            preview: str = json_str[:500] + ("..." if len(json_str) > 500 else "")
            print(f"Pré-visualização JSON:\n{preview}")
    except ErroBookmarks as exc:
        print(f"Erro: {exc}")


def demo_exportacao_multipla(arquivo: Path = Path("bookmarks.html")) -> None:
    """Opção 4: extrai bookmarks e exporta em todos os formatos disponíveis."""
    print("=== [4] Exportação em todos os formatos ===")
    if not arquivo.exists():
        print(f"Arquivo '{arquivo}' não encontrado, pulando.")
        return
    try:
        conteudo: str = ler_arquivo_html(caminho=arquivo)
        raiz: BookmarkFolder = parse_bookmarks_html(conteudo_html=conteudo)
        for formato in EXPORTADORES:
            saida = Path(f"bookmarks{formato}")
            exportar_bookmarks(raiz=raiz, formato=formato, caminho_saida=saida)
            print(f"Exportado: {saida}")
    except ErroBookmarks as exc:
        print(f"Erro: {exc}")


# =============================================================================


MODOS_DISPONIVEIS: dict[str, Callable[[], None]] = {
    "busca_simples": demo_busca_simples,
    "busca_com_data": demo_busca_com_data,
    "extracao_bookmarks": demo_extracao_bookmarks,
    "exportacao_multipla": demo_exportacao_multipla,
}

# Troque aqui quais demonstrações rodar (uma, várias ou todas).
MODOS_ATIVOS: list[str] = ["busca_simples", "extracao_bookmarks"]

# =============================================================================


def main() -> None:
    """Ponto de entrada: lista as opções disponíveis e roda as ativas.

    Todas as opções de inicialização ficam visíveis em MODOS_DISPONIVEIS;
    para trocar o que roda, edite a lista MODOS_ATIVOS acima.
    """
    print(f"Opções disponíveis: {', '.join(MODOS_DISPONIVEIS)}")
    print(f"Rodando agora: {', '.join(MODOS_ATIVOS)}\n")
    for nome_modo in MODOS_ATIVOS:
        try:
            MODOS_DISPONIVEIS[nome_modo]()
        except NenhumDiretorioValidoError as exc:
            print(exc)
        print()


if __name__ == "__main__":
    main()
