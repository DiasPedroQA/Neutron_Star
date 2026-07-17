# main.py
"""
Módulo de busca de arquivos e extração de bookmarks (HTML).

Oferece funções puras de filtragem, pipeline de busca, parser de
arquivos Netscape Bookmark e exportadores para JSON, CSV, TXT e PDF.

Uso como biblioteca:
    from atoms import buscar_arquivos, parse_bookmarks_html, exportar_bookmarks
"""

from __future__ import annotations

from collections.abc import Callable  # Python 3.11+

import tomllib
from aplicacao.etapas import (
    etapa_busca,
    etapa_exportar,
    etapa_extrair,
    etapa_selecionar_arquivo,
)
from dominio.excecoes import ErroBookmarks

# Mapeia nomes de etapas para as funções
MAPEAMENTO_ETAPAS: dict[str, Callable[[dict], dict]] = {
    "busca": etapa_busca,
    "extrair": etapa_extrair,
    "exportar": etapa_exportar,
    "selecionar_arquivo": etapa_selecionar_arquivo,
}


def carregar_config(caminho: str) -> dict:
    """Carrega a configuração da aplicação a partir de um arquivo TOML.
    Retorna um dicionário com os dados estruturados para uso no pipeline.

    A função lê o arquivo em disco no caminho informado, interpreta seu conteúdo
    como TOML e expõe as configurações em forma de estrutura Python.

    Args:
        caminho: Caminho para o arquivo de configuração TOML.

    Returns:
        Dicionário contendo as configurações carregadas do arquivo.
    """
    with open(caminho, "rb") as f:
        return tomllib.load(f)


def executar_pipeline(config: dict) -> None:
    """Executa o pipeline de etapas configurado em um arquivo de configuração.
    Coordena a passagem de um contexto entre etapas nomeadas, tratando erros de forma controlada.

    A função lê a lista de etapas ativas, inicializa o contexto com parâmetros
    globais e aplica cada função de etapa em sequência, interrompendo o fluxo em caso de falha.

    Args:
        config: Dicionário de configuração contendo a seção 'pipeline' com nomes de etapas e,
        opcionalmente, 'parametros' iniciais.

    Returns:
        None. A função atua pelos efeitos colaterais das etapas executadas (como I/O e logs).
    """
    etapas_nomes = config["pipeline"]["etapas"]
    parametros = config.get("parametros", {})
    ctx = dict(parametros)  # inicia o contexto com os parâmetros

    for nome in etapas_nomes:
        etapa_func = MAPEAMENTO_ETAPAS.get(nome)
        if etapa_func is None:
            print(f"Etapa desconhecida: '{nome}'")
            continue
        try:
            ctx = etapa_func(ctx)
        except (ErroBookmarks, ValueError) as e:
            print(f"Erro na etapa '{nome}': {e}")
            break


def main() -> None:
    """Função principal da aplicação de bookmarks.
    Carrega a configuração externa e dispara a execução coordenada do pipeline de etapas.

    A função delega a leitura do arquivo de configuração e à função de
    pipeline, atuando como ponto de entrada simples do programa.

    Returns:
        None. A aplicação é conduzida pelos efeitos colaterais das etapas configuradas.
    """
    config = carregar_config(caminho="pyproject.toml")
    executar_pipeline(config=config)


if __name__ == "__main__":
    main()
