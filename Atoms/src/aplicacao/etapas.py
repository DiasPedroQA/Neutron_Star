# aplicacao/etapas.py
"""Etapas de alto nível do filtro de processamento de bookmarks.

Define funções de etapa que recebem e devolvem um contexto mutável,
encadeando busca de arquivos, seleção, extração de favoritos e exportação em formatos diversos.
"""

from pathlib import Path

from dominio.entidades import VirtualFolder
from infraestrutura.sistema_arquivos import confirmar_dados_entrada, ler_arquivo_html

from aplicacao.casos_de_uso.busca_arquivos import buscar_arquivos
from aplicacao.casos_de_uso.exportar_bookmarks import exportar_bookmarks
from aplicacao.casos_de_uso.parse_bookmarks import parse_bookmarks_html
from aplicacao.tipos import ParametrosBusca


def etapa_buscar(contexto_busca: ParametrosBusca) -> ParametrosBusca:
    """Executa a etapa de busca de arquivos de bookmarks no pipeline.
    Atualiza o contexto com a lista de arquivos encontrados de acordo com os filtros configurados.

    Args:
        contexto_busca: Contexto mutável contendo diretórios,
        extensão, chaves e demais parâmetros de busca.

    Returns:
        ParametrosBusca: O mesmo contexto recebido, enriquecido com a chave "arquivos_encontrados".
    """
    extensao: str = contexto_busca.get("extensao", ".html")
    chaves: list[str] = contexto_busca.get("chaves", [])
    exigir_data: bool = contexto_busca.get("exigir_data", False)
    diretorio: Path = contexto_busca.get("diretorio", Path.home())

    validos: list[Path] = confirmar_dados_entrada(caminhos=diretorio)
    todos_arquivos: list[Path] = []
    for pasta in validos:
        todos_arquivos.extend(buscar_arquivos(pasta=pasta, extensao=extensao, chaves=chaves, exigir_data=exigir_data))

    contexto_busca["arquivos_encontrados"] = todos_arquivos
    print(f"Busca concluída: {len(todos_arquivos)} arquivo(s) encontrado(s).")
    return contexto_busca


def etapa_selecionar_arquivo(contexto_busca: ParametrosBusca) -> ParametrosBusca:
    """Executa a etapa de seleção de um arquivo de bookmarks no pipeline.
    Escolhe um arquivo da lista encontrada anteriormente
    e atualiza o contexto com o arquivo escolhido.

    Args:
        contexto_busca: Contexto mutável contendo os arquivos encontrados
        e o índice desejado para seleção.

    Returns:
        ParametrosBusca: O mesmo contexto recebido, enriquecido com a chave "arquivo_selecionado".

    Raises:
        ValueError: Se não houver arquivos encontrados para seleção.
    """
    arquivos: list[Path] = contexto_busca.get("arquivos_encontrados", [])
    if not arquivos:
        raise ValueError("Nenhum arquivo encontrado para seleção.")

    indice: int = contexto_busca.get("indice_arquivo", 0)
    if not 0 <= indice < len(arquivos):
        indice = 0

    contexto_busca["arquivo_selecionado"] = arquivos[indice]
    return contexto_busca


def etapa_extrair(contexto_busca: ParametrosBusca) -> ParametrosBusca:
    """Executa a etapa de extração da estrutura de bookmarks a partir do arquivo HTML.
    Lê o conteúdo do arquivo selecionado, interpreta as tags de favoritos
    e atualiza o contexto com a raiz de bookmarks.

    Args:
        contexto_busca: Contexto mutável contendo o arquivo selecionado
        e demais parâmetros necessários à extração.

    Returns:
        ParametrosBusca: O mesmo contexto recebido,
        enriquecido com a chave "raiz_bookmarks".
    """
    arquivo: Path = contexto_busca.get("arquivo_selecionado", Path())
    conteudo: str = ler_arquivo_html(caminho=arquivo)
    raiz: VirtualFolder = parse_bookmarks_html(conteudo_html=conteudo)
    contexto_busca["raiz_bookmarks"] = raiz
    print("Extração concluída.")
    return contexto_busca


def etapa_exportar(contexto_busca: ParametrosBusca) -> ParametrosBusca:
    """Executa a etapa de exportação dos bookmarks em formatos diversos.
    Gera arquivos de saída a partir da estrutura de bookmarks
    e atualiza o contexto com o estado final do processo.

    Args:
        contexto_busca: Contexto mutável contendo a raiz de bookmarks,
        formatos desejados e diretório de saída.

    Returns:
        ParametrosBusca: O mesmo contexto recebido, após a criação dos arquivos exportados.

    Raises:
        ValueError: Se não houver raiz de bookmarks disponível.
    """
    raiz: VirtualFolder | None = contexto_busca.get("raiz_bookmarks")
    if raiz is None:
        raise ValueError("Nenhuma raiz de bookmarks disponível para exportação.")

    formatos: list[str] = contexto_busca.get("formatos_exportacao", [".json"])
    dir_saida: Path = Path(contexto_busca.get("diretorio_saida", "."))
    dir_saida.mkdir(parents=True, exist_ok=True)
    for fmt in formatos:
        caminho: Path = dir_saida / f"bookmarks{fmt}"
        exportar_bookmarks(raiz=raiz, formato=fmt, caminho_saida=caminho)
        print(f"Exportado: {caminho}")
    return contexto_busca
