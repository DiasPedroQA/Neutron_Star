# Atoms/src/infra/conteiner.py
# pylint: disable=too-few-public-methods, too-many-instance-attributes

"""Módulo de composição (Composition Root) para Injeção de Dependências."""

from src.aplicacao.casos_uso import (
    ConverterFavoritosLoteUseCase,
    EscanearDiretorioUseCase,
    ObterInfoSistemaUseCase,
)
from src.infra.buscador import BuscadorLocal, GerenciadorSistemaLocal
from src.infra.escritores import EscritorLocal
from src.infra.leitor import LeitorHTML
from src.infra.parser import ParserBeautifulSoup


class ConteinerDependencias:
    """Contêiner de dependências centralizado para a aplicação Neutron Star.

    Instancia os adaptadores concretos de infraestrutura e os injeta nos
    casos de uso da aplicação, atuando como o Composition Root do sistema.
    """

    def __init__(self) -> None:
        """Inicializa e amarra todos os adaptadores físicos e casos de uso."""
        # 1. Instanciação dos adaptadores concretos de infraestrutura (Portas de Saída)
        self.gerenciador_sistema_infra = GerenciadorSistemaLocal()
        self.buscador_infra = BuscadorLocal()
        self.leitor_infra = LeitorHTML()
        self.parser_infra = ParserBeautifulSoup()
        self.escritor_infra = EscritorLocal()

        # 2. Inicialização dos Casos de Uso injetando as dependências corretas
        self.obter_info_sistema_use_case = ObterInfoSistemaUseCase(
            gerenciador_sistema=self.gerenciador_sistema_infra
        )

        self.escanear_diretorio_use_case = EscanearDiretorioUseCase(buscador=self.buscador_infra)

        self.converter_favoritos_use_case = ConverterFavoritosLoteUseCase(
            leitor=self.leitor_infra,
            parser=self.parser_infra,
            escritor=self.escritor_infra,
        )


# Instância global compartilhada do contêiner para ser consumida pelos adaptadores de API
conteiner = ConteinerDependencias()
