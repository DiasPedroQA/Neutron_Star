"""Definições de tipos estruturados para a aplicação Neutron Star.

.. module:: src.utils.tipos
   :platform: Unix, Windows
   :synopsis: Type hints específicos e TypedDict para validação estática.

Este módulo centraliza todos os tipos customizados da aplicação, permitindo:
- Validação estática de tipos com mypy
- Documentação clara dos contratos de dados
- Detecção precoce de erros de tipo
- Autocompletar mais preciso em IDEs

Tipos principais:
- MetadadosArquivo: Informações sobre um arquivo HTML encontrado
- StatusConversao: Estado da conversão de um lote de favoritos
- FavoritoDict: Dicionário serializado de um favorito
- InfoSistema: Informações coletadas do sistema operacional
- ResultadoEscaneamento: Resultado da varredura de diretório
"""

from typing import TypedDict

__all__ = [
    "MetadadosArquivo",
    "StatusConversao",
    "FavoritoDict",
    "InfoSistema",
    "AtalhoSugerido",
    "ResultadoEscaneamento",
    "ArquivoConvertido",
    "ErroConversao",
]


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
    total_arquivos: int
    tamanho_total_mb: float
    data_busca: str
    arquivos: list[MetadadosArquivo]
