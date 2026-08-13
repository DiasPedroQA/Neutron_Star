"""Leitor de arquivos HTML para extração de tags enriquecidas."""

from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup
from bs4.element import AttributeValueList, Tag

from aplicacao.portas import LeitorArquivo
from dominio.entidades import TagExtraida


class LeitorArquivoHTML(LeitorArquivo):
    """Extrai tags <a> e metadados de um arquivo HTML (formato Netscape)."""

    def extrair_tags(self, caminho: Path) -> list[TagExtraida]:
        """Extrai todas as tags <a> de um arquivo HTML de bookmarks."""
        conteudo: str = self.ler_arquivo(caminho_arquivo=caminho)
        soup = BeautifulSoup(markup=conteudo, features="html.parser")
        return self._extrair_tags_do_soup(soup)

    def criar_tag_extraida(
        self, elemento: Tag, pasta_atual: str | None
    ) -> TagExtraida | None:
        """Cria uma TagExtraida a partir de um elemento <a>."""
        titulo: str = elemento.get_text(strip=True)
        url_raw: str | AttributeValueList | None = elemento.get("href")
        if not titulo or url_raw is None:
            return None

        return TagExtraida(
            titulo=titulo,
            url=str(url_raw),
            data_criacao=self._formatar_data_br(
                timestamp_str=self._extrair_atributo(elemento, "add_date")
            ),
            ultima_modificacao=self._formatar_data_br(
                timestamp_str=self._extrair_atributo(elemento, "last_modified")
            ),
            pasta=pasta_atual,
            tags=self._extrair_atributo(elemento, "tags"),
        )

    @staticmethod
    def _extrair_atributo(elemento: Tag, nome: str) -> str | None:
        """Extrai um atributo do elemento e retorna como string ou None."""
        valor: str | AttributeValueList | None = elemento.get(nome)
        return str(valor) if valor is not None else None

    def _validar_caminho(self, caminho_arquivo: str) -> Path:
        """Valida e retorna o caminho absoluto do arquivo."""
        caminho_abs: Path = Path(caminho_arquivo).resolve()
        if not caminho_abs.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_abs}")
        return caminho_abs

    def ler_arquivo(self, caminho_arquivo: Path) -> str:
        """Lê o conteúdo do arquivo com tentativa de encoding."""
        try:
            with open(file=caminho_arquivo, mode="r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file=caminho_arquivo, mode="r", encoding="latin-1") as f:
                return f.read()

    def _extrair_tags_do_soup(self, soup: BeautifulSoup) -> list[TagExtraida]:
        """Percorre a árvore do BeautifulSoup e extrai as tags."""
        tags: list[TagExtraida] = []
        pasta_atual: str | None = None

        for elemento in soup.find_all(name=["h3", "a"]):
            if elemento.name == "h3":
                pasta_atual = self._extrair_nome_pasta(elemento)
            elif elemento.name == "a" and self._is_bookmark_link(elemento):
                tag: TagExtraida | None = self.criar_tag_extraida(elemento, pasta_atual)
                if tag:
                    tags.append(tag)

        return tags

    def _extrair_nome_pasta(self, elemento: Tag) -> str:
        """Retorna o texto do elemento H3."""
        return elemento.get_text(strip=True)

    def _is_bookmark_link(self, elemento: Tag) -> bool:
        """Verifica se o elemento <a> está dentro de um <dt>."""
        return elemento.parent is not None and elemento.parent.name == "dt"

    def _formatar_data_br(self, timestamp_str: str | None) -> str | None:
        """Converte timestamp (em segundos) para data no formato brasileiro dd/mm/aaaa HH:MM:SS."""
        if not timestamp_str:
            return None
        try:
            timestamp = int(timestamp_str)
            dt: datetime = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            return dt.strftime("%d/%m/%Y %H:%M:%S")
        except (ValueError, TypeError, OSError):
            return None
