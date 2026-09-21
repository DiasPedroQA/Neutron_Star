# src/dominio/entidades.py

"""Entidades centrais do domínio e tipos estruturados do Neutron Star.

Este módulo não pode depender de frameworks (Flask, pydantic, etc.) —
os contratos HTTP (DTOs de request/response) ficam em adaptadores/schemas.py.

.. module:: src.dominio.entidades
   :platform: Unix, Windows
   :synopsis: Entidades de domínio e TypedDicts de tipagem estática.

Contém:
- ``Favorito``: entidade imutável de um link de favorito.
- ``FavoritoDict``: forma serializada de ``Favorito``.
- ``MetadadosArquivo``: informações de um arquivo HTML encontrado.
- ``ResultadoEscaneamento``: resultado completo de uma varredura.
- ``StatusConversao`` / ``ArquivoConvertido`` / ``ErroConversao``:
  estado do processamento em lote (streaming SSE).
- ``InfoSistema`` / ``AtalhoSugerido``: metadados do SO hospedeiro.
"""

from dataclasses import dataclass
from typing import TypedDict

# =============================================================================
# Entidade de domínio
# =============================================================================


@dataclass(frozen=True)
class Favorito:
    """Entidade de Domínio Pura.

    Representa o contrato essencial de um link de favorito no ecossistema Neutron Star.
    Como é definida com frozen=True, ela é imutável e thread-safe.
    Todos os campos de texto são normalizados (.strip()) e recebem valores
    padrão caso venham vazios ou com apenas espaços em branco.
    """

    titulo: str = "Sem título"
    url: str = ""
    pasta: str = "Favoritos"
    data_adicao: str = "Sem data"

    def __post_init__(self) -> None:
        """Validações e normalizações de consistência do domínio."""
        if not self.url or not self.url.strip():
            raise ValueError("Um favorito precisa obrigatoriamente conter uma URL válida.")

        # Normalização de atributos em dataclass imutável (frozen=True)
        object.__setattr__(self, "url", self.url.strip())
        object.__setattr__(
            self,
            "titulo",
            self.titulo.strip() if self.titulo and self.titulo.strip() else "Sem título",
        )
        object.__setattr__(
            self,
            "pasta",
            self.pasta.strip() if self.pasta and self.pasta.strip() else "Favoritos",
        )
        object.__setattr__(
            self,
            "data_adicao",
            self.data_adicao.strip()
            if self.data_adicao and self.data_adicao.strip()
            else "Sem data",
        )

    def to_dict(self) -> dict[str, str]:
        """Converte a entidade de domínio em um dicionário serializável padrão."""
        return {
            "Titulo": self.titulo,
            "URL": self.url,
            "Pasta": self.pasta,
            "Data_Adicao": self.data_adicao,
        }


# =============================================================================
# Tipos estruturados (TypedDict)
# =============================================================================


class MetadadosArquivo(TypedDict):
    """Metadados de um arquivo HTML encontrado no escaneamento.

    Attributes:
        nome (str): Nome do arquivo (ex: "bookmarks.html").
        caminho_completo (str): Caminho absoluto completo do arquivo.
        tamanho_kb (float): Tamanho do arquivo em kilobytes (com 2 casas decimais).
        modificado_em (str): Timestamp da última modificação (formato: dd/mm/yyyy HH:MM:SS).
        selecionado (bool): Flag indicando se o arquivo foi selecionado para conversão.

    Example:
        >>> arquivo: MetadadosArquivo = {
        ...     "nome": "bookmarks.html",
        ...     "caminho_completo": "/home/usuario/bookmarks.html",
        ...     "tamanho_kb": 245.67,
        ...     "modificado_em": "25/09/2026 14:30:00",
        ...     "selecionado": True
        ... }
    """

    nome: str
    caminho_completo: str
    tamanho_kb: float
    modificado_em: str
    selecionado: bool
    elegivel: bool


class FavoritoDict(TypedDict):
    """Dicionário serializado de um favorito (link).

    Attributes:
        Titulo (str): Título/texto exibido do link (vazio → "Sem título").
        URL (str): Endereço web do favorito (sempre presente, nunca vazio).
        Pasta (str): Caminho hierárquico de pastas (ex: "Favoritos / Trabalho / Python").
        Data_Adicao (str): Data e hora da adição (formato: dd/mm/yyyy HH:MM:SS ou "Sem data").

    Note:
        As chaves usam PascalCase por compatibilidade com exportação Excel/CSV.

    Example:
        >>> favorito: FavoritoDict = {
        ...     "Titulo": "Python Docs",
        ...     "URL": "https://docs.python.org",
        ...     "Pasta": "Favoritos / Desenvolvimento",
        ...     "Data_Adicao": "15/08/2026 10:45:00"
        ... }
    """

    Titulo: str
    URL: str
    Pasta: str
    Data_Adicao: str


class ArquivoConvertido(TypedDict):
    """Informações sobre um arquivo que foi convertido com sucesso.

    Attributes:
        origem (str): Nome do arquivo HTML original.
        destino (str): Nome do arquivo de saída (CSV ou JSON).
        total_links (int): Quantidade de favoritos extraídos.

    Example:
        >>> arquivo_ok: ArquivoConvertido = {
        ...     "origem": "bookmarks.html",
        ...     "destino": "bookmarks_processado.json",
        ...     "total_links": 42
        ... }
    """

    origem: str
    destino: str
    total_links: int


class ErroConversao(TypedDict):
    """Informações sobre um erro durante a conversão de um arquivo.

    Attributes:
        arquivo (str): Nome do arquivo que falhou.
        erro (str): Mensagem descritiva do erro ocorrido.

    Example:
        >>> erro: ErroConversao = {
        ...     "arquivo": "corrupted.html",
        ...     "erro": "Falha na leitura: Arquivo inacessível ou corrompido"
        ... }
    """

    arquivo: str
    erro: str


class StatusConversao(TypedDict):
    """Estado atual do processamento de um lote de conversão.

    Utilizado para streaming de progresso em tempo real (Server-Sent Events).

    Attributes:
        progresso (int): Percentual de conclusão (0-100).
        arquivo_atual (str): Nome do arquivo sendo processado agora.
        concluido (bool): True se o processamento terminou (último pacote).
        sucesso (bool): True se pelo menos um arquivo foi convertido com sucesso.
        arquivos_convertidos (list[ArquivoConvertido]): Lista de sucessos até o momento.
        erros (list[ErroConversao]): Lista de falhas até o momento.

    Example:
        >>> status: StatusConversao = {
        ...     "progresso": 50,
        ...     "arquivo_atual": "bookmarks2.html",
        ...     "concluido": False,
        ...     "sucesso": True,
        ...     "arquivos_convertidos": [
        ...         {
        ...             "origem": "bookmarks1.html",
        ...             "destino": "bookmarks1_processado.json",
        ...             "total_links": 30
        ...         }
        ...     ],
        ...     "erros": []
        ... }
    """

    progresso: int
    arquivo_atual: str
    concluido: bool
    sucesso: bool
    arquivos_convertidos: list[ArquivoConvertido]
    erros: list[ErroConversao]


class AtalhoSugerido(TypedDict):
    """Atalho de navegação rápida sugerido ao usuário.

    Attributes:
        label (str): Descrição amigável do atalho (ex: "Documentos (~Documents)").
        caminho (str): Caminho relativo à home (ex: "~/Documents") ou token "custom".

    Example:
        >>> atalho: AtalhoSugerido = {
        ...     "label": "Downloads (~Downloads)",
        ...     "caminho": "~/Downloads"
        ... }
    """

    label: str
    caminho: str


class InfoSistema(TypedDict):
    """Informações coletadas do sistema operacional.

    Attributes:
        so (str): Nome e versão do sistema operacional (ex: "Linux (5.10.0)").
        usuario (str): Nome do usuário logado (ex: "pedro").
        pasta_home (str): Caminho absoluto da pasta home (/home/pedro).
        atalhos_sugeridos (list[AtalhoSugerido]): Pastas recomendadas para navegação ágil.

    Example:
        >>> info_so: InfoSistema = {
        ...     "so": "Linux (5.10.0)",
        ...     "usuario": "pedro",
        ...     "pasta_home": "/home/pedro",
        ...     "atalhos_sugeridos": [
        ...         {"label": "Pasta Home (~/)", "caminho": "~/"},
        ...         {"label": "Documentos (~Documents)", "caminho": "~/Documents"}
        ...     ]
        ... }
    """

    so: str
    usuario: str
    pasta_home: str
    atalhos_sugeridos: list[AtalhoSugerido]


class NoArvore(TypedDict, total=False):
    """Nó hierárquico da árvore de estrutura encontrada.

    Attributes:
        type (str): "folder" ou "file".
        name (str): nome do nó (sem barra).
        path (str): caminho relativo à raiz varrida.
        size_kb (float): tamanho em KB (só para type="file").
        elegivel (bool): se é um bookmark Netscape elegível (só para type="file").
        children (list[NoArvore]): subnós (só para type="folder").
    """

    type: str
    name: str
    path: str
    size_kb: float
    elegivel: bool
    children: list["NoArvore"]


class ResultadoEscaneamento(TypedDict):
    """Resultado completo da varredura de um diretório em busca de HTMLs.

    Attributes:
        caminho_varrido (str): Caminho absoluto que foi escaneado.
        total_arquivos (int): Quantidade de arquivos HTML/HTM encontrados.
        tamanho_total_mb (float): Soma total de tamanhos em megabytes.
        data_busca (str): Timestamp de quando a busca foi realizada.
        arquivos (list[MetadadosArquivo]): Lista de metadados dos arquivos encontrados.

    Example:
        >>> resultado: ResultadoEscaneamento = {
        ...     "caminho_varrido": "/home/pedro/Documents",
        ...     "total_arquivos": 3,
        ...     "tamanho_total_mb": 2.45,
        ...     "data_busca": "25/09/2026 14:30:00",
        ...     "arquivos": [
        ...         {
        ...             "nome": "bookmarks.html",
        ...             "caminho_completo": "/home/pedro/Documents/bookmarks.html",
        ...             "tamanho_kb": 1024.5,
        ...             "modificado_em": "20/09/2026 10:00:00",
        ...             "selecionado": True
        ...         }
        ...     ]
        ... }
    """

    caminho_varrido: str
    extensao_usada: str
    profundidade_usada: int
    total_arquivos: int
    total_elegiveis: int
    tamanho_total_mb: float
    data_busca: str
    arquivos: list[MetadadosArquivo]
    tree: list[NoArvore]
