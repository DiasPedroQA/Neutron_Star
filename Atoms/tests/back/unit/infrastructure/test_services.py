# Atoms/tests/back/unit/infrastructure/test_services.py

"""Testes para o serviço de processamento FavoritoProcessingService."""

from unittest.mock import MagicMock
from pathlib import Path
import pytest

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_bookmark import Favorito
from backend.core.entidades.entidade_processamento import ResultadoProcessamento
from backend.core.services import FavoritoProcessingService


@pytest.fixture
def mock_scanner() -> MagicMock:
    scanner = MagicMock()
    scanner.localizar_arquivos_html.return_value = [
        ModeloArquivo(
            nome_arquivo="f.html", caminho_arquivo=Path("/abs/f.html"), eh_html=True
        )
    ]
    return scanner


@pytest.fixture
def mock_parser() -> MagicMock:
    parser = MagicMock()
    parser.suporta_arquivo.return_value = True
    parser.analisar_arquivo.return_value = [
        Favorito(titulo="Test", url="http://test.com")
    ]
    return parser


@pytest.fixture
def servico(
    mock_scanner: MagicMock, mock_parser: MagicMock
) -> FavoritoProcessingService:
    return FavoritoProcessingService(vassoura=mock_scanner, analisador=mock_parser)


def test_processar_diretorio_retorna_resultado(
    servico: FavoritoProcessingService, tmp_path: Path
) -> None:
    resultado: ResultadoProcessamento = servico.processar_diretorio(
        caminho_raiz=tmp_path
    )
    assert len(resultado.favoritos_processados) == 1
    assert resultado.favoritos_processados[0].titulo == "Test"
    assert resultado.estatisticas_processadas.total_arquivos == 1


def test_exportar_sem_exportador_levanta_erro(
    servico: FavoritoProcessingService,
) -> None:
    with pytest.raises(
        expected_exception=ValueError, match="Nenhum exportador configurado"
    ):
        servico.exportar_favoritos(
            links_favoritos=[], caminho_saida=Path("/tmp/out.json")
        )


def test_salvar_no_repositorio_sem_repositorio_nao_faz_nada(
    servico: FavoritoProcessingService,
) -> None:
    # não deve levantar exceção
    servico.salvar_no_repositorio(
        favoritos=[Favorito(titulo="x", url="x")], id_sessao="1"
    )


def test_alias_process_directory(
    servico: FavoritoProcessingService, tmp_path: Path
) -> None:
    resultado: ResultadoProcessamento = servico.process_directory(root_path=tmp_path)
    assert resultado.caminho_raiz == str(tmp_path)
