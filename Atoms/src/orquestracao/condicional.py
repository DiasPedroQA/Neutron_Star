from typing import Callable, Dict, Iterable, Any, Optional

# Exemplo: ETAPAS_DISPONIVEIS = {'buscar': buscar_fn, 'extrair': extrair_fn}
ETAPAS_DISPONIVEIS: Dict[str, Callable[..., Any]] = {}


def executar_condicional(condicoes: Dict[str, Callable[[], bool]],
                         etapas: Optional[Iterable[str]] = None,
                         *args, **kwargs):
    """
    condicoes: dict[etapa_nome] -> predicate() -> bool
    etapas: lista opcional de nomes a considerar; se None, considerar todas as chaves de condicoes
    Retorna dict com resultados das etapas executadas.
    """
    seq = list(etapas) if etapas is not None else list(condicoes.keys())
    resultados = {}
    for nome in seq:
        pred = condicoes.get(nome)
        if pred is None:
            continue
        try:
            should_run = bool(pred())
        except Exception:
            should_run = False
        if should_run:
            fn = ETAPAS_DISPONIVEIS.get(nome)
            if fn is None:
                continue
            resultados[nome] = fn(*args, **kwargs)
    return resultados
