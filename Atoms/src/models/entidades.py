# Atoms/src/models/entidades.py

"""Definição de entidades e estruturas de dados de transporte (TypedDicts)."""

from dataclasses import dataclass
from typing import Any, TypedDict

FORMATOS_SAIDA: frozenset[str] = frozenset({"csv", "json", "md", "markdown"})


@dataclass(frozen=True, slots=True)
class Favorito:
    """Entidade que representa um favorito extraído do HTML."""

    titulo: str
    url: str
    pasta: str = "Favoritos"
    data_adicao: str = "Sem data"


class FavoritoDict(TypedDict):
    """Representação em dicionário serializável de um Favorito."""

    titulo: str
    url: str
    pasta: str
    data_adicao: str


class ArquivoConvertido(TypedDict):
    """Dados de um arquivo convertido com sucesso."""

    arquivo_origem: str
    arquivo_destino: str
    total_links: int


class ErroConversao(TypedDict):
    """Dados de falha de conversão de um arquivo."""

    arquivo: str
    erro: str


class StatusConversao(TypedDict):
    """Estado de progresso emitido durante a conversão em lote."""

    progresso: int
    arquivo_atual: str
    arquivos_convertidos: list[ArquivoConvertido]
    erros: list[ErroConversao]
    concluido: bool
    sucesso: bool


class AtalhoSugerido(TypedDict):
    """Atalho rápido para navegação no sistema."""

    label: str
    caminho: str


class InfoSistema(TypedDict):
    """Informações do ambiente operacional do usuário."""

    so: str
    usuario: str
    pasta_home: str
    atalhos_sugeridos: list[AtalhoSugerido]


class MetadadosArquivo(TypedDict):
    """Metadados de um arquivo HTML identificado."""

    nome: str
    caminho_completo: str
    tamanho_kb: float
    modificado_em: str
    selecionado: bool
    elegivel: bool


class NoArvore(TypedDict, total=False):
    """Nó da árvore hierárquica de arquivos e pastas."""

    type: str
    name: str
    path: str
    size_kb: float
    elegivel: bool
    children: list[Any]


class ResultadoEscaneamento(TypedDict):
    """Resultado consolidado da varredura de diretório."""

    caminho_varrido: str
    extensao_usada: str
    profundidade_usada: int
    total_arquivos: int
    total_elegiveis: int
    tamanho_total_mb: float
    data_busca: str
    arquivos: list[MetadadosArquivo]
    tree: list[NoArvore]
