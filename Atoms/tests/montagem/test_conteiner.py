# Atoms/tests/montagem/test_conteiner.py

"""Testes unitários para o Composition Root (ConteinerDependencias)."""

from src.aplicacao.casos_uso import (
    ConverterFavoritosLoteUseCase,
    EscanearDiretorioUseCase,
    ObterInfoSistemaUseCase,
)
from src.infra.buscador import BuscadorLocal, GerenciadorSistemaLocal
from src.infra.escritores import EscritorLocal
from src.infra.leitor import LeitorHTML
from src.infra.parser import ParserBeautifulSoup
from src.montagem.conteiner import ConteinerDependencias, conteiner


def test_conteiner_singleton_e_instancia_de_conteiner_dependencias() -> None:
    """Garante que a instância global exportada é do tipo esperado."""
    assert isinstance(conteiner, ConteinerDependencias)


def test_conteiner_instancia_os_cinco_adaptadores_concretos_corretos() -> None:
    """Garante que cada atributo de infraestrutura é do adaptador concreto esperado."""
    assert isinstance(conteiner.gerenciador_sistema_infra, GerenciadorSistemaLocal)
    assert isinstance(conteiner.buscador_infra, BuscadorLocal)
    assert isinstance(conteiner.leitor_infra, LeitorHTML)
    assert isinstance(conteiner.parser_infra, ParserBeautifulSoup)
    assert isinstance(conteiner.escritor_infra, EscritorLocal)


def test_conteiner_instancia_os_tres_casos_de_uso_corretos() -> None:
    """Garante que cada atributo de caso de uso é do tipo esperado."""
    assert isinstance(conteiner.obter_info_sistema_use_case, ObterInfoSistemaUseCase)
    assert isinstance(conteiner.escanear_diretorio_use_case, EscanearDiretorioUseCase)
    assert isinstance(conteiner.converter_favoritos_use_case, ConverterFavoritosLoteUseCase)


def test_obter_info_sistema_use_case_recebe_o_gerenciador_infra_correto() -> None:
    """Garante que a injeção de dependência amarrou o adaptador certo, não uma cópia."""
    # pylint: disable=protected-access
    assert conteiner.obter_info_sistema_use_case._gerenciador_sistema is (
        conteiner.gerenciador_sistema_infra
    )


def test_escanear_diretorio_use_case_recebe_o_buscador_infra_correto() -> None:
    """Garante que a injeção de dependência amarrou o adaptador certo, não uma cópia."""
    # pylint: disable=protected-access
    assert conteiner.escanear_diretorio_use_case._buscador is conteiner.buscador_infra


def test_converter_favoritos_use_case_recebe_leitor_parser_e_escritor_corretos() -> None:
    """Garante que as três dependências do pipeline de conversão foram amarradas corretamente."""
    # pylint: disable=protected-access
    caso_uso: ConverterFavoritosLoteUseCase = conteiner.converter_favoritos_use_case
    assert caso_uso._leitor is conteiner.leitor_infra
    assert caso_uso._parser is conteiner.parser_infra
    assert caso_uso._escritor is conteiner.escritor_infra


def test_nova_instancia_do_conteiner_produz_adaptadores_independentes() -> None:
    """Garante que o contêiner não é acidentalmente um estado global compartilhado por classe.

    Cada nova instância de ConteinerDependencias deve montar seu próprio grafo de
    objetos, sem reaproveitar os adaptadores da instância global 'conteiner'.
    """
    outro_conteiner = ConteinerDependencias()

    assert outro_conteiner.buscador_infra is not conteiner.buscador_infra
    assert outro_conteiner.escanear_diretorio_use_case is not conteiner.escanear_diretorio_use_case
