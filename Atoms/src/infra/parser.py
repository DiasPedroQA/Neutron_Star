# src/infra/parser.py
# pylint: disable=too-few-public-methods

"""Implementação concreta do adaptador de extração de tags usando BeautifulSoup."""

from datetime import UTC, datetime

from bs4 import BeautifulSoup
from bs4.element import Tag

from ..aplicacao.portas import ParserPort
from ..dominio.entidades import Favorito


class ParserBeautifulSoup(ParserPort):
    """Adaptador de infraestrutura para extração e processamento de favoritos HTML."""

    @staticmethod
    def _coerce_atributo(valor: object) -> str:
        """Normaliza atributos HTML que podem vir como str, list ou None."""
        return valor if isinstance(valor, str) else ""

    @staticmethod
    def _converter_timestamp(timestamp_str: str) -> str:
        """Converte um timestamp Unix string em data e hora formatadas."""
        if not timestamp_str:
            return "Sem data"
        try:
            return datetime.fromtimestamp(timestamp=int(timestamp_str), tz=UTC).strftime(
                format="%d/%m/%Y %H:%M:%S"
            )
        except (ValueError, TypeError):
            return "Data inválida"

    @staticmethod
    def _criar_favorito(link: Tag, pilha_pastas: list[str]) -> Favorito | None:
        """Cria um favorito a partir de um link válido."""
        caminho_pasta: str = " / ".join(pilha_pastas) if pilha_pastas else "Favoritos"
        url: str = ParserBeautifulSoup._coerce_atributo(link.get("href", ""))
        add_date: str = ParserBeautifulSoup._coerce_atributo(link.get("add_date", ""))
        try:
            return Favorito(
                titulo=link.get_text().strip(),
                url=url,
                pasta=caminho_pasta,
                data_adicao=ParserBeautifulSoup._converter_timestamp(timestamp_str=add_date),
            )
        except ValueError:
            return None

    def _processar_no(self, no: Tag, pilha_pastas: list[str], favoritos: list[Favorito]) -> None:
        """Processa um nó e seus descendentes."""
        if not no.contents:
            return

        ultimo_h3: str | None = None
        for filho in no.contents:
            if not isinstance(filho, Tag):
                continue

            nome_tag: str = filho.name.lower()

            if nome_tag == "h3":
                ultimo_h3 = filho.get_text().strip()
            elif nome_tag == "a":
                favorito: Favorito | None = self._criar_favorito(
                    link=filho, pilha_pastas=pilha_pastas
                )
                if favorito is not None:
                    favoritos.append(favorito)

            # Só empilha uma pasta se houver um <H3> real precedendo a <DL>.
            # A <DL> raiz do arquivo (sem H3 anterior) não representa uma pasta
            # nomeada — o valor padrão "Favoritos" já é aplicado em
            # _criar_favorito quando a pilha estiver vazia.
            nova_pilha: list[str] = pilha_pastas
            if nome_tag == "dl" and ultimo_h3 is not None:
                nova_pilha = pilha_pastas + [ultimo_h3]
                ultimo_h3 = None
            self._processar_no(no=filho, pilha_pastas=nova_pilha, favoritos=favoritos)

    def extrair_favoritos(self, html_conteudo: str) -> list[Favorito]:
        """Varre o HTML recursivamente e instancia entidades de Favorito."""
        soup = BeautifulSoup(markup=html_conteudo, features="html.parser")
        favoritos: list[Favorito] = []
        self._processar_no(no=soup, pilha_pastas=[], favoritos=favoritos)
        return favoritos
