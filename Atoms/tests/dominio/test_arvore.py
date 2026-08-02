"""
Testes da árvore de bookmarks (dominio.arvore).

Usa `aplicacao.leitura.parsear_html` para montar as fixtures, garantindo
que o teste valida o domínio exatamente com o parser que a aplicação
usa em produção (html5lib) — ver nota em `aplicacao/leitura.py`.
"""

from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from src.aplicacao.leitura import parsear_html
from src.dominio.arvore import contar_links, extrair_arvore, flatten_tree
from src.dominio.entidades import BookmarkNode

# ---------------------------------------------------------------------------
# Função auxiliar para evitar duplicação em verificações de tipo/nome
# ---------------------------------------------------------------------------


def _verificar_no(no: BookmarkNode, tipo: str, nome: str) -> None:
    """Afirma que o nó possui o tipo e o nome esperados."""
    assert no.tipo == tipo, f"Esperado tipo '{tipo}', obtido '{no.tipo}'"
    assert no.nome == nome, f"Esperado nome '{nome}', obtido '{no.nome}'"


# ---------------------------------------------------------------------------
# Testes de extração da árvore
# ---------------------------------------------------------------------------


def test_extrair_arvore_simples() -> None:
    """Um único link na raiz."""
    conteudo = """<DL><p>
        <DT><A HREF="https://example.com">Exemplo</A>
    </DL>"""
    soup: BeautifulSoup = parsear_html(conteudo)
    root: Tag | None = soup.find("dl")
    assert root is not None, "Tag <DL> raiz não encontrada"

    arvore: list[BookmarkNode] = extrair_arvore(tag_dl=root)
    assert len(arvore) == 1
    node: BookmarkNode = arvore[0]
    assert node.tipo == "link"
    assert node.nome == "Exemplo"
    assert node.url == "https://example.com"


def test_extrair_arvore_aninhada() -> None:
    """Pastas aninhadas e links em diferentes níveis."""
    conteudo = """<DL><p>
        <DT><H3>Pasta 1</H3>
        <DL><p>
            <DT><A HREF="https://a.com">Link A</A>
            <DT><H3>Subpasta</H3>
            <DL><p>
                <DT><A HREF="https://b.com">Link B</A>
            </DL>
        </DL>
        <DT><A HREF="https://c.com">Link C (raiz)</A>
    </DL>"""
    soup: BeautifulSoup = parsear_html(conteudo)
    root: Tag | None = soup.find(name="dl")
    assert root is not None, "Tag <DL> raiz não encontrada"

    arvore: list[BookmarkNode] = extrair_arvore(tag_dl=root)

    # Pasta 1 e Link C na raiz
    assert len(arvore) == 2

    pasta = arvore[0]
    _verificar_no(pasta, "pasta", "Pasta 1")
    assert len(pasta.filhos) == 2  # Link A e Subpasta

    link_a = pasta.filhos[0]
    _verificar_no(link_a, "link", "Link A")
    assert link_a.url == "https://a.com"

    subpasta = pasta.filhos[1]
    _verificar_no(subpasta, "pasta", "Subpasta")
    assert len(subpasta.filhos) == 1
    assert subpasta.filhos[0].nome == "Link B"

    link_c = arvore[1]
    _verificar_no(link_c, "link", "Link C (raiz)")
    assert link_c.url == "https://c.com"


def test_extrair_arvore_tags_intermediarias() -> None:
    """Garante que a árvore é extraída mesmo com <p> entre <DT> e <DL>."""
    conteudo = """<DL><p>
        <DT><H3>Pasta</H3>
        <p>
        <DL><p>
            <DT><A HREF="https://d.com">Link D</A>
        </DL>
    </DL>"""
    soup: BeautifulSoup = parsear_html(conteudo)
    root: Tag | None = soup.find("dl")
    assert root is not None, "Tag <DL> raiz não encontrada"

    arvore: list[BookmarkNode] = extrair_arvore(tag_dl=root)
    assert len(arvore) == 1

    pasta: BookmarkNode = arvore[0]
    assert pasta.tipo == "pasta"
    assert len(pasta.filhos) == 1
    assert pasta.filhos[0].tipo == "link"
    assert pasta.filhos[0].nome == "Link D"


def test_extrair_arvore_vazia() -> None:
    """Árvore a partir de um <DL> sem itens."""
    soup: BeautifulSoup = parsear_html(conteudo="<DL></DL>")
    root: Tag | None = soup.find(name="dl")
    assert root is not None, "Tag <DL> raiz não encontrada"

    arvore: list[BookmarkNode] = extrair_arvore(tag_dl=root)
    assert not arvore


# ---------------------------------------------------------------------------
# Testes de achatamento (flatten_tree)
# ---------------------------------------------------------------------------


def test_flatten_tree_simples() -> None:
    """Achatamento de um único link."""
    arvore: list[BookmarkNode] = [BookmarkNode(tipo="link", nome="Site", url="https://site.com")]
    records: list[dict[str, str]] = flatten_tree(nodes=arvore)
    assert len(records) == 1
    assert records[0]["title"] == "Site"
    assert records[0]["url"] == "https://site.com"
    assert records[0]["folder"] == ""


def test_flatten_tree_com_pastas() -> None:
    """Achatamento com pastas e links em diferentes níveis."""
    sublink: BookmarkNode = BookmarkNode(tipo="link", nome="Sub", url="https://sub.com")
    link: BookmarkNode = BookmarkNode(tipo="link", nome="Root", url="https://root.com")
    pasta: BookmarkNode = BookmarkNode(tipo="pasta", nome="Minha Pasta", filhos=[sublink])
    arvore: list[BookmarkNode] = [pasta, link]
    records: list[dict[str, str]] = flatten_tree(nodes=arvore)
    assert len(records) == 2

    # Primeiro registro: link dentro da pasta
    assert records[0]["title"] == "Sub"
    assert records[0]["folder"] == "Minha Pasta"

    # Segundo registro: link na raiz
    assert records[1]["title"] == "Root"
    assert records[1]["folder"] == ""


def test_flatten_tree_pasta_vazia() -> None:
    """Pasta sem filhos não gera registros."""
    pasta_vazia: BookmarkNode = BookmarkNode(tipo="pasta", nome="Vazia", filhos=[])
    records: list[dict[str, str]] = flatten_tree(nodes=[pasta_vazia])
    assert not records


def test_flatten_tree_arvore_vazia() -> None:
    """Lista vazia de nós retorna lista vazia."""
    records: list[dict[str, str]] = flatten_tree(nodes=[])
    assert not records


# ---------------------------------------------------------------------------
# Testes de contagem de links
# ---------------------------------------------------------------------------


def test_contar_links_simples() -> None:
    """Um link conta como 1."""
    node: BookmarkNode = BookmarkNode(tipo="link", nome="x")
    assert contar_links(no=node) == 1


def test_contar_links_pasta() -> None:
    """Contagem recursiva de links em uma pasta."""
    pasta: BookmarkNode = BookmarkNode(
        tipo="pasta",
        nome="P",
        filhos=[
            BookmarkNode(tipo="link", nome="a"),
            BookmarkNode(tipo="link", nome="b"),
            BookmarkNode(tipo="pasta", nome="sub", filhos=[BookmarkNode(tipo="link", nome="c")]),
        ],
    )
    assert contar_links(no=pasta) == 3


def test_contar_links_vazio() -> None:
    """Pasta sem links retorna zero."""
    pasta_vazia: BookmarkNode = BookmarkNode(tipo="pasta", nome="Vazia")
    assert contar_links(no=pasta_vazia) == 0
