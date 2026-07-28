# Simplified pipeline runner that accepts uma lista de etapas (sequência de chaves)
from typing import Callable, Dict, Iterable, List, Optional

ETAPAS_DISPONIVEIS: Dict[str, Callable[..., object]] = {}


def registrar_etapa(nome: str):
    def decorator(fn: Callable[..., object]):
        ETAPAS_DISPONIVEIS[nome] = fn
        return fn

    return decorator


def executar_etapas(etapas: Optional[Iterable[str]] = None, *args, **kwargs):
    """
    Executa as etapas na ordem fornecida em 'etapas'.
    - se etapas for None, executa todas as etapas na ordem definida por ETAPAS_DISPONIVEIS.keys()
    - ignora nomes não registrados e retorna um dict de resultados por etapa
    """
    seq: List[str] = list(etapas) if etapas is not None else list(ETAPAS_DISPONIVEIS.keys())
    resultados = {}
    for nome in seq:
        fn = ETAPAS_DISPONIVEIS.get(nome)
        if fn is None:
            # etapa desconhecida — ignora silenciosamente, pode-se ajustar para log/raise
            continue
        resultados[nome] = fn(*args, **kwargs)
    return resultados
