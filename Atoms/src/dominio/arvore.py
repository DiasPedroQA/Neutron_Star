"""
Regras de domínio para extrair e transformar a árvore de bookmarks.

Estas funções recebem uma árvore HTML já parseada (objetos `Tag` do
bs4) e não fazem I/O — quem lê o arquivo e decide o parser é a camada
de aplicação (`aplicacao.leitura`, `aplicacao.casos_de_uso`).
"""

from __future__ import annotations

from bs4.element import NavigableString, Tag

from src.dominio.entidades import BookmarkNode
from src.dominio.tipos import to_str

# ---------------------------------------------------------------------------
# Extração da árvore
# ---------------------------------------------------------------------------


def _buscar_proximo_irmao_relevante(
    elemento: Tag, nomes_validos: tuple[str, ...] = ("dl", "dt")
) -> Tag | None:
    """
    A partir de um elemento, percorre os irmãos seguintes até encontrar
    um com o nome desejado (ex.: 'dl' ou 'dt'), ignorando tags como <p>.

    Serve apenas como rede de segurança para HTML malformado além do
    padrão já tratado por `extrair_arvore` (ver `_find_sub_dl`).
    """
    sibling: Tag | NavigableString | None = elemento.find_next_sibling()
    while sibling is not None:
        if isinstance(sibling, Tag) and sibling.name in nomes_validos:
            return sibling
        sibling = sibling.find_next_sibling()
    return None


def _find_descendant_tag(element: Tag, name: str, recursive: bool) -> Tag | None:
    tag: Tag | NavigableString | None = element.find(name=name, recursive=recursive)
    return tag if isinstance(tag, Tag) else None


def _find_h3(element: Tag) -> Tag | None:
    h3: Tag | None = _find_descendant_tag(element, "h3", recursive=False)
    return h3 or _find_descendant_tag(element, "h3", recursive=True)


def _find_a(element: Tag) -> Tag | None:
    a: Tag | None = _find_descendant_tag(element, "a", recursive=False)
    return a or _find_descendant_tag(element, "a", recursive=True)


def _find_sub_dl(element: Tag) -> Tag | None:
    """Encontra a tag <dl> que representa a subpasta associada a um elemento <dt>."""
    if filho := _find_descendant_tag(element, "dl", recursive=False):
        return filho

    sub: Tag | NavigableString | None = element.find_next_sibling(name="dl")
    if isinstance(sub, Tag):
        return sub

    return _buscar_proximo_irmao_relevante(elemento=element, nomes_validos=("dl",))


def _make_folder_node(dt: Tag, h3: Tag) -> BookmarkNode:
    nome_pasta: str = h3.get_text(strip=True)
    data: str | None = to_str(valor=h3.get("add_date"))
    sub_dl: Tag | None = _find_sub_dl(element=dt)
    filhos: list[BookmarkNode] = extrair_arvore(tag_dl=sub_dl) if sub_dl else []
    return BookmarkNode(
        tipo="pasta",
        nome=nome_pasta,
        data_adicao=data,
        filhos=filhos,
    )


def _make_link_node(a: Tag) -> BookmarkNode:
    return BookmarkNode(
        tipo="link",
        nome=a.get_text(strip=True),
        url=to_str(valor=a.get("href")),
        data_adicao=to_str(valor=a.get("add_date")),
        icone=to_str(valor=a.get("icon")),
    )


def extrair_arvore(tag_dl: Tag) -> list[BookmarkNode]:
    """Extrai recursivamente a árvore de bookmarks a partir de uma tag <DL>."""
    nodes: list[BookmarkNode] = []

    for dt in tag_dl.find_all(name="dt", recursive=False):
        if h3 := _find_h3(element=dt):
            nodes.append(_make_folder_node(dt=dt, h3=h3))
            continue

        if a := _find_a(element=dt):
            nodes.append(_make_link_node(a=a))

    return nodes


# ---------------------------------------------------------------------------
# Achatamento da árvore para lista de dicionários (formato tabular)
# ---------------------------------------------------------------------------


def flatten_tree(
    nodes: list[BookmarkNode], parent_path: list[str] | None = None
) -> list[dict[str, str]]:
    """
    Converte uma lista de BookmarkNode em uma lista plana de dicionários,
    incluindo a coluna 'folder' com o caminho completo da pasta.
    """
    records: list[dict[str, str]] = []
    if parent_path is None:
        parent_path = []

    for node in nodes:
        if node.tipo == "pasta":
            current_path: list[str] = [*parent_path, node.nome]
            records.extend(flatten_tree(nodes=node.filhos, parent_path=current_path))
        else:  # link
            objeto_novo: dict[str, str] = {
                "title": node.nome,
                "url": node.url or "",
                "add_date": str(node.data_adicao) if node.data_adicao else "",
                "icon": node.icone or "",
                "folder": "/".join(parent_path) if parent_path else "",
            }
            records.append(objeto_novo)
    return records


# ---------------------------------------------------------------------------
# Contagem de links (útil para relatórios)
# ---------------------------------------------------------------------------


def contar_links(no: BookmarkNode) -> int:
    """Conta recursivamente o número de links em uma subárvore."""
    total = 0
    stack: list[BookmarkNode] = [no]
    while stack:
        node: BookmarkNode = stack.pop()
        if node.tipo == "link":
            total += 1
        else:
            stack.extend(node.filhos)
    return total
