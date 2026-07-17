from collections.abc import Iterator

from bs4 import BeautifulSoup, NavigableString, Tag
from dominio.entidades import Bookmark, BookmarkFolder, ItemPasta
from dominio.excecoes import ErroParseBookmarks


def _montar_bookmark(tag_a: Tag) -> Bookmark:
    """Converte uma tag <A> em Bookmark."""
    return Bookmark(
        url=str(tag_a.get("href", "")),
        titulo=tag_a.get_text(strip=True),
        data_adicao=str(tag_a.get("add_date", "")),
        ultima_modificacao=str(tag_a.get("last_modified", "")),
        icon_uri=str(tag_a.get("icon_uri", "")),
    )


def _montar_pasta(tag_h3: Tag, dl_pasta: Tag | NavigableString | None) -> BookmarkFolder:
    """Converte um <H3> e seu <DL> associado em BookmarkFolder."""
    itens: list[ItemPasta] = _processar_lista(tag_dl=dl_pasta) if isinstance(dl_pasta, Tag) else []
    return BookmarkFolder(
        nome=tag_h3.get_text(strip=True),
        data_adicao=str(tag_h3.get("add_date", "")),
        ultima_modificacao=str(tag_h3.get("last_modified", "")),
        itens=itens,
    )


def _item_de_dt(dt_tag: Tag) -> ItemPasta | None:
    """Converte um <DT> em Bookmark ou BookmarkFolder, ou None se não reconhecido.

    Usa recursive=False ao procurar <a>/<h3>/<dl> dentro do <dt>: como o
    Netscape Bookmark File não fecha as tags <DT>, um parser tolerante
    (html.parser) aninha o próximo <DT> DENTRO do anterior. Uma busca
    recursiva pegaria itens de níveis mais profundos por engano.
    """
    tag_a: Tag | NavigableString | None = dt_tag.find("a", recursive=False)
    if isinstance(tag_a, Tag):
        return _montar_bookmark(tag_a=tag_a)

    tag_h3: Tag | NavigableString | None = dt_tag.find("h3", recursive=False)
    if isinstance(tag_h3, Tag):
        dl_pasta: Tag | NavigableString | None = dt_tag.find("dl", recursive=False)
        return _montar_pasta(tag_h3=tag_h3, dl_pasta=dl_pasta)

    return None


def _dts_do_nivel(dl: Tag) -> Iterator[Tag]:
    """Itera os <DT> cujo <DL> ancestral mais próximo é `dl`.

    Substitui `dl.find_all("dt", recursive=False)`, que não funciona aqui:
    como <DT> não é fechado, os "irmãos" viram filhos aninhados uns dos
    outros. O <DL> ancestral mais próximo, porém, continua identificando
    corretamente a qual pasta/nível cada <DT> pertence.
    """
    for dt_tag in dl.find_all("dt"):
        if dt_tag.find_parent("dl") is dl:
            yield dt_tag


def _processar_lista(tag_dl: Tag) -> list[ItemPasta]:
    """Processa uma <DL>, retornando os itens (Bookmark ou BookmarkFolder) do seu nível."""
    itens: list[ItemPasta] = []
    for dt_tag in _dts_do_nivel(dl=tag_dl):
        if item := _item_de_dt(dt_tag=dt_tag):
            itens.append(item)
    return itens


def parse_bookmarks_html(conteudo_html: str) -> BookmarkFolder:
    """Interpreta um documento Netscape Bookmark File.

    Returns:
        Pasta raiz artificial 'Bookmarks' com os itens de nível superior.
    """
    soup = BeautifulSoup(markup=conteudo_html, features="html.parser")
    dl_raiz: Tag | NavigableString | None = soup.find(name="dl")
    if not isinstance(dl_raiz, Tag):
        raise ErroParseBookmarks(mensagem="Elemento <DL> raiz não encontrado.")

    itens: list[ItemPasta] = _processar_lista(tag_dl=dl_raiz)
    return BookmarkFolder(nome="Bookmarks", itens=itens)
