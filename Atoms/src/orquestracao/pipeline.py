"""Pipeline básico de etapas para processamento de bookmarks."""

from collections.abc import Callable

from aplicacao.etapas import (
    etapa_buscar,
    etapa_exportar,
    etapa_extrair,
    etapa_selecionar_arquivo,
)
from aplicacao.tipos import ParametrosBusca
from dominio.excecoes import ErroBookmarks

# Mapeamento de nomes de etapas para funções
ETAPAS_DISPONIVEIS: dict[str, Callable[[ParametrosBusca], ParametrosBusca]] = {
    "buscar": etapa_buscar,
    "selecionar_arquivo": etapa_selecionar_arquivo,
    "extrair": etapa_extrair,
    "exportar": etapa_exportar,
}


def executar_pipeline_basico(
    contexto: ParametrosBusca,
) -> ParametrosBusca:
    """
    Executa uma lista de etapas em sequência.

    Args:
        contexto: Contexto inicial.
        etapas: Nomes das etapas a executar.

    Returns:
        Contexto final após todas as etapas.

    Raises:
        ErroBookmarks: Se alguma etapa falhar.
        ValueError: Se ocorrer erro de validação.
    """
    for nome, acao in ETAPAS_DISPONIVEIS.items():
        etapa: Callable[[ParametrosBusca], ParametrosBusca] | None = acao
        if etapa is None:
            print(f"Etapa '{nome}' desconhecida - ignorada.")
            continue
        try:
            contexto = etapa(contexto)
        except (ErroBookmarks, ValueError) as e:
            print(f"Erro na etapa '{nome}': {e}")
            raise
    return contexto
