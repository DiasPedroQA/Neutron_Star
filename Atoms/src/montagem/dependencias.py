# Atoms/dependencias.py

"""Configuração de dependências (injeção simples)."""

from aplicacao.casos_uso import BuscarEExtrairTags, ExtrairTags, ListarArquivos
from infra.buscador import PastaBuscadora
from infra.leitor import LeitorArquivoHTML


async def obter_listar_arquivos() -> ListarArquivos:
    """Fábrica para ListarArquivos com PastaBuscadora."""
    buscador = PastaBuscadora(incluir_ocultos=False, excluir_privados=True)
    return ListarArquivos(diretorio=buscador)


async def obter_extrair_tags() -> ExtrairTags:
    """Fábrica para ExtrairTags com LeitorArquivoHTML."""
    leitor = LeitorArquivoHTML()
    return ExtrairTags(leitor=leitor)


async def obter_buscar_e_extrair() -> BuscarEExtrairTags:
    """Fábrica para BuscarEExtrairTags com PastaBuscadora e LeitorArquivoHTML."""
    diretorio = PastaBuscadora(incluir_ocultos=False, excluir_privados=True)
    leitor = LeitorArquivoHTML()
    return BuscarEExtrairTags(diretorio=diretorio, leitor=leitor)
