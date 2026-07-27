"""Pipeline com execução condicional de etapas."""

from collections.abc import Callable

from aplicacao.tipos import ParametrosBusca
from dominio.excecoes import ErroBookmarks

from orquestracao.pipeline import ETAPAS_DISPONIVEIS


def executar_pipeline_condicional(
    contexto: ParametrosBusca,
) -> ParametrosBusca:
    """
    Executa etapas com condições (callable que retorna True/False).

    Args:
        contexto: Contexto inicial.
        etapas: Lista de tuplas (nome_da_etapa, condicao).
                Se condicao for None, executa sempre.

    Returns:
        Contexto final após as etapas executadas.

    Exemplo:
        etapas = [
            ("buscar", None),
            ("selecionar_arquivo", lambda c: len(c.get("arquivos_encontrados", [])) > 0),
            ("extrair", lambda c: c.get("arquivo_selecionado") is not None),
        ]
    """
    for nome, condicao in ETAPAS_DISPONIVEIS.items():
        if condicao is not None and not condicao(contexto):
            print(f"Pulando etapa '{nome}' (condição não atendida)")
            continue

        etapa: Callable[[ParametrosBusca], ParametrosBusca] | None = ETAPAS_DISPONIVEIS.get(nome)
        if etapa is None:
            print(f"Etapa '{nome}' desconhecida - ignorada.")
            continue

        try:
            contexto = etapa(contexto)
        except (ErroBookmarks, ValueError) as e:
            print(f"Erro na etapa '{nome}': {e}")
            raise

    return contexto
