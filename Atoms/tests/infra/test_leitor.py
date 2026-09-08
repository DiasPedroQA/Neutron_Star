# Atoms/tests/test_leitor.py

"""Testes unitários para leitura de arquivos HTML."""

import tempfile
import unittest
from pathlib import Path
from shutil import rmtree

from src.infra.leitor import LeitorHTML


class TestLeitorHTML(unittest.TestCase):
    """Testa a leitura com expansão de diretório e diferentes conteúdos."""

    def setUp(self) -> None:
        self.raiz = Path(tempfile.mkdtemp())
        self.addCleanup(rmtree, self.raiz)
        self.leitor = LeitorHTML()

    def criar_arquivo(self, nome: str, conteudo: str, encoding: str = "utf-8") -> Path:
        """Cria um arquivo temporário com o conteúdo informado."""
        arquivo: Path = self.raiz / nome
        arquivo.write_text(data=conteudo, encoding=encoding)
        return arquivo

    def test_le_arquivo_utf8(self) -> None:
        """Lê corretamente um arquivo codificado em UTF-8."""
        self._testar_leitura_arquivo(nome="favoritos.html", conteudo="Olá, favoritos!")

    def test_le_arquivo_vazio(self) -> None:
        """Lê corretamente um arquivo vazio."""
        self._testar_leitura_arquivo(nome="vazio.html", conteudo="")

    def _testar_leitura_arquivo(self, nome: str, conteudo: str) -> None:
        arquivo: Path = self.criar_arquivo(nome=nome, conteudo=conteudo)
        resultado: str = self.leitor.ler_arquivo(caminho=arquivo)
        self.assertEqual(first=resultado, second=conteudo)

    def test_le_arquivo_com_conteudo_latin1(self) -> None:
        """Lê um arquivo com conteúdo codificado em Latin-1."""
        arquivo: Path = self.criar_arquivo(
            nome="latin1.html", conteudo="Favoritos: ação", encoding="latin-1"
        )

        resultado: str = self.leitor.ler_arquivo(caminho=arquivo)

        self.assertIn(member="Favoritos", container=resultado)

    def test_arquivo_inexistente_lanca_erro(self) -> None:
        """Testa que a leitura de um arquivo inexistente lança FileNotFoundError."""
        with self.assertRaises(expected_exception=FileNotFoundError):
            self.leitor.ler_arquivo(caminho=self.raiz / "nao-existe.html")
