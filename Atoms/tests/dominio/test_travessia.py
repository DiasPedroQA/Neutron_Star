"""Testes da travessia recursiva de bookmarks (dominio/travessia.py).

Cobre o contrato compartilhado por todos os exportadores: percorrer a
hierarquia de pastas e retornar apenas os favoritos (TagA), em profundidade.
"""

from dominio.entidades import TagA, VirtualFolder
from dominio.travessia import iterar_bookmarks, iterar_bookmarks_com_caminho


class TestIterarBookmarks:
    """Percurso em profundidade sobre a árvore de pastas/favoritos."""

    def test_pasta_vazia_nao_produz_favoritos(self) -> None:
        """Pasta sem filhos deve resultar em iterador vazio."""
        pasta = VirtualFolder(nome="Raiz")

        assert not list(iterar_bookmarks(pasta=pasta))

    def test_favoritos_no_primeiro_nivel_sao_retornados_na_ordem(self) -> None:
        """Favoritos diretamente na raiz devem sair na ordem em que aparecem."""
        pasta = VirtualFolder(
            nome="Raiz",
            filhos_da_pasta=[
                TagA(url="https://a.com", titulo="A"),
                TagA(url="https://b.com", titulo="B"),
            ],
        )

        titulos: list[str] = [bm.titulo for bm in iterar_bookmarks(pasta=pasta)]

        assert titulos == ["A", "B"]

    def test_desce_recursivamente_em_subpastas_aninhadas(self) -> None:
        """Favoritos dentro de subpastas (em qualquer profundidade) devem ser incluídos."""
        pasta = VirtualFolder(
            nome="Raiz",
            filhos_da_pasta=[
                TagA(url="https://a.com", titulo="A"),
                VirtualFolder(
                    nome="Nivel1",
                    filhos_da_pasta=[
                        TagA(url="https://b.com", titulo="B"),
                        VirtualFolder(
                            nome="Nivel2",
                            filhos_da_pasta=[TagA(url="https://c.com", titulo="C")],
                        ),
                    ],
                ),
            ],
        )

        titulos: list[str] = [bm.titulo for bm in iterar_bookmarks(pasta=pasta)]

        assert titulos == ["A", "B", "C"]

    def test_subpastas_vazias_nao_quebram_a_travessia(self) -> None:
        """Uma subpasta sem favoritos não deve interromper nem afetar o resultado."""
        pasta = VirtualFolder(
            nome="Raiz",
            filhos_da_pasta=[
                VirtualFolder(nome="Vazia"),
                TagA(url="https://a.com", titulo="A"),
            ],
        )

        titulos: list[str] = [bm.titulo for bm in iterar_bookmarks(pasta=pasta)]

        assert titulos == ["A"]


class TestIterarBookmarksComCaminho:
    """Percurso que também informa o caminho de pastas até cada favorito."""

    def test_favorito_no_primeiro_nivel_tem_caminho_vazio(self) -> None:
        """Favorito diretamente na raiz não pertence a nenhuma subpasta."""
        pasta = VirtualFolder(nome="Raiz", filhos_da_pasta=[TagA(url="https://a.com", titulo="A")])

        resultado: list[tuple[str, TagA]] = list(iterar_bookmarks_com_caminho(pasta=pasta))

        assert resultado == [("", pasta.filhos_da_pasta[0])]

    def test_favorito_em_subpasta_recebe_o_nome_da_subpasta(self) -> None:
        """Favorito dentro de uma subpasta deve ter o nome dela como caminho."""
        pasta = VirtualFolder(
            nome="Raiz",
            filhos_da_pasta=[
                VirtualFolder(
                    nome="Trabalho",
                    filhos_da_pasta=[TagA(url="https://b.com", titulo="B")],
                ),
            ],
        )

        caminhos: list[str] = [caminho for caminho, _ in iterar_bookmarks_com_caminho(pasta=pasta)]

        assert caminhos == ["Trabalho"]

    def test_subpastas_aninhadas_acumulam_caminho_com_barra(self) -> None:
        """Vários níveis de aninhamento devem gerar um caminho tipo 'Nivel1/Nivel2'."""
        pasta = VirtualFolder(
            nome="Raiz",
            filhos_da_pasta=[
                VirtualFolder(
                    nome="Nivel1",
                    filhos_da_pasta=[
                        VirtualFolder(
                            nome="Nivel2",
                            filhos_da_pasta=[TagA(url="https://c.com", titulo="C")],
                        ),
                    ],
                ),
            ],
        )

        caminhos: list[str] = [caminho for caminho, _ in iterar_bookmarks_com_caminho(pasta=pasta)]

        assert caminhos == ["Nivel1/Nivel2"]
