# pylint: disable=protected-access,redefined-outer-name

"""Testes do serviço de domínio que coordena varredura e conversão."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.models.buscador import BuscadorLocal, GerenciadorSistemaLocal
from src.models.conversor import ConversorService
from src.models.entidades import InfoSistema
from src.models.escritores import EscritorLocal
from src.models.excecoes import DiretorioInexistenteError, ExtensaoInvalidaError, PathInseguroError
from src.utils.leitor import LeitorLocal
from src.utils.parser import ParserBeautifulSoup


@pytest.fixture
def home_isolada(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Cria e configura uma Home temporária para os testes de segurança de caminho."""
    home: Path = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: home)
    return home


@pytest.fixture
def conversor_service() -> ConversorService:
    """Fornece uma instância isolada do serviço de conversão."""
    return ConversorService()


class TestConversorService:
    """Comportamentos públicos do serviço de conversão."""

    def test_construtor_configura_colaboradores(self) -> None:
        """Monta as dependências concretas usadas pelo fluxo de aplicação."""
        servico = ConversorService()

        assert isinstance(servico.gerenciador, GerenciadorSistemaLocal)
        assert isinstance(servico.buscador, BuscadorLocal)
        assert isinstance(servico.leitor, LeitorLocal)
        assert isinstance(servico.parser, ParserBeautifulSoup)
        assert isinstance(servico.escritor, EscritorLocal)

    def test_validar_seguranca_caminho_aceita_descendente_da_home(self, home_isolada: Path) -> None:
        """Resolve caminhos contidos na Home sem alterar sua localização."""
        caminho: Path = home_isolada / "Documentos" / "favoritos.html"

        assert ConversorService().validar_seguranca_caminho(caminho) == caminho.resolve()

    def test_validar_seguranca_caminho_rejeita_caminho_externo(
        self, home_isolada: Path, conversor_service: ConversorService
    ) -> None:
        """Bloqueia caminhos fora da Home com a exceção de domínio apropriada."""
        caminho_externo: Path = home_isolada.parent / "externo"

        with pytest.raises(PathInseguroError):
            conversor_service.validar_seguranca_caminho(caminho_externo)

    def test_obter_info_sistema_delega_ao_gerenciador(
        self, monkeypatch: pytest.MonkeyPatch, conversor_service: ConversorService
    ) -> None:
        """Retorna as informações produzidas pelo colaborador do sistema."""
        esperado: InfoSistema = {
            "so": "Linux (6.1)",
            "usuario": "ana",
            "pasta_home": "/home/ana",
            "atalhos_sugeridos": [],
        }
        obter_info = MagicMock(return_value=esperado)
        monkeypatch.setattr(
            GerenciadorSistemaLocal,
            "obter_informacoes_so",
            staticmethod(obter_info),
        )

        assert conversor_service.obter_info_sistema() == esperado
        obter_info.assert_called_once_with()

    def test_escanear_valida_a_home_e_delega_a_busca(
        self, home_isolada: Path, html_netscape_exemplo: str
    ) -> None:
        """Varre arquivos elegíveis dentro da Home e retorna o resumo real."""
        (home_isolada / "favoritos.html").write_text(html_netscape_exemplo, encoding="utf-8")

        resultado = ConversorService().escanear(caminho_str=str(home_isolada), profundidade=1)

        assert resultado["total_arquivos"] == 1
        assert resultado["total_elegiveis"] == 1
        assert resultado["arquivos"][0]["nome"] == "favoritos.html"

    def test_escanear_rejeita_caminho_externo(
        self, home_isolada: Path, conversor_service: ConversorService
    ) -> None:
        """Interrompe a varredura antes de acessar uma pasta fora da Home."""
        caminho_externo: str = str(home_isolada.parent / "externo")

        with pytest.raises(PathInseguroError):
            conversor_service.escanear(caminho_str=caminho_externo)

    def test_escanear_rejeita_diretorio_ausente(
        self, home_isolada: Path, conversor_service: ConversorService
    ) -> None:
        """Traduz diretório inexistente para a exceção de domínio prevista."""
        caminho_ausente: str = str(home_isolada / "ausente")

        with pytest.raises(DiretorioInexistenteError):
            conversor_service.escanear(caminho_str=caminho_ausente)

    def test_converter_sem_arquivos_emite_conclusao_vazia(
        self, conversor_service: ConversorService
    ) -> None:
        """Emite um único evento bem-sucedido quando a seleção está vazia."""
        eventos = list(conversor_service.converter_com_progresso([], "json"))

        assert eventos == [
            {
                "progresso": 100,
                "arquivo_atual": "",
                "arquivos_convertidos": [],
                "erros": [],
                "concluido": True,
                "sucesso": True,
            }
        ]

    def test_converter_rejeita_formato_nao_suportado(
        self, conversor_service: ConversorService
    ) -> None:
        """Não inicia o fluxo quando a extensão de destino não é reconhecida."""
        eventos = conversor_service.converter_com_progresso([], "xml")

        with pytest.raises(ExtensaoInvalidaError, match="não suportado"):
            list(eventos)

    def test_converter_emite_progresso_e_salva_resultado(
        self,
        home_isolada: Path,
        html_netscape_exemplo: str,
        conversor_service: ConversorService,
    ) -> None:
        """Converte um HTML real, grava JSON e relata total de links e conclusão."""
        origem: Path = home_isolada / "favoritos.html"
        origem.write_text(html_netscape_exemplo, encoding="utf-8")

        eventos = list(
            conversor_service.converter_com_progresso(
                [str(origem)], "json", str(home_isolada / "saida")
            )
        )

        assert eventos[0]["progresso"] == 0
        assert eventos[0]["arquivo_atual"] == "favoritos.html"
        assert eventos[-1]["progresso"] == 100
        assert eventos[-1]["concluido"] is True
        assert eventos[-1]["sucesso"] is True
        convertido = eventos[-1]["arquivos_convertidos"][0]
        assert convertido["total_links"] == 3
        assert Path(convertido["arquivo_destino"]).is_file()

    def test_converter_relata_falha_de_arquivo_sem_interromper_fluxo(
        self, home_isolada: Path, conversor_service: ConversorService
    ) -> None:
        """Registra falha de leitura no evento final em vez de encerrar o gerador."""
        caminho_ausente: str = str(home_isolada / "ausente.html")

        eventos = list(conversor_service.converter_com_progresso([caminho_ausente], "json"))

        assert eventos[-1]["concluido"] is True
        assert eventos[-1]["sucesso"] is False
        assert eventos[-1]["arquivos_convertidos"] == []
        assert eventos[-1]["erros"][0]["arquivo"].endswith("ausente.html")
