"""Caso de uso de interpretação de arquivos Netscape TagA (HTML).

Converte o conteúdo HTML exportado por navegadores em uma estrutura
de entidades de domínio (pastas e favoritos) pronta para uso em outros casos de uso.
"""

from collections.abc import Iterator

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from dominio.entidades import ItemPasta, TagA, VirtualFolder
from dominio.excecoes import ErroParseBookmarks


def _montar_bookmark(tag_a: Tag) -> TagA:
    """Converte uma tag <A> em TagA."""
    return TagA(
        url=str(tag_a.get(key="href", default="")),
        titulo=tag_a.get_text(strip=True),
        data_adicao=str(tag_a.get(key="add_date", default="")),
        ultima_modificacao=str(tag_a.get(key="last_modified", default="")),
        icon_uri=str(tag_a.get(key="icon_uri", default="")),
    )


def _montar_pasta(tag_h3: Tag, dl_pasta: Tag | NavigableString | None) -> VirtualFolder:
    """Converte um <H3> e seu <DL> associado em VirtualFolder."""
    filhos_da_pasta: list[ItemPasta] = _processar_lista(tag_dl=dl_pasta) if isinstance(dl_pasta, Tag) else []
    return VirtualFolder(
        nome=tag_h3.get_text(strip=True),
        data_adicao=str(tag_h3.get(key="add_date", default="")),
        ultima_modificacao=str(tag_h3.get(key="last_modified", default="")),
        filhos_da_pasta=filhos_da_pasta,
    )


def _item_de_dt(dt_tag: Tag) -> ItemPasta | None:
    """Converte um <DT> em TagA ou VirtualFolder, ou None se não reconhecido.

    Usa recursive=False ao procurar <a>/<h3>/<dl> dentro do <dt>: como o
    Netscape TagA File não fecha as tags <DT>, um parser tolerante
    (html.parser) aninha o próximo <DT> DENTRO do anterior. Uma busca
    recursiva pegaria itens de níveis mais profundos por engano.
    """
    tag_a: Tag | NavigableString | None = dt_tag.find(name="a", recursive=False)
    if isinstance(tag_a, Tag):
        return _montar_bookmark(tag_a=tag_a)

    tag_h3: Tag | NavigableString | None = dt_tag.find(name="h3", recursive=False)
    if isinstance(tag_h3, Tag):
        dl_pasta: Tag | NavigableString | None = dt_tag.find(name="dl", recursive=False)
        return _montar_pasta(tag_h3=tag_h3, dl_pasta=dl_pasta)

    return None


def _dts_do_nivel(dl: Tag) -> Iterator[Tag]:
    """Itera os <DT> cujo <DL> ancestral mais próximo é `dl`.

    Substitui `dl.find_all("dt", recursive=False)`, que não funciona aqui:
    como <DT> não é fechado, os "irmãos" viram filhos aninhados uns dos
    outros. O <DL> ancestral mais próximo, porém, continua identificando
    corretamente a qual pasta/nível cada <DT> pertence.
    """
    for dt_tag in dl.find_all(name="dt"):
        if dt_tag.find_parent(name="dl") is dl:
            yield dt_tag


def _processar_lista(tag_dl: Tag) -> list[ItemPasta]:
    """Processa uma <DL>, retornando os itens (TagA ou VirtualFolder) do seu nível."""
    tags_dt: list[ItemPasta] = []
    for dt_tag in _dts_do_nivel(dl=tag_dl):
        if item := _item_de_dt(dt_tag=dt_tag):
            tags_dt.append(item)
    return tags_dt


def parse_bookmarks_html(conteudo_html: str) -> VirtualFolder:
    """Interpreta um documento Netscape TagA File.

    Returns:
        Pasta raiz artificial 'Bookmarks' com os itens de nível superior.
    """
    soup = BeautifulSoup(markup=conteudo_html, features="html.parser")
    dl_raiz: Tag | NavigableString | None = soup.find(name="dl")
    if not isinstance(dl_raiz, Tag):
        raise ErroParseBookmarks(mensagem="Elemento <DL> raiz não encontrado.")

    filhos_da_pasta: list[ItemPasta] = _processar_lista(tag_dl=dl_raiz)
    return VirtualFolder(nome="Bookmarks", filhos_da_pasta=filhos_da_pasta)
