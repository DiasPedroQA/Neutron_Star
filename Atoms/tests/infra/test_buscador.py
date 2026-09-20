# Atoms/tests/test_buscador.py

"""Testes unitários para a varredura de arquivos HTML."""

import tempfile
import unittest
from pathlib import Path

from src.infra.buscador import BuscadorLocal, GerenciadorSistemaLocal


class TestBuscadorLocal(unittest.TestCase):
    """Testa validação, limites e metadados da busca local."""

    def setUp(self) -> None:
        """Prepara um diretório temporário para cada teste."""
        # pylint: disable=consider-using-with
        self.temp_dir: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.raiz = Path(self.temp_dir.name)
        self.buscador = BuscadorLocal()

    def test_validar_pasta_existente(self) -> None:
        """Aceita uma pasta existente."""
        self.assertTrue(self.buscador.validar_pasta(self.raiz))

    def test_validar_pasta_inexistente(self) -> None:
        """Rejeita uma pasta inexistente."""
        caminho = self.raiz / "nao-existe"

        self.assertFalse(self.buscador.validar_pasta(caminho))

    def test_validar_pasta_com_caminho_invalido_retorna_falso(self) -> None:
        """Rejeita, sem lançar exceção, um caminho fisicamente irresolvível."""
        caminho_invalido = Path(self.raiz, "arquivo\x00nulo.html")

        self.assertFalse(self.buscador.validar_pasta(caminho_invalido))

    def test_escanear_respeita_profundidade_maxima(self) -> None:
        """Não desce em subpastas além da profundidade máxima configurada."""
        buscador = BuscadorLocal(max_profundidade=1)
        pasta_profunda = self.raiz / "nivel1" / "nivel2"
        pasta_profunda.mkdir(parents=True)
        (self.raiz / "raso.html").write_text("html", encoding="utf-8")
        (pasta_profunda / "profundo.html").write_text("html", encoding="utf-8")

        resultado = buscador.escanear(self.raiz)

        nomes = {item["nome"] for item in resultado["arquivos"]}
        self.assertEqual(nomes, {"raso.html"})

    def test_escanear_encontra_html_e_htm(self) -> None:
        """Encontra arquivos com extensões HTML válidas."""
        (self.raiz / "favoritos.html").write_text("html", encoding="utf-8")
        (self.raiz / "outro.HTM").write_text("html", encoding="utf-8")
        resultado = self._preparar_e_escanear("ignorado.txt", "texto", 2)
        nomes = {item["nome"] for item in resultado["arquivos"]}
        self.assertEqual(nomes, {"favoritos.html", "outro.HTM"})

    def test_escanear_ignora_arquivos_ocultos(self) -> None:
        """Ignora arquivos HTML ocultos."""
        (self.raiz / ".oculto.html").write_text("html", encoding="utf-8")
        resultado = self._preparar_e_escanear("visivel.html", "html", 1)
        self.assertEqual(resultado["arquivos"][0]["nome"], "visivel.html")

    def test_escanear_ignora_diretorios_protegidos(self) -> None:
        """Ignora diretórios protegidos durante a varredura."""
        pasta_ignorada = self.raiz / ".git"
        pasta_ignorada.mkdir()
        (pasta_ignorada / "interno.html").write_text(
            "html",
            encoding="utf-8",
        )

        resultado = self._preparar_e_escanear("normal.html", "html", 1)
        self.assertEqual(resultado["arquivos"][0]["nome"], "normal.html")

    def _preparar_e_escanear(
        self,
        nome_arquivo: str,
        conteudo: str,
        total_esperado: int,
    ) -> dict:
        (self.raiz / nome_arquivo).write_text(
            conteudo,
            encoding="utf-8",
        )
        result = self.buscador.escanear(self.raiz)
        self.assertEqual(
            result["total_arquivos"],
            total_esperado,
        )
        return result

    def test_escanear_respeita_maximo_de_arquivos(self) -> None:
        """Limita a quantidade de arquivos retornados."""
        buscador = BuscadorLocal(max_arquivos=1)

        (self.raiz / "um.html").write_text("html", encoding="utf-8")
        (self.raiz / "dois.html").write_text("html", encoding="utf-8")

        resultado = buscador.escanear(self.raiz)

        self.assertLessEqual(resultado["total_arquivos"], 1)

    def test_escanear_pasta_inexistente_lanca_erro(self) -> None:
        """Lança erro quando a pasta informada não existe."""
        caminho = self.raiz / "inexistente"

        with self.assertRaises(FileNotFoundError):
            self.buscador.escanear(caminho)

    def test_metadados_de_arquivo_indisponivel_retorna_none(self) -> None:
        """Retorna None quando não há metadados disponíveis."""
        # pylint: disable=protected-access
        resultado = BuscadorLocal._obter_metadados(self.raiz / "arquivo-inexistente.html")

        self.assertIsNone(resultado)

    def test_metadados_contem_tamanho_e_nome(self) -> None:
        """Retorna nome, tamanho e seleção nos metadados."""
        arquivo: Path = self.raiz / "favoritos.html"
        arquivo.write_text("1234", encoding="utf-8")

        # pylint: disable=protected-access
        resultado = BuscadorLocal._obter_metadados(arquivo)

        self.assertIsNotNone(resultado)
        if resultado is None:
            self.fail("Os metadados deveriam estar disponíveis")
        metadados, tamanho = resultado

        self.assertEqual(metadados["nome"], "favoritos.html")
        self.assertEqual(tamanho, 4)
        self.assertEqual(metadados["tamanho_kb"], 0.0)
        self.assertTrue(metadados["selecionado"])


class TestGerenciadorSistemaLocal(unittest.TestCase):
    """Testa a coleta de metadados e atalhos do sistema operacional."""

    def test_obter_informacoes_so_contem_campos_essenciais(self) -> None:
        """Retorna S.O., usuário, pasta home e ao menos os atalhos fixos."""
        gerenciador = GerenciadorSistemaLocal()

        dados = gerenciador.obter_informacoes_so()

        self.assertIn("so", dados)
        self.assertIn("usuario", dados)
        self.assertEqual(dados["pasta_home"], str(Path.home()))
        atalhos = dados["atalhos_sugeridos"]
        rotulos = {atalho["caminho"] for atalho in atalhos}
        self.assertIn("~/", rotulos)
        self.assertIn("editável", rotulos)
