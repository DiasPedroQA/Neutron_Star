# pylint: disable=redefined-outer-name

"""Testes unitários do serviço de processamento de favoritos."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_bookmark import Favorito
from backend.core.entidades.entidade_diretorio import ModeloPasta
from backend.core.entidades.entidade_processamento import ResultadoProcessamento
from backend.core.interfaces.bookmark_exporter import FavoritoExporter
from backend.core.interfaces.bookmark_parser import FavoritoParser
from backend.core.interfaces.bookmark_repository import FavoritoRepository
from backend.core.interfaces.file_scanner import FileScanner
from backend.core.services import FavoritoProcessingService


class TestFavoritoProcessingService:
    """Testes unitários para o FavoritoProcessingService.

    Valida a orquestração entre vassoura, analisador, exportador e repositório,
    garantindo que a lógica de negócio se comporte conforme esperado.
    """

    # ------------------------------------------------------------------
    # Dummies (implementações mínimas das interfaces)
    # ------------------------------------------------------------------

    class DummyScanner(FileScanner):
        """Mock de FileScanner para os testes de serviço."""

        def __init__(self) -> None:
            self.pasta_varrida: ModeloPasta | None = None

        def varrer_diretorio(self, pasta_raiz: ModeloPasta) -> None:
            """Armazena a pasta raiz varrida."""
            self.pasta_varrida = pasta_raiz

        def localizar_arquivos_html(self, pasta: ModeloPasta) -> list[ModeloArquivo]:
            """Retorna um arquivo HTML dummy."""
            return [
                ModeloArquivo(
                    nome_arquivo="favoritos.html",
                    caminho_arquivo=pasta.caminho_absoluto / "favoritos.html",
                    tamanho_arquivo_bytes=0,
                    eh_html=True,
                )
            ]

    class DummyParser(FavoritoParser):
        """Mock de FavoritoParser que sempre retorna um favorito."""

        def suporta_arquivo(self, arquivo: ModeloArquivo) -> bool:
            return True

        def analisar_arquivo(self, arquivo: ModeloArquivo) -> list[Favorito]:
            return [
                Favorito(
                    titulo="Example",
                    url="https://example.com",
                    data_adicao=datetime(
                        year=2023, month=1, day=1, tzinfo=timezone.utc
                    ),
                )
            ]

    class DummyParserWithoutResults(FavoritoParser):
        """Mock de FavoritoParser que nunca encontra favoritos."""

        def suporta_arquivo(self, arquivo: ModeloArquivo) -> bool:
            return True

        def analisar_arquivo(self, arquivo: ModeloArquivo) -> list[Favorito]:
            return []

    class DummyParserUnsupported(FavoritoParser):
        """Mock de FavoritoParser que não suporta nenhum arquivo."""

        def suporta_arquivo(self, arquivo: ModeloArquivo) -> bool:
            return False

        def analisar_arquivo(self, arquivo: ModeloArquivo) -> list[Favorito]:
            return []

    class DummyExporter(FavoritoExporter):
        """Mock de FavoritoExporter que escreve 'ok' no arquivo."""

        def obter_formatos_suportados(self) -> str:
            return "json"

        def exportar(self, lista_favoritos: list[Favorito], saida: Path) -> None:
            saida.write_text(data="ok", encoding="utf-8")

    class DummyRepository(FavoritoRepository):
        """Mock de FavoritoRepository que memoriza a última chamada."""

        def __init__(self) -> None:
            self.favoritos_salvos: tuple[list[Favorito], str] | None = None

        def salvar(self, favoritos: list[Favorito], identificador: str) -> None:
            self.favoritos_salvos = (favoritos, identificador)

        def carregar(self, identificador: str) -> list[Favorito]:
            return []

    # ------------------------------------------------------------------
    # Método auxiliar
    # ------------------------------------------------------------------

    def _processar_e_validar_estatisticas(
        self,
        servico: FavoritoProcessingService,
        raiz: Path,
        processados_esperados: int,
        falhas_esperadas: int,
    ) -> ResultadoProcessamento:
        """Executa processar_diretorio e confere as estatísticas.

        Args:
            servico: Serviço configurado com os dummies desejados.
            raiz: Diretório raiz para o processamento.
            processados_esperados: Quantidade esperada de arquivos processados.
            falhas_esperadas: Quantidade esperada de falhas.

        Returns:
            O objeto ResultadoProcessamento obtido.
        """
        resultado: ResultadoProcessamento = servico.processar_diretorio(
            caminho_raiz=raiz
        )
        assert resultado.estatisticas_processadas.total_arquivos == 1
        assert (
            resultado.estatisticas_processadas.arquivos_processados
            == processados_esperados
        )
        assert resultado.estatisticas_processadas.arquivos_com_falha == falhas_esperadas
        assert (
            resultado.estatisticas_processadas.total_favoritos == processados_esperados
        )
        return resultado

    # ------------------------------------------------------------------
    # Testes
    # ------------------------------------------------------------------

    def test_processar_diretorio_collects_favoritos_and_stats(
        self, tmp_path: Path
    ) -> None:
        """Verifica se o serviço processa o diretório e coleta estatísticas."""
        pasta_raiz: Path = tmp_path / "home"
        pasta_raiz.mkdir()
        servico_extracao: FavoritoProcessingService = FavoritoProcessingService(
            vassoura=self.DummyScanner(),
            analisador=self.DummyParser(),
            exportador=None,
            repositorio=None,
        )
        resultado: ResultadoProcessamento = self._processar_e_validar_estatisticas(
            servico=servico_extracao,
            raiz=pasta_raiz,
            processados_esperados=1,
            falhas_esperadas=0,
        )
        assert resultado.caminho_raiz == str(pasta_raiz)

    def test_processar_diretorio_skips_files_with_no_favoritos(
        self, tmp_path: Path
    ) -> None:
        """Registra falha quando o analisador não extrai nenhum favorito."""
        pasta_raiz: Path = tmp_path / "home"
        pasta_raiz.mkdir()
        servico_extracao: FavoritoProcessingService = FavoritoProcessingService(
            vassoura=self.DummyScanner(),
            analisador=self.DummyParserWithoutResults(),
            exportador=None,
            repositorio=None,
        )
        self._processar_e_validar_estatisticas(
            servico=servico_extracao,
            raiz=pasta_raiz,
            processados_esperados=0,
            falhas_esperadas=1,
        )

    def test_processar_diretorio_skips_unsupported_files(self, tmp_path: Path) -> None:
        """Ignora arquivos para os quais o analisador não oferece suporte."""
        pasta_raiz: Path = tmp_path / "home"
        pasta_raiz.mkdir()
        servico_extracao: FavoritoProcessingService = FavoritoProcessingService(
            vassoura=self.DummyScanner(),
            analisador=self.DummyParserUnsupported(),
            exportador=None,
            repositorio=None,
        )
        self._processar_e_validar_estatisticas(
            servico=servico_extracao,
            raiz=pasta_raiz,
            processados_esperados=0,
            falhas_esperadas=1,
        )

    def test_salvar_no_repositorio_ignores_missing_repository(self) -> None:
        """Chamar salvar_no_repositorio sem repositório configurado não causa erro."""
        servico_extracao: FavoritoProcessingService = FavoritoProcessingService(
            vassoura=self.DummyScanner(),
            analisador=self.DummyParser(),
        )
        favoritos: list[Favorito] = [
            Favorito(
                titulo="Example",
                url="https://example.com",
                data_adicao=datetime(2023, 1, 1, tzinfo=timezone.utc),
            )
        ]
        servico_extracao.salvar_no_repositorio(favoritos=favoritos, id_sessao="test-id")

    def test_export_favoritos_adds_suffix_and_uses_exporter(
        self, tmp_path: Path
    ) -> None:
        """A exportação adiciona a extensão correta e grava o arquivo."""
        exportador_fake = self.DummyExporter()
        servico_extracao: FavoritoProcessingService = FavoritoProcessingService(
            vassoura=self.DummyScanner(),
            analisador=self.DummyParser(),
            exportador=exportador_fake,
        )
        favoritos: list[Favorito] = [
            Favorito(
                titulo="Example",
                url="https://example.com",
                data_adicao=datetime(year=2023, month=1, day=1, tzinfo=timezone.utc),
            )
        ]
        saida: Path = tmp_path / "out"
        servico_extracao.exportar_favoritos(
            links_favoritos=favoritos, caminho_saida=saida, formato_saida="json"
        )
        assert saida.with_suffix(suffix=".json").exists()

    def test_export_favoritos_raises_without_exporter(self) -> None:
        """Exportar sem exportador configurado deve levantar ValueError."""
        servico_extracao: FavoritoProcessingService = FavoritoProcessingService(
            vassoura=self.DummyScanner(),
            analisador=self.DummyParser(),
        )
        with pytest.raises(ValueError, match="Nenhum exportador"):
            servico_extracao.exportar_favoritos(
                links_favoritos=[], caminho_saida=Path("out.json"), formato_saida="json"
            )

    def test_export_favoritos_raises_invalid_format(self, tmp_path: Path) -> None:
        """Formatos não suportados pelo exportador devem gerar ValueError."""
        exportador_fake = self.DummyExporter()
        servico_extracao: FavoritoProcessingService = FavoritoProcessingService(
            vassoura=self.DummyScanner(),
            analisador=self.DummyParser(),
            exportador=exportador_fake,
        )
        with pytest.raises(ValueError, match="não suportado"):
            servico_extracao.exportar_favoritos(
                links_favoritos=[],
                caminho_saida=tmp_path / "out.txt",
                formato_saida="csv",
            )

    def test_salvar_no_repositorio_calls_repo(self) -> None:
        """O serviço delega a persistência ao repositório injetado."""
        repositorio = self.DummyRepository()
        servico: FavoritoProcessingService = FavoritoProcessingService(
            vassoura=self.DummyScanner(),
            analisador=self.DummyParser(),
            repositorio=repositorio,
        )
        favoritos: list[Favorito] = [
            Favorito(
                titulo="Example",
                url="https://example.com",
                data_adicao=datetime(2023, 1, 1, tzinfo=timezone.utc),
            )
        ]
        servico.salvar_no_repositorio(favoritos=favoritos, id_sessao="test-id")
        assert repositorio.favoritos_salvos is not None
        assert repositorio.favoritos_salvos[1] == "test-id"
