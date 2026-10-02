# Atoms/src/utils/parser.py
# pylint: disable=too-few-public-methods

"""Módulo de extração de tags de favoritos Netscape usando BeautifulSoup."""

from datetime import UTC, datetime

from bs4 import BeautifulSoup
from bs4.element import Tag


class ParserBeautifulSoup:
    """Extrai e processa favoritos estruturados a partir de HTML Netscape."""

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

    @classmethod
    def _criar_favorito(cls, link: Tag, pilha_pastas: list[str]) -> dict[str, str] | None:
        """Cria um favorito a partir de um link válido."""
        caminho_pasta: str = " / ".join(pilha_pastas) if pilha_pastas else "Favoritos"
        url: str = cls._coerce_atributo(valor=link.get("href", ""))
        add_date: str = cls._coerce_atributo(valor=link.get("add_date", ""))
        try:
            return {
                "titulo": link.get_text().strip(),
                "url": url,
                "pasta": caminho_pasta,
                "data_adicao": cls._converter_timestamp(timestamp_str=add_date),
            }
        except ValueError:
            return None

    def _processar_no(
        self, no: Tag, pilha_pastas: list[str], favoritos: list[dict[str, str]]
    ) -> None:
        """Processa um nó e seus descendentes recursivamente."""
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
                favorito: dict[str, str] | None = self._criar_favorito(
                    link=filho, pilha_pastas=pilha_pastas
                )
                if favorito is not None:
                    favoritos.append(favorito)

            nova_pilha: list[str] = pilha_pastas
            if nome_tag == "dl" and ultimo_h3 is not None:
                nova_pilha = pilha_pastas + [ultimo_h3]
                ultimo_h3 = None
            self._processar_no(no=filho, pilha_pastas=nova_pilha, favoritos=favoritos)

    def extrair_favoritos(self, html_conteudo: str) -> list[dict[str, str]]:
        """Varre o HTML recursivamente e retorna instâncias de Favorito."""
        soup = BeautifulSoup(markup=html_conteudo, features="html.parser")
        favoritos: list[dict[str, str]] = []
        self._processar_no(no=soup, pilha_pastas=[], favoritos=favoritos)
        return favoritos
