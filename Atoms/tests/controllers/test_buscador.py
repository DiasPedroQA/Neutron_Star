"""Testes de integração para Buscador.

Cobre o fluxo completo (glob -> poda de ocultos -> regex -> metadados),
incluindo os três requisitos tratados nesta sessão:
    1. Diretórios ocultos nunca são visitados.
    2. Prefixos sinônimos pt-BR/en-US são aceitos como o mesmo padrão.
    3. Datas com/sem zero à esquerda são equivalentes.

Nota: não havia arquivo-fonte de teste para Buscador no repositório (só um
.pyc órfão em __pycache__), então esta suíte cobre uma lacuna real.
"""

from __future__ import annotations

from pathlib import Path

from src.controllers.buscador import Buscador
from src.models.arquivo import Arquivo


def _criar(base: Path, relativo: str, conteudo: str = "conteudo") -> Path:
    """Cria um arquivo de teste com conteúdo simples em uma estrutura de diretórios.
    Garante que os diretórios necessários existam antes de escrever o conteúdo.

    Args:
        base: Diretório base onde o caminho relativo será criado.
        relativo: Caminho relativo do arquivo a ser criado dentro de `base`.
        conteudo: Conteúdo textual que será gravado no arquivo criado.

    Returns:
        Caminho completo para o arquivo recém-criado.
    """
    caminho: Path = base / relativo
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(data=conteudo)
    return caminho


class TestBuscadorIgnoraOcultos:
    """Requisito 1: nunca descer em diretórios ocultos."""

    def test_arquivos_em_venv_e_local_nao_aparecem(self, tmp_path: Path) -> None:
        """Garante que arquivos localizados em diretórios ocultos padrão são ignorados na busca.
        Verifica que apenas arquivos visíveis na raiz são retornados mesmo quando há conteúdo em caminhos ocultos.

        Args:
            tmp_path: Diretório temporário usado como raiz para criar a estrutura de arquivos e diretórios de teste.
        """
        _criar(base=tmp_path, relativo=".venv/lib/site-packages/coverage/index.html")
        _criar(base=tmp_path, relativo=".local/share/Trash/files/relatorio.html")
        _criar(base=tmp_path, relativo="favoritos.html")

        buscador = Buscador(prefixo="favoritos")
        buscador.raiz = tmp_path
        resultado: list[Arquivo] = buscador.buscar_arquivos()

        nomes: set[str] = {a.caminho.name for a in resultado}
        assert nomes == {"favoritos.html"}


class TestBuscadorMultiplosPrefixos:
    """Requisito 3: aceitar aliases pt-BR/en-US como o mesmo padrão."""

    def test_encontra_favoritos_e_bookmarks_na_mesma_busca(self, tmp_path: Path) -> None:
        """Verifica que múltiplos prefixos equivalentes retornam todos os arquivos compatíveis em uma única busca.
        Garante que aliases pt-BR e en-US são tratados como padrões equivalentes ao filtrar resultados por prefixo e data.

        Args:
            tmp_path: Diretório temporário usado como raiz para criar os arquivos de teste com diferentes prefixos.
        """
        _criar(base=tmp_path, relativo="favoritos_5_20_26.html")
        _criar(base=tmp_path, relativo="bookmarks_5_20_26.html")
        _criar(base=tmp_path, relativo="outracoisa.html")

        buscador = Buscador(prefixo=["favoritos", "bookmarks"], data="5_20_26")
        buscador.raiz = tmp_path
        resultado: list[Arquivo] = buscador.buscar_arquivos()

        nomes: set[str] = {a.caminho.name for a in resultado}
        assert nomes == {"favoritos_5_20_26.html", "bookmarks_5_20_26.html"}

    def test_encontra_bookmarks_sem_data(self, tmp_path: Path) -> None:
        """Verifica que a busca por prefixos encontra arquivos mesmo quando nenhuma data é informada.
        Garante que o Buscador não exige padrão de data para retornar resultados compatíveis com o prefixo.

        Args:
            tmp_path: Diretório temporário usado como raiz para criar o arquivo de teste sem data no nome.
        """
        _criar(base=tmp_path, relativo="bookmarks.html")

        buscador = Buscador(prefixo=["favoritos", "bookmarks"])
        buscador.raiz = tmp_path
        resultado: list[Arquivo] = buscador.buscar_arquivos()

        assert len(resultado) == 1
        assert resultado[0].caminho.name == "bookmarks.html"


class TestBuscadorDataToleranteAZeroAEsquerda:
    """Requisito 2 (correlato): data "5_20_26" deve casar com "05_20_26"."""

    def test_zero_a_esquerda_nao_impede_o_casamento(self, tmp_path: Path) -> None:
        """Garante que datas com zero à esquerda ainda são reconhecidas como equivalentes na busca.
        Valida que o padrão de data fornecido casa corretamente com arquivos cujo nome inclui zeros à esquerda.

        Args:
            tmp_path: Diretório temporário usado como raiz para criar o arquivo de teste com data contendo zero à esquerda.
        """
        _criar(base=tmp_path, relativo="bookmarks_05_20_26.html")

        buscador = Buscador(prefixo="bookmarks", data="5_20_26")
        buscador.raiz = tmp_path
        resultado: list[Arquivo] = buscador.buscar_arquivos()

        assert resultado
        assert resultado[0].caminho.name == "bookmarks_05_20_26.html"
