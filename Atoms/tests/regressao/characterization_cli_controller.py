"""Testes de caracterização dos comandos da interface CLI."""

from argparse import Namespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from src.controllers.cli_controller import CLIController


@pytest.mark.characterization
def test_executar_comando_sistema_imprime_saida_humanizada(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Caracteriza a saída legível com dados do sistema e atalhos da home."""
    info: dict[str, Any] = {
        "so": "Linux (6.1)",
        "usuario": "ana",
        "pasta_home": "/home/ana",
        "atalhos_sugeridos": [
            {"label": "Documentos", "caminho": "/home/ana/Documentos"},
            {"label": "Downloads", "caminho": "/home/ana/Downloads"},
        ],
    }
    servico: MagicMock = MagicMock()
    servico.obter_info_sistema.return_value = info
    monkeypatch.setattr(target=CLIController, name="servico", value=servico)

    codigo: int = CLIController.executar_comando_sistema(args=Namespace(saida_json=False))

    assert codigo == 0
    assert capsys.readouterr().out == (
        "\n🌌 Informações do Ambiente:\n"
        "  • Sistema Operacional : Linux (6.1)\n"
        "  • Usuário Ativo       : ana\n"
        "  • Diretório Pessoal   : /home/ana\n"
        "\n📂 Atalhos Rápidos Recomendados:\n"
        "  - Documentos -> /home/ana/Documentos\n"
        "  - Downloads -> /home/ana/Downloads\n"
        "\n"
    )
