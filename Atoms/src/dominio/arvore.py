"""
Regras de domínio para extrair e transformar a árvore de bookmarks.

Estas funções recebem uma árvore HTML já parseada (objetos `Tag` do
bs4) e não fazem I/O — quem lê o arquivo e decide o parser é a camada
de aplicação (`aplicacao.leitura`, `aplicacao.casos_de_uso`).
"""

from __future__ import annotations

from bs4 import Tag

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
    sibling: Tag | None = elemento.find_next_sibling()
    while sibling is not None:
        if sibling.name in nomes_validos:
            return sibling
        sibling = sibling.find_next_sibling()
    return None


def extrair_arvore(tag_dl: Tag) -> list[BookmarkNode]:
    """
    Extrai recursivamente a árvore de bookmarks a partir de uma tag <DL>.

    Pressupõe que `tag_dl` foi parseada com um parser que fecha `<p>` e
    `<DT>` seguindo as regras do HTML5 (ex.: 'html5lib'), de modo que o
    `<DL>` de uma subpasta apareça como filho do `<DT>` correspondente
    — que é como o formato Netscape Bookmark File é definido. Ver
    `aplicacao.leitura` para o ponto onde o parser é escolhido.
    """
    nodes: list[BookmarkNode] = []

    def _find_h3(element: Tag) -> Tag | None:
        """Localiza a tag <h3> associada a um elemento de pasta na árvore de bookmarks.

        Busca primeiro por um filho direto <h3> e, se necessário, por qualquer ocorrência descendente para obter o título da pasta.
        """
        h: Tag | None = element.find(name="h3", recursive=False)
        return h or element.find(name="h3")

    def _find_a(element: Tag) -> Tag | None:
        """Localiza a tag <a> correspondente a um link dentro de um elemento de bookmark.

        Procura primeiro por um filho direto <a> e, se necessário, por qualquer ocorrência descendente para recuperar o link associado.
        """
        a: Tag | None = element.find(name="a", recursive=False)
        return a or element.find("a")

    def _find_sub_dl(element: Tag) -> Tag | None:
        """Encontra a tag <dl> que representa a subpasta associada a um elemento <dt>.

        Procura primeiro por um filho direto <dl> e, se necessário, usa irmãos seguintes para lidar com HTML malformado mantendo a relação de hierarquia.
        """
        # caso padrão: <DT><H3>...</H3><DL>...</DL></DT> — DL é filho de DT
        filho: Tag | None = element.find(name="dl", recursive=False)
        if filho:
            return filho
        # fallback para HTML malformado onde o DL aparece como irmão
        sub: Tag | None = element.find_next_sibling(name="dl")
        if sub:
            return sub
        return _buscar_proximo_irmao_relevante(elemento=element, nomes_validos=("dl",))

    for dt in tag_dl.find_all(name="dt", recursive=False):
        h3: Tag | None = _find_h3(element=dt)
        if h3:
            nome_pasta: str = h3.get_text(strip=True)
            data: str | None = to_str(valor=h3.get("add_date"))
            sub_dl: Tag | None = _find_sub_dl(element=dt)
            filhos: list[BookmarkNode] = extrair_arvore(tag_dl=sub_dl) if sub_dl else []
            nodes.append(
                BookmarkNode(tipo="pasta", nome=nome_pasta, data_adicao=data, filhos=filhos)
            )
            continue

        a: Tag | None = _find_a(element=dt)
        if not a:
            continue
        nodes.append(
            BookmarkNode(
                tipo="link",
                nome=a.get_text(strip=True),
                url=to_str(valor=a.get("href")),
                data_adicao=to_str(valor=a.get("add_date")),
                icone=to_str(valor=a.get("icon")),
            )
        )

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
