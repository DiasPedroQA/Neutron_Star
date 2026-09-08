"""Implementação concreta do adaptador de extração de tags usando BeautifulSoup."""

from datetime import UTC, datetime

from bs4 import BeautifulSoup

from ..aplicacao.portas import ParserPort
from ..dominio.entidades import Favorito


class ParserBeautifulSoup(ParserPort):  # pylint: disable=too-few-public-methods
    """Adaptador de infraestrutura para extração e processamento de favoritos HTML."""

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
    def _criar_favorito(link, pilha_pastas: list[str]) -> Favorito | None:
        """Cria um favorito a partir de um link válido."""
        caminho_pasta: str = " / ".join(pilha_pastas) if pilha_pastas else "Favoritos"
        try:
            return Favorito(
                titulo=link.get_text().strip(),
                url=link.get("href", ""),
                pasta=caminho_pasta,
                data_adicao=ParserBeautifulSoup._converter_timestamp(
                    timestamp_str=link.get("add_date", "")
                ),
            )
        except ValueError:
            return None

    def _processar_no(self, no, pilha_pastas: list[str], favoritos: list[Favorito]) -> None:
        """Processa um nó e seus descendentes."""
        if not getattr(no, "contents", None):
            return

        ultimo_h3 = None
        for filho in no.contents:
            nome_tag = getattr(filho, "name", None)
            if not nome_tag:
                continue
            nome_tag = nome_tag.lower()

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
