"""Testes das rotas GET da API e das respostas HTTP de erro."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from src.models.excecoes import DiretorioInexistenteError, PathInseguroError


def _resultado_sistema() -> dict[str, Any]:
    """Fornece uma resposta mínima válida para a rota de informações do sistema."""
    return {
        "so": "Linux (6.1)",
        "usuario": "ana",
        "pasta_home": "/home/ana",
        "atalhos_sugeridos": [],
    }


def _resultado_escanear() -> dict[str, Any]:
    """Fornece um resumo mínimo válido para a rota de escaneamento."""
    return {
        "caminho_varrido": "/home/ana",
        "extensao_usada": ".html",
        "profundidade_usada": 5,
        "total_arquivos": 0,
        "total_elegiveis": 0,
        "tamanho_total_mb": 0.0,
        "data_busca": "01/01/2026 00:00:00",
        "arquivos": [],
        "tree": [],
    }


class TestRotasWeb:
    """Respostas das rotas públicas de sistema, escaneamento e interface web."""

    def test_index_renderiza_a_interface(self, client: FlaskClient) -> None:
        """Entrega a página HTML principal com sucesso."""
        resposta = client.get("/")

        assert resposta.status_code == 200
        assert resposta.mimetype == "text/html"

    def test_obter_info_sistema_retorna_json(
        self, client: FlaskClient, mock_servico: MagicMock
    ) -> None:
        """Serializa no JSON os dados devolvidos pelo serviço de domínio."""
        esperado: dict[str, Any] = _resultado_sistema()
        mock_servico.obter_info_sistema.return_value = esperado

        resposta = client.get("/api/sistema")

        assert resposta.status_code == 200
        assert resposta.get_json() == esperado

    def test_obter_info_sistema_retorna_500_se_servico_falhar(
        self, client: FlaskClient, mock_servico: MagicMock
    ) -> None:
        """Converte falha inesperada em resposta genérica sem expor detalhes."""
        mock_servico.obter_info_sistema.side_effect = RuntimeError("falha interna")

        resposta = client.get("/api/sistema")

        assert resposta.status_code == 500
        assert resposta.get_json() == {"erro": "Falha ao obter informações do sistema."}

    def test_escanear_passa_filtros_e_usa_profundidade_padrao_se_invalida(
        self, client: FlaskClient, mock_servico: MagicMock
    ) -> None:
        """Repassa os filtros e substitui profundidade não numérica pelo padrão 5."""
        esperado: dict[str, Any] = _resultado_escanear()
        mock_servico.escanear.return_value = esperado

        resposta = client.get(
            "/api/escanear?caminho=%2Fhome%2Fana&extensao=.htm&profundidade=profunda"
        )

        assert resposta.status_code == 200
        assert resposta.get_json() == esperado
        mock_servico.escanear.assert_called_once_with(
            caminho_str="/home/ana",
            extensao=".htm",
            profundidade=5,
        )

    def test_escanear_usa_parametros_padrao(
        self, client: FlaskClient, mock_servico: MagicMock
    ) -> None:
        """Aplica os valores documentados quando a query string não informa filtros."""
        mock_servico.escanear.return_value = _resultado_escanear()

        resposta = client.get("/api/escanear")

        assert resposta.status_code == 200
        mock_servico.escanear.assert_called_once_with(
            caminho_str="~/",
            extensao=".html",
            profundidade=5,
        )

    @pytest.mark.parametrize(
        ("erro", "status"),
        [
            pytest.param(PathInseguroError("/etc"), 403, id="caminho-proibido"),
            pytest.param(DiretorioInexistenteError("/ausente"), 404, id="pasta-ausente"),
            pytest.param(RuntimeError("falha"), 500, id="falha-inesperada"),
        ],
    )
    def test_escanear_mapeia_erros_para_status_http(
        self,
        client: FlaskClient,
        mock_servico: MagicMock,
        erro: Exception,
        status: int,
    ) -> None:
        """Mapeia erros de domínio e erros inesperados aos status HTTP esperados."""
        mock_servico.escanear.side_effect = erro

        resposta = client.get("/api/escanear?caminho=%2Fhome%2Fana")

        assert resposta.status_code == status
        assert "erro" in resposta.get_json()
