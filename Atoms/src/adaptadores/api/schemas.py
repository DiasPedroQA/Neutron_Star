"""Esquemas de entrada/saída da API HTTP de bookmarks.

Ficam isolados dos modelos de domínio (TagA, VirtualFolder) de propósito:
são um contrato de transporte HTTP, não a modelagem do problema. Se o
formato da API mudar amanhã, o domínio não precisa mudar junto.
"""

from pydantic import BaseModel, Field


class RequisicaoBusca(BaseModel):
    """Parâmetros para buscar arquivos de bookmarks em um diretório."""

    diretorio: str = Field(description="Diretório onde buscar os arquivos.")


class RespostaBusca(BaseModel):
    """Arquivos encontrados por uma busca."""

    arquivos_encontrados: list[str]


class RequisicaoProcessarLote(BaseModel):
    """Parâmetros para processar um conjunto de arquivos de bookmarks."""

    arquivos: list[str] = Field(description="Caminhos dos arquivos HTML de bookmarks a processar.")
    formatos: list[str] = Field(description="Formatos de exportação desejados (ex.: ['.json', '.md']).")
    diretorio_saida: str | None = Field(
        default=None, description="Diretório de saída; se ausente, exporta ao lado de cada original."
    )


class RespostaProcessarLote(BaseModel):
    """Resultado do processamento em lote: quantos deram certo e quais falharam."""

    total: int
    sucesso: int
    falhas: dict[str, str]
