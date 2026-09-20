# Atoms/tests/adaptadores/test_api.py

"""Testes de integração para o Blueprint Flask de API (src/adaptadores/api.py)."""

import json
import unittest
from collections.abc import Generator
from typing import Any, cast
from unittest.mock import MagicMock

from flask import Flask
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from infra.conteiner import conteiner
from main import criar_aplicacao
from src.dominio.excecoes import DiretorioInexistenteError, PathInseguroError


class TestApiSistema(unittest.TestCase):
    """Suíte para a rota GET /api/sistema."""

    def setUp(self) -> None:
        """Cria o app de teste e substitui o caso de uso real por um mock."""
        self.app: Flask = criar_aplicacao()
        self.app.config["TESTING"] = True
        self.client: FlaskClient = self.app.test_client()
        self._original_use_case = conteiner.obter_info_sistema_use_case
        self.mock_info = MagicMock()
        conteiner.obter_info_sistema_use_case = self.mock_info

    def tearDown(self) -> None:
        """Restaura o caso de uso original no conteiner global (evita vazar mock entre testes)."""
        conteiner.obter_info_sistema_use_case = self._original_use_case

    @staticmethod
    def _dados(resposta: TestResponse) -> dict[str, Any]:
        """Converte o corpo JSON da resposta para dicionário."""
        return cast(dict[str, Any], json.loads(resposta.data))

    def test_obter_sistema_sucesso_retorna_200_e_modo_arquitetura(self) -> None:
        """Garante 200 e a injeção do campo 'modo_arquitetura' na resposta."""
        self.mock_info.executar.return_value = {
            "so": "Linux",
            "usuario": "diaspedro",
            "pasta_home": "/home/diaspedro",
            "atalhos_sugeridos": [],
        }

        resposta: TestResponse = self.client.get("/api/sistema")
        dados: dict[str, Any] = self._dados(resposta)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(dados["so"], "Linux")
        self.assertEqual(dados["modo_arquitetura"], "Hexagonal (Portas e Adaptadores)")

    def test_obter_sistema_erro_inesperado_retorna_500(self) -> None:
        """Garante 500 e chave 'erro' quando o caso de uso lança exceção genérica."""
        self.mock_info.executar.side_effect = RuntimeError("falha simulada")

        resposta: TestResponse = self.client.get("/api/sistema")
        dados: dict[str, Any] = self._dados(resposta)

        self.assertEqual(resposta.status_code, 500)
        self.assertIn("erro", dados)


class TestApiEscanear(unittest.TestCase):
    """Suíte para a rota GET /api/escanear."""

    def setUp(self) -> None:
        """Cria o app de teste e substitui o caso de uso real por um mock."""
        self.app: Flask = criar_aplicacao()
        self.app.config["TESTING"] = True
        self.client: FlaskClient = self.app.test_client()
        self._original_use_case = conteiner.escanear_diretorio_use_case
        self.mock_escanear = MagicMock()
        conteiner.escanear_diretorio_use_case = self.mock_escanear

    def tearDown(self) -> None:
        """Restaura o caso de uso original no conteiner global (evita vazar mock entre testes)."""
        conteiner.escanear_diretorio_use_case = self._original_use_case

    @staticmethod
    def _dados(resposta: TestResponse) -> dict[str, Any]:
        """Converte o corpo JSON da resposta para dicionário."""
        return cast(dict[str, Any], json.loads(resposta.data))

    def test_escanear_sem_query_param_usa_home_como_padrao(self) -> None:
        """Garante que, sem '?caminho=', o padrão '~/' seja repassado ao caso de uso."""
        self.mock_escanear.executar.return_value = {"total_arquivos": 0}

        self.client.get("/api/escanear")

        self.mock_escanear.executar.assert_called_once_with(caminho_str="~/")

    def test_escanear_sucesso_retorna_200(self) -> None:
        """Garante 200 com o payload de varredura repassado pelo caso de uso."""
        self.mock_escanear.executar.return_value = {
            "caminho_varrido": "/home/diaspedro/Documentos",
            "total_arquivos": 1,
            "tamanho_total_mb": 0.05,
            "arquivos": [],
        }

        resposta: TestResponse = self.client.get("/api/escanear?caminho=~/Documentos")
        dados: dict[str, Any] = self._dados(resposta)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(dados["total_arquivos"], 1)
        self.mock_escanear.executar.assert_called_once_with(caminho_str="~/Documentos")

    def test_escanear_path_traversal_retorna_403(self) -> None:
        """Garante 403 quando o caso de uso levanta PathInseguroError."""
        self.mock_escanear.executar.side_effect = PathInseguroError(caminho="../../etc")

        resposta: TestResponse = self.client.get("/api/escanear?caminho=../../etc")
        dados: dict[str, Any] = self._dados(resposta)

        self.assertEqual(resposta.status_code, 403)
        self.assertIn("Acesso Proibido", dados["erro"])

    def test_escanear_diretorio_inexistente_retorna_404(self) -> None:
        """Garante 404 quando o caso de uso levanta DiretorioInexistenteError."""
        self.mock_escanear.executar.side_effect = DiretorioInexistenteError(caminho="~/Inexistente")

        resposta: TestResponse = self.client.get("/api/escanear?caminho=~/Inexistente")
        dados: dict[str, Any] = self._dados(resposta)

        self.assertEqual(resposta.status_code, 404)
        self.assertIn("não existe no disco local", dados["erro"])

    def test_escanear_erro_inesperado_retorna_500(self) -> None:
        """Garante 500 e chave 'erro' quando o caso de uso lança exceção genérica."""
        self.mock_escanear.executar.side_effect = RuntimeError("falha simulada")

        resposta: TestResponse = self.client.get("/api/escanear?caminho=~/Documentos")
        dados: dict[str, Any] = self._dados(resposta)

        self.assertEqual(resposta.status_code, 500)
        self.assertIn("erro", dados)


class TestApiProcessar(unittest.TestCase):
    """Suíte para a rota POST /api/processar (streaming SSE)."""

    def setUp(self) -> None:
        """Cria o app de teste e substitui o caso de uso real por um mock."""
        self.app: Flask = criar_aplicacao()
        self.app.config["TESTING"] = True
        self.client: FlaskClient = self.app.test_client()
        self._original_use_case = conteiner.converter_favoritos_use_case
        self.mock_converter = MagicMock()
        conteiner.converter_favoritos_use_case = self.mock_converter

    def tearDown(self) -> None:
        """Restaura o caso de uso original no conteiner global (evita vazar mock entre testes)."""
        conteiner.converter_favoritos_use_case = self._original_use_case

    @staticmethod
    def _dados(resposta: TestResponse) -> dict[str, Any]:
        """Converte o corpo JSON da resposta para dicionário."""
        return cast(dict[str, Any], json.loads(resposta.data))

    def test_processar_payload_invalido_retorna_400(self) -> None:
        """Garante 400 quando o schema de entrada reprova o payload."""
        payload_ruim: dict[str, list | str] = {
            "arquivos_selecionados": [],
            "extensao_destino": "xml",
        }

        resposta: TestResponse = self.client.post(
            "/api/processar",
            data=json.dumps(payload_ruim),
            content_type="application/json",
        )
        dados: dict[str, Any] = self._dados(resposta)

        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", dados)
        self.mock_converter.executar_com_progresso.assert_not_called()

    def test_processar_sucesso_transmite_eventos_sse(self) -> None:
        """Garante 200, mimetype SSE e repasse por keyword ao caso de uso."""
        payload: dict[str, list[str] | str] = {
            "arquivos_selecionados": ["/home/diaspedro/favoritos.html"],
            "extensao_destino": "json",
        }

        def simular_generator(
            *_args: Any, **_kwargs: Any
        ) -> Generator[dict[str, int | str | bool], Any, None]:
            yield {"progresso": 50, "arquivo_atual": "fav.html", "concluido": False}
            yield {"progresso": 100, "arquivo_atual": "fav.html", "concluido": True}

        self.mock_converter.executar_com_progresso.side_effect = simular_generator

        resposta: TestResponse = self.client.post(
            "/api/processar",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.mimetype, "text/event-stream")

        blocos: list[str] = [
            linha.replace("data: ", "").strip()
            for linha in resposta.data.decode("utf-8").split("\n\n")
            if linha.strip()
        ]
        self.assertEqual(len(blocos), 2)
        self.assertEqual(json.loads(blocos[0])["progresso"], 50)
        self.assertEqual(json.loads(blocos[1])["progresso"], 100)

        self.mock_converter.executar_com_progresso.assert_called_once_with(
            arquivos_selecionados=["/home/diaspedro/favoritos.html"],
            extensao_destino="json",
        )

    def test_processar_erro_no_stream_gera_evento_de_erro_sse(self) -> None:
        """Garante que uma exceção durante o streaming vire um evento SSE de erro."""
        payload: dict[str, list[str] | str] = {
            "arquivos_selecionados": ["/home/diaspedro/favoritos.html"],
            "extensao_destino": "json",
        }
        self.mock_converter.executar_com_progresso.side_effect = RuntimeError(
            "falha crítica simulada"
        )

        resposta: TestResponse = self.client.post(
            "/api/processar",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(resposta.status_code, 200)
        corpo: str = resposta.data.decode("utf-8")
        bloco: str = corpo.replace("data: ", "").strip()
        evento_erro: dict[str, str] = json.loads(bloco)

        self.assertIn("Erro crítico no pipeline", evento_erro["erro"])
        self.assertIn("falha crítica simulada", evento_erro["erro"])


if __name__ == "__main__":
    unittest.main()
