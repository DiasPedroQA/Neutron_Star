"""
Módulo de apresentação de resultados do Neutron Star.

Exibe um ``ResultadoBusca`` no terminal de forma clara e estruturada,
usando ``rich`` se disponível, com fallback para texto puro.
"""

from __future__ import annotations

import importlib
from datetime import datetime
from typing import Any, Final, LiteralString

from rich import box
from rich.console import Console
from rich.table import Table

from src.model.arquivo_info import ItemArquivo
from src.model.diretorio_info import ItemDiretorio
from src.model.item_neutro import ItemBase
from src.model.resultado_busca import ResultadoBusca

# ---------------------------------------------------------------------------
# Constantes de apresentação
# ---------------------------------------------------------------------------
_MAX_ITENS_PADRAO: Final[int] = 100
_LARGURA_SEPARADOR: Final[int] = 70
_SIMBOLO_ARQUIVO: Final[str] = "📄"
_SIMBOLO_PASTA: Final[str] = "📁"
_AVISO_TRUNCADO: Final[str] = "… (lista truncada — use filtros para refinar)"
_TITULO_BUSCA: Final[str] = "🔭 Neutron Star — Resultado da Busca"


# ---------------------------------------------------------------------------
# Funções auxiliares de formatação (não poluem os modelos)
# ---------------------------------------------------------------------------
def _formatar_tamanho(bytes_: int | float | None) -> str:
    """Converte bytes em representação legível (B, KB, MB, GB)."""
    if bytes_ is None:
        return "—"
    for unidade in ("B", "KB", "MB", "GB"):
        if bytes_ < 1024:
            return f"{bytes_:.1f} {unidade}" if unidade != "B" else f"{bytes_} B"
        bytes_ /= 1024
    return f"{bytes_:.1f} TB"


def _formatar_data(dt: datetime | None) -> str:
    """Formata datetime para string amigável."""
    return "—" if dt is None else dt.strftime("%d/%m/%Y %H:%M")


def _formatar_qtd_itens(qtd: int | None) -> str:
    """Retorna 'X itens' ou '—'."""
    return "—" if qtd is None else f"{qtd} itens"


# ---------------------------------------------------------------------------
# Detecção de rich
# ---------------------------------------------------------------------------
def _rich_disponivel() -> bool:
    """Verifica se a biblioteca ``rich`` está instalada."""
    try:
        importlib.import_module("rich")
        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------
class Apresentador:
    """Formata e exibe um ``ResultadoBusca`` no terminal.

    Parâmetros:
        max_itens: Número máximo de itens exibidos na tabela.
        usar_rich: Força uso (ou não) de ``rich``. ``None`` detecta automaticamente.
        nome_so: Nome do sistema operacional para exibir no cabeçalho (opcional).
    """

    def __init__(
        self,
        max_itens: int = _MAX_ITENS_PADRAO,
        usar_rich: bool | None = None,
        nome_so: str | None = None,
    ) -> None:
        self._max_itens: int = max_itens
        self._usar_rich: bool = _rich_disponivel() if usar_rich is None else usar_rich
        self._nome_so: str | None = nome_so

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def exibir(self, resultado: ResultadoBusca) -> None:
        """Imprime o relatório completo do resultado no stdout."""
        if self._usar_rich:
            self._exibir_rich(resultado)
        else:
            self._exibir_texto(resultado)

    def resumo(self, resultado: ResultadoBusca) -> str:
        """Retorna apenas o cabeçalho do relatório como string."""
        raiz = str(resultado.raiz_busca) if resultado.raiz_busca else "?"
        consulta = resultado.consulta or (resultado.criterios.padrao_glob if resultado.criterios else "?")
        return (
            f"Busca '{consulta}' em '{raiz}' → {resultado.total_encontrado} item(ns) em {resultado.tempo_execucao:.2f}s"
        )

    # ------------------------------------------------------------------
    # Modo rich
    # ------------------------------------------------------------------
    def _exibir_rich(self, resultado: ResultadoBusca) -> None:
        """Exibe o relatório com tabelas e cores via ``rich``."""
        console = Console()
        console.print()

        # Título com SO opcional
        titulo = _TITULO_BUSCA
        if self._nome_so:
            titulo += f"  [dim]({self._nome_so})[/dim]"
        console.rule(f"[bold cyan]{titulo}[/bold cyan]")

        # Informações gerais
        raiz = str(resultado.raiz_busca) if resultado.raiz_busca else "?"
        console.print(f"  [dim]Diretório raiz:[/dim]  {raiz}")

        if resultado.criterios:
            self._exibir_criterios_rich(resultado.criterios, console)

        console.print(f"  [dim]Tempo:[/dim]           {resultado.tempo_execucao:.2f}s")
        console.print()

        if resultado.total_encontrado == 0:
            console.print("  [yellow]Nenhum item encontrado.[/yellow]")
            console.rule()
            return

        # Tabela de itens
        tabela = Table(
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
            expand=False,
        )
        tabela.add_column("#", style="dim", width=4, justify="right")
        tabela.add_column("Tipo", width=5, justify="center")
        tabela.add_column("Nome", style="bold")
        tabela.add_column("Tamanho / Itens", justify="right")
        tabela.add_column("Modificado", style="dim")

        itens_exibidos: list[ItemBase] = resultado.itens[: self._max_itens]
        for i, item in enumerate(itens_exibidos, start=1):
            if isinstance(item, ItemArquivo):
                simbolo = _SIMBOLO_ARQUIVO
                detalhe = _formatar_tamanho(item.tamanho)
            else:
                simbolo = _SIMBOLO_PASTA
                detalhe = _formatar_qtd_itens(item.qtd_itens if isinstance(item, ItemDiretorio) else None)
            tabela.add_row(
                str(i),
                simbolo,
                item.nome,
                detalhe,
                _formatar_data(item.modificado),
            )

        console.print(tabela)

        if resultado.total_encontrado > self._max_itens:
            console.print(f"  [yellow]{_AVISO_TRUNCADO}[/yellow]")
            console.print()

        # Rodapé com totais
        arqs: int = sum(isinstance(it, ItemArquivo) for it in resultado.itens)
        pastas: int = resultado.total_encontrado - arqs
        tamanho_total: int = sum(it.tamanho for it in resultado.itens if isinstance(it, ItemArquivo) and it.tamanho)
        console.rule()
        console.print(
            f"  [green]✔[/green] "
            f"[bold]{arqs}[/bold] arquivo(s)  "
            f"[bold]{pastas}[/bold] pasta(s)  │  "
            f"Tamanho total: [bold]{_formatar_tamanho(tamanho_total)}[/bold]"
        )
        console.print()

    def _exibir_criterios_rich(self, criterios: Any, console: Any) -> None:
        """Exibe os critérios da busca no console rich."""
        detalhes = []
        if criterios.consulta:
            detalhes.append(f"consulta='{criterios.consulta}'")
        if criterios.padrao_glob:
            detalhes.append(f"glob='{criterios.padrao_glob}'")
        if criterios.extensoes:
            detalhes.append(f"extensões={criterios.extensoes}")
        if criterios.filtro_nome and criterios.filtro_nome.regex:
            detalhes.append(f"regex nome='{criterios.filtro_nome.regex}'")
        if criterios.filtro_caminho and criterios.filtro_caminho.regex:
            detalhes.append(f"regex caminho='{criterios.filtro_caminho.regex}'")
        if detalhes:
            console.print(f"  [dim]Critérios:[/dim]  {', '.join(detalhes)}")

    # ------------------------------------------------------------------
    # Modo texto puro (fallback)
    # ------------------------------------------------------------------
    def _exibir_texto(self, resultado: ResultadoBusca) -> None:
        """Exibe o relatório em texto puro, sem dependências externas."""
        sep: LiteralString = "─" * _LARGURA_SEPARADOR
        print()

        self._imprimir_cabecalho_texto(sep)
        self._imprimir_info_gerais_texto(resultado, sep)

        if resultado.total_encontrado == 0:
            print("  Nenhum item encontrado.")
            print(sep)
            return

        self._imprimir_itens_texto(resultado)
        self._imprimir_rodape_texto(resultado, sep)
        print()

    def _imprimir_cabecalho_texto(self, sep: LiteralString) -> None:
        """Imprime título e separador em modo texto."""
        titulo = _TITULO_BUSCA
        if self._nome_so:
            titulo += f"  ({self._nome_so})"
        print(sep)
        print(f"  {titulo}")
        print(sep)

    def _imprimir_info_gerais_texto(self, resultado: ResultadoBusca, sep: LiteralString) -> None:
        """Imprime informações gerais da busca em modo texto."""
        raiz: str = str(resultado.raiz_busca) if resultado.raiz_busca else "?"
        print(f"  Diretório raiz : {raiz}")
        if resultado.criterios:
            crit = resultado.criterios
            if crit.consulta:
                print(f"  Consulta       : {crit.consulta}")
            if crit.padrao_glob:
                print(f"  Glob           : {crit.padrao_glob}")
        print(f"  Tempo          : {resultado.tempo_execucao:.2f}s")
        print(sep)

    def _detalhes_item_texto(self, item: ItemBase) -> tuple[str, str]:
        """Retorna símbolo e detalhe (tamanho/itens) para um item em modo texto."""
        if isinstance(item, ItemArquivo):
            simbolo: str = _SIMBOLO_ARQUIVO
            detalhe: str = _formatar_tamanho(item.tamanho)
        else:
            simbolo = _SIMBOLO_PASTA
            detalhe = _formatar_qtd_itens(qtd=item.qtd_itens if isinstance(item, ItemDiretorio) else None)
        return simbolo, detalhe

    def _imprimir_itens_texto(self, resultado: ResultadoBusca) -> None:
        """Imprime a lista de itens em modo texto."""
        itens_exibidos: list[ItemBase] = resultado.itens[: self._max_itens]
        for i, item in enumerate(itens_exibidos, start=1):
            simbolo, detalhe = self._detalhes_item_texto(item)
            print(f"  {i:>4}.  {simbolo}  {item.nome:<40}  {detalhe:>10}  {_formatar_data(dt=item.modificado)}")

        if resultado.total_encontrado > self._max_itens:
            print(f"  {_AVISO_TRUNCADO}")

    def _imprimir_rodape_texto(self, resultado: ResultadoBusca, sep: LiteralString) -> None:
        """Imprime o rodapé com totais em modo texto."""
        self._imprimir_rodape_texto_impl(resultado, sep)

    def _imprimir_rodape_texto_impl(self, resultado: ResultadoBusca, sep: LiteralString) -> None:
        arqs: int = sum(isinstance(it, ItemArquivo) for it in resultado.itens)
        pastas: int = resultado.total_encontrado - arqs
        tamanho_total: int = sum(it.tamanho for it in resultado.itens if isinstance(it, ItemArquivo) and it.tamanho)
        print(sep)
        print(f"  ✔  {arqs} arquivo(s)  {pastas} pasta(s)  │  Tamanho total: {_formatar_tamanho(tamanho_total)}")
        print(sep)


# ---------------------------------------------------------------------------
# Atalho de módulo
# ---------------------------------------------------------------------------
def exibir_resultado(
    resultado: ResultadoBusca,
    max_itens: int = _MAX_ITENS_PADRAO,
    nome_so: str | None = None,
) -> None:
    """Atalho: instancia ``Apresentador`` e exibe o resultado.

    Args:
        resultado: Resultado da busca a ser exibido.
        max_itens: Número máximo de itens na listagem.
        nome_so: Nome do sistema operacional (opcional, exibido no título).
    """
    Apresentador(max_itens=max_itens, nome_so=nome_so).exibir(resultado=resultado)
