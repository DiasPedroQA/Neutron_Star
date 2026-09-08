"""Módulo de testes unitários para o adaptador de parser BeautifulSoup."""

import unittest

from src.dominio.entidades import Favorito
from src.infra.parser import ParserBeautifulSoup


class TestParserBeautifulSoup(unittest.TestCase):
    """Suíte de testes para validar a extração de favoritos de arquivos HTML."""

    def setUp(self) -> None:
        """Configura o parser antes de cada caso de teste."""
        self.parser = ParserBeautifulSoup()

    def test_extrair_favoritos_sucesso(self) -> None:
        """Garante que um arquivo de favoritos simples seja extraído corretamente."""
        resultados: list[Favorito] = self._extrair_favoritos(
            html_exemplo="""
        <!DOCTYPE NETSCAPE-Bookmark-file-1>
        <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
        <TITLE>Bookmarks</TITLE>
        <H1>Bookmarks</H1>
        <DL><p>
            <DT><H3 ADD_DATE="1710000000">Pasta Teste</H3>
            <DL><p>
                <DT><A HREF="https://exemplo.com" ADD_DATE="1710000000">Exemplo</A>
            </DL><p>
        </DL><p>
        """,
            quantidade=1,
        )
        favorito: Favorito = resultados[0]
        self.assertIsInstance(favorito, Favorito)
        self.assertEqual(first=favorito.titulo, second="Exemplo")
        self.assertEqual(first=favorito.url, second="https://exemplo.com")
        self.assertEqual(first=favorito.pasta, second="Pasta Teste")

    def test_extrair_favoritos_aninhados(self) -> None:
        """Garante a persistência das subpastas na árvore recursiva de favoritos."""
        resultados: list[Favorito] = self._extrair_favoritos(
            html_exemplo="""
        <!DOCTYPE NETSCAPE-Bookmark-file-1>
        <DL><p>
            <DT><H3>Nível 1</H3>
            <DL><p>
                <DT><H3>Nível 2</H3>
                <DL><p>
                    <DT><A HREF="https://teste.com">Sublink</A>
                </DL><p>
            </DL><p>
        </DL><p>
        """,
            quantidade=1,
        )
        self.assertEqual(
            first=resultados[0].pasta,
            second="Nível 1 / Nível 2",
        )

    def test_ignorar_tags_sem_url(self) -> None:
        """Garante que tags A sem URL (href) ou vazias sejam ignoradas pelo parser."""
        resultados: list[Favorito] = self._extrair_favoritos(
            html_exemplo="""
        <!DOCTYPE NETSCAPE-Bookmark-file-1>
        <DL><p>
            <DT><A>Sem URL</A>
            <DT><A HREF="">URL Vazia</A>
            <DT><A HREF="https://valido.com">Valido</A>
        </DL><p>
        """,
            quantidade=1,
        )
        self.assertEqual(
            first=resultados[0].url,
            second="https://valido.com",
        )

    def test_conversao_timestamp_invalido(self) -> None:
        """Garante tratamento elegante em caso de timestamp com formato incorreto."""
        resultados: list[Favorito] = self._extrair_favoritos(
            html_exemplo="""
        <!DOCTYPE NETSCAPE-Bookmark-file-1>
        <DL><p>
            <DT><A HREF="https://site.com" ADD_DATE="texto_invalido">Site</A>
            <DT><A HREF="https://site2.com" ADD_DATE="">Site 2</A>
        </DL><p>
        """,
            quantidade=2,
        )
        self.assertEqual(first=resultados[0].data_adicao, second="Data inválida")
        self.assertEqual(first=resultados[1].data_adicao, second="Sem data")

    def _extrair_favoritos(self, html_exemplo: str, quantidade: int) -> list[Favorito]:
        result: list[Favorito] = self.parser.extrair_favoritos(html_conteudo=html_exemplo)
        self.assertEqual(first=len(result), second=quantidade)
        return result
