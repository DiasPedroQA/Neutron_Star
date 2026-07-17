# aplicacao/etapas.py
"""Etapas de alto nível do pipeline de processamento de bookmarks.

Define funções de etapa que recebem e devolvem um contexto mutável,
encadeando busca de arquivos, seleção, extração de favoritos e exportação em formatos diversos.
"""

from pathlib import Path

from dominio.entidades import BookmarkFolder
from infraestrutura.sistema_arquivos import (
    confirmar_dados_entrada,
    ler_arquivo_html,
)

from aplicacao.casos_de_uso.busca_arquivos import buscar_arquivos
from aplicacao.casos_de_uso.exportar_bookmarks import (
    exportar_bookmarks,
)
from aplicacao.casos_de_uso.parse_bookmarks import (
    parse_bookmarks_html,
)


def etapa_busca(ctx: dict) -> dict:
    """Busca arquivos conforme parâmetros em ctx e armazena o resultado."""
    diretorios: list[Path] = [Path(d) for d in ctx.get("dirs", ["."])]
    extensao = ctx.get("extensao", ".html")
    chaves = ctx.get("chaves", [])
    exigir_data = ctx.get("exigir_data", False)

    validos: list[Path] = confirmar_dados_entrada([str(d) for d in diretorios])
    todos_arquivos = []
    for pasta in validos:
        todos_arquivos.extend(buscar_arquivos(pasta=pasta, extensao=extensao, chaves=chaves, exigir_data=exigir_data))

    ctx["arquivos_encontrados"] = todos_arquivos
    print(f"Busca concluída: {len(todos_arquivos)} arquivo(s) encontrado(s).")
    return ctx


def etapa_selecionar_arquivo(ctx: dict) -> dict:
    """Seleciona um arquivo da lista (por índice) para a extração."""
    arquivos = ctx.get("arquivos_encontrados", [])
    indice = ctx.get("indice_arquivo", 0)
    if not arquivos:
        raise ValueError("Nenhum arquivo disponível para seleção.")
    if indice >= len(arquivos):
        indice = 0  # fallback seguro
    ctx["arquivo_selecionado"] = arquivos[indice]
    print(f"Arquivo selecionado: {arquivos[indice]}")
    return ctx


def etapa_extrair(ctx: dict) -> dict:
    """Extrai bookmarks do arquivo selecionado e guarda a raiz."""
    arquivo = ctx["arquivo_selecionado"]
    conteudo: str = ler_arquivo_html(caminho=arquivo)
    raiz: BookmarkFolder = parse_bookmarks_html(conteudo_html=conteudo)
    ctx["raiz_bookmarks"] = raiz
    print("Extração concluída.")
    return ctx


def etapa_exportar(ctx: dict) -> dict:
    """Exporta a raiz para os formatos especificados."""
    raiz = ctx["raiz_bookmarks"]
    formatos = ctx.get("formatos_exportacao", [".json"])
    dir_saida = Path(ctx.get("diretorio_saida", "."))
    dir_saida.mkdir(parents=True, exist_ok=True)
    for fmt in formatos:
        caminho: Path = dir_saida / f"bookmarks{fmt}"
        exportar_bookmarks(raiz=raiz, formato=fmt, caminho_saida=caminho)
        print(f"Exportado: {caminho}")
    return ctx
