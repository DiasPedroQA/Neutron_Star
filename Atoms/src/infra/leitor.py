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
        # Valida o caminho antes de ler
        caminho_validado: Path = self._validar_caminho(caminho_arquivo=caminho)
        conteudo: str = self.ler_arquivo(caminho_arquivo=caminho_validado)
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
            data_criacao=self._formatar_data_iso(
                timestamp_str=self._extrair_atributo(elemento, nome="add_date")
            ),
            ultima_modificacao=self._formatar_data_iso(
                timestamp_str=self._extrair_atributo(elemento, nome="last_modified")
            ),
            pasta=pasta_atual,
        )

    @staticmethod
    def _extrair_atributo(elemento: Tag, nome: str) -> str | None:
        """Extrai um atributo do elemento e retorna como string ou None."""
        valor: str | AttributeValueList | None = elemento.get(nome)
        return str(valor) if valor is not None else None

    def _validar_caminho(self, caminho_arquivo: Path) -> Path:
        """Valida se o caminho existe e retorna o Path absoluto."""
        caminho_abs: Path = caminho_arquivo.resolve()
        if not caminho_abs.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_abs}")
        return caminho_abs

    def ler_arquivo(self, caminho_arquivo: Path) -> str:
        """Lê o conteúdo do arquivo com tentativa de encoding UTF-8 e fallback Latin-1."""
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(caminho_arquivo, "r", encoding="latin-1") as f:
                return f.read()

    def _extrair_tags_do_soup(self, soup: BeautifulSoup) -> list[TagExtraida]:
        """Percorre a árvore do BeautifulSoup e extrai as tags."""
        tags: list[TagExtraida] = []
        pasta_atual: str | None = None

        for elemento in soup.find_all(name=["h3", "a"]):
            if elemento.name == "h3":
                pasta_atual = self._extrair_nome_pasta(elemento)
            if (
                elemento.name == "a"
                and self._is_bookmark_link(elemento)
                and (tag := self.criar_tag_extraida(elemento, pasta_atual))
            ):
                tags.append(tag)

        return tags

    @staticmethod
    def _extrair_nome_pasta(elemento: Tag) -> str:
        """Retorna o texto do elemento H3."""
        return elemento.get_text(strip=True)

    @staticmethod
    def _is_bookmark_link(elemento: Tag) -> bool:
        """Verifica se o elemento <a> está dentro de um <dt>."""
        return elemento.parent is not None and elemento.parent.name == "dt"

    def _formatar_data_iso(self, timestamp_str: str | None) -> str | None:
        if not timestamp_str:
            return None
        try:
            timestamp = int(timestamp_str)
            # 13 dígitos = milissegundos
            if timestamp > 1_000_000_000_000:
                timestamp //= 1_000  # milissegundos → segundos
            dt: datetime = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            return dt.isoformat()
        except (ValueError, TypeError, OSError):
            return None
