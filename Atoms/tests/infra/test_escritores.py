"""Módulo de testes unitários para as estratégias de escrita de arquivos."""

import csv
import json
import tempfile
from contextlib import ExitStack
from typing import Any
import unittest
from pathlib import Path

from src.infra.escritores import EscritorLocal


class TestEscritorLocal(unittest.TestCase):
    """Suíte de testes para validar a persistência física em JSON e CSV."""

    def setUp(self) -> None:
        """Configura o escritor e o diretório temporário para os testes."""
        self.escritor = EscritorLocal()
        self._exit_stack = ExitStack()
        self.addCleanup(self._exit_stack.close)
        temp_dir = self._exit_stack.enter_context(tempfile.TemporaryDirectory())
        self.caminho_base: Path = Path(temp_dir) / "favoritos.html"

        # Dados de exemplo típicos serializados pelo domínio/casos de uso
        self.dados_teste: list[dict[str | Any, str | Any]] = [
            {
                "Titulo": "Google",
                "URL": "https://google.com",
                "Pasta": "Favoritos",
                "Data_Adicao": "05/09/2026 18:00:00",
            },
            {
                "Titulo": "GitHub",
                "URL": "https://github.com",
                "Pasta": "Favoritos / Desenvolvimento",
                "Data_Adicao": "05/09/2026 19:00:00",
            },
        ]

    def test_gerar_caminho_destino(self) -> None:
        """Garante que o caminho de destino seja calculado de forma correta."""
        caminho_orig = Path("/home/usuario/bookmarks.html")

        # Caso 1: Extensão limpa e sufixo padrão
        caminho_csv: Path = EscritorLocal.gerar_caminho_destino(
            caminho_original=caminho_orig, extensao="csv"
        )
        self.assertEqual(first=caminho_csv.name, second="bookmarks_processado.csv")

        # Caso 2: Extensão com ponto e sufixo personalizado
        caminho_json: Path = EscritorLocal.gerar_caminho_destino(
            caminho_original=caminho_orig, extensao=".json", sufixo="_custom"
        )
        self.assertEqual(first=caminho_json.name, second="bookmarks_custom.json")

    def test_salvar_lote_json_sucesso(self) -> None:
        """Garante a gravação de favoritos estruturados em formato JSON."""
        caminho_gravado: Path = self._salvar_lote_e_validar_caminho(
            extensao="json", extensao_esperada=".json"
        )
        # Abre o arquivo JSON gravado e valida os dados físicos
        with open(file=caminho_gravado, mode="r", encoding="utf-8") as arq:
            dados_lidos = json.load(arq)

        self._validar_dados_lidos(
            dados=dados_lidos,
            campo="URL",
            primeiro_valor="https://google.com",
            segundo_valor="https://github.com",
        )

    def test_salvar_lote_csv_sucesso(self) -> None:
        """Garante gravação em CSV formatado com BOM e separador ';'."""
        caminho_gravado: Path = self._salvar_lote_e_validar_caminho(
            extensao="csv", extensao_esperada=".csv"
        )
        # Valida codificação utf-8-sig (BOM) e delimitador ';' do Excel BR
        with open(file=caminho_gravado, mode="r", encoding="utf-8-sig", newline="") as arq:
            leitor: csv.DictReader[str] = csv.DictReader(arq, delimiter=";")
            linhas: list[dict[str | Any, str | Any]] = list(leitor)

        self._validar_dados_lidos(
            dados=linhas,
            campo="Pasta",
            primeiro_valor="Favoritos",
            segundo_valor="Favoritos / Desenvolvimento",
        )

    def _salvar_lote_e_validar_caminho(
        self,
        extensao: str,
        extensao_esperada: str,
    ) -> Path:
        caminho_gravado_str: str = self.escritor.salvar_lote(
            caminho_original=self.caminho_base,
            dados=self.dados_teste,
            extensao=extensao,
        )
        result = Path(caminho_gravado_str)
        self.assertTrue(expr=result.exists())
        self.assertEqual(first=result.suffix, second=extensao_esperada)
        return result

    def _validar_dados_lidos(
        self,
        dados: list[dict[str | Any, str | Any]],
        campo: str,
        primeiro_valor: str,
        segundo_valor: str,
    ) -> None:
        self.assertEqual(first=len(dados), second=2)
        self.assertEqual(first=dados[0]["Titulo"], second="Google")
        self.assertEqual(first=dados[0][campo], second=primeiro_valor)
        self.assertEqual(first=dados[1]["Titulo"], second="GitHub")
        self.assertEqual(first=dados[1][campo], second=segundo_valor)

    def test_salvar_lote_dados_vazios_erro(self) -> None:
        """Garante falha ao tentar exportar um lote sem nenhum registro."""
        with self.assertRaises(expected_exception=ValueError) as contexto:
            self.escritor.salvar_lote(caminho_original=self.caminho_base, dados=[], extensao="json")

        self.assertIn(member="Não há dados para exportar", container=str(contexto.exception))

    def test_salvar_lote_formato_nao_suportado(self) -> None:
        """Garante falha ao solicitar salvamento em extensão inválida."""
        with self.assertRaises(expected_exception=ValueError) as contexto:
            self.escritor.salvar_lote(
                caminho_original=self.caminho_base, dados=self.dados_teste, extensao="xml"
            )

        self.assertIn(member="Formato '.xml' não suportado", container=str(contexto.exception))
