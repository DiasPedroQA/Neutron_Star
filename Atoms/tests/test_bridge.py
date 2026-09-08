"""Módulo de testes de integração para as rotas da API (Flask Bridge)."""

import json
import unittest
from typing import Any, cast
from collections.abc import Generator
from unittest.mock import MagicMock

from flask import Flask
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

# Importa a fábrica para criar o app de teste
from main import criar_aplicacao
from src.dominio.excecoes import DiretorioInexistenteError, PathInseguroError
from src.montagem.conteiner import conteiner


class TestAPIBridge(unittest.TestCase):
    """Suíte de testes de integração para validar as rotas Flask e segurança."""

    @staticmethod
    def _dados_resposta(resposta: TestResponse) -> dict[str, Any]:
        """Converte o corpo JSON da resposta para um dicionário."""
        return cast(dict[str, Any], json.loads(resposta.data))

    def setUp(self) -> None:
        """Configura o cliente de testes Flask e limpa mocks."""
        self.app: Flask = criar_aplicacao()
        self.app.config["TESTING"] = True
        self.client: FlaskClient = self.app.test_client()

        # Mocks dos Casos de Uso no container global
        self.mock_info = MagicMock()
        self.mock_escanear = MagicMock()
        self.mock_converter = MagicMock()

        conteiner.obter_info_sistema_use_case = self.mock_info
        conteiner.escanear_diretorio_use_case = self.mock_escanear
        conteiner.converter_favoritos_use_case = self.mock_converter

    def test_obter_sistema_sucesso(self) -> None:
        """Garante que a rota /api/sistema retorne dados com sucesso (200)."""
        self.mock_info.executar.return_value = {
            "so": "Linux",
            "usuario": "diaspedro",
            "pasta_home": "/home/diaspedro",
            "atalhos_sugeridos": [],
        }

        dados: dict[str, Any] = self._obter_dados_get_com_status(
            caminho="/api/sistema", status_esperado=200
        )
        self.assertEqual(first=dados["so"], second="Linux")
        self.assertEqual(first=dados["modo_arquitetura"], second="Hexagonal (Portas e Adaptadores)")

    def test_escanear_pasta_sucesso(self) -> None:
        """Garante que a varredura retorne a estrutura com sucesso."""
        self.mock_escanear.executar.return_value = {
            "caminho_varrido": "/home/diaspedro/Documentos",
            "total_arquivos": 1,
            "tamanho_total_mb": 0.05,
            "arquivos": [],
        }

        dados: dict[str, Any] = self._obter_dados_get_com_status(
            caminho="/api/escanear?caminho=~/Documentos", status_esperado=200
        )
        self.assertEqual(first=dados["total_arquivos"], second=1)

    def test_escanear_pasta_insegura_forbidden(self) -> None:
        """Garante retorno 403 (Forbidden) ao tentar Path Traversal."""
        self.mock_escanear.executar.side_effect = PathInseguroError(caminho="../../etc")

        dados: dict[str, Any] = self._obter_dados_get_com_status(
            caminho="/api/escanear?caminho=../../etc", status_esperado=403
        )
        self.assertIn(member="Acesso Proibido", container=dados["erro"])

    def test_escanear_pasta_inexistente_not_found(self) -> None:
        """Garante retorno 404 ao tentar escanear pasta inexistente."""
        self.mock_escanear.executar.side_effect = DiretorioInexistenteError(caminho="~/Inexistente")

        dados: dict[str, Any] = self._obter_dados_get_com_status(
            caminho="/api/escanear?caminho=~/Inexistente", status_esperado=404
        )
        self.assertIn(member="não existe no disco local", container=dados["erro"])

    def _obter_dados_get_com_status(
        self,
        caminho: str,
        status_esperado: int,
    ) -> dict[str, Any]:
        """Executa uma requisição GET e valida o status da resposta."""
        resposta: TestResponse = self.client.get(caminho)
        result: dict[str, Any] = self._dados_resposta(resposta)
        self.assertEqual(first=resposta.status_code, second=status_esperado)
        return result

    def test_processar_lote_schema_invalido(self) -> None:
        """Garante retorno 400 se o payload estiver malformado."""
        payload_ruim: dict[str, list | str] = {
            "arquivos_selecionados": [],  # Vazio é inválido pelo validador
            "extensao_destino": "xml",  # Formato inválido
        }

        resposta: TestResponse = self.client.post(
            "/api/processar", data=json.dumps(payload_ruim), content_type="application/json"
        )
        dados: dict[str, Any] = self._dados_resposta(resposta)

        self.assertEqual(first=resposta.status_code, second=400)
        self.assertIn(member="erro", container=dados)

    def test_processar_lote_streaming_sse_sucesso(self) -> None:
        """Garante o consumo de progresso no padrão SSE (200)."""
        payload: dict[str, list[str] | str] = {
            "arquivos_selecionados": ["/home/diaspedro/favoritos.html"],
            "extensao_destino": "json",
        }

        # Simula as yieldings do Generator no Caso de Uso de lote
        def simular_generator(
            *_args: Any, **_kwargs: Any
        ) -> Generator[dict[str, int | str | bool], Any, None]:
            yield {"progresso": 50, "arquivo_atual": "fav.html", "concluido": False}
            yield {"progresso": 100, "arquivo_atual": "fav.html", "concluido": True}

        self.mock_converter.executar_com_progresso.side_effect = simular_generator

        resposta: TestResponse = self.client.post(
            "/api/processar", data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(first=resposta.status_code, second=200)
        self.assertEqual(first=resposta.mimetype, second="text/event-stream")

        # Analisa o stream de dados retornado no protocolo SSE
        linhas: list[str] = resposta.data.decode("utf-8").split("\n\n")
        blocos_eventos: list[str] = [
            linha.replace("data: ", "").strip() for linha in linhas if linha.strip()
        ]

        self.assertEqual(first=len(blocos_eventos), second=2)
        evento_1: dict[str, Any] = json.loads(blocos_eventos[0])
        evento_2: dict[str, Any] = json.loads(blocos_eventos[1])

        self.assertEqual(first=evento_1["progresso"], second=50)
        self.assertEqual(first=evento_2["progresso"], second=100)
        self.assertTrue(expr=evento_2["concluido"])
